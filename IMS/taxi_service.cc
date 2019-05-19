/* 
  IMS Simulace taxisluzby
  Vytvoril: Ondrej Deingruber
            Ivan Estvan 

  modelovy cas je v minutach
  jsou modelovany pouze pracovni dny
*/
#include "simlib.h"
#include <stdio.h>      /* printf, NULL */
#include <iostream>
#include <cstdlib>
#include<stdio.h>

#define AVG_TRIP_SPEED 0.2365871355  // in miles per minute
#define DISTANCE_FEE 0.5
#define ENTER_FEE 2.5
#define IMP_SUPERCHARGE 0.3
#define NYC_CHARGE 0.5
#define WAITING_FEE 0.5
#define AVG_TIP 2.548377293

// global objects:
Facility  Taxi("Taxi");
int quitters = 0;
int workdays = 0;
int launchbreaks = 0;
double myTime = Time; // Debug
Queue customersOnStreet("Queue of customers on street");
Queue customersOnPhone("Queue of customers on phone");
Stat TripDistance("Distance of the trip");
Stat TripIncome("Income of the trip");
Histogram HistTripTime("Time of the trip",0,4,30);
Histogram HistTripDistance("Distance of the trip",0,2,20);

void activateNextTransaction();

class Timeout : public Event {
    Process *ptr;               // which process
  public:
    Timeout(double t, Process *p): ptr(p) {
      Activate(Time+t);         // when to time-out the process
    }
    void Behavior() {
      delete ptr;               // kill process
      quitters++;                 // counter of time-out operations
    }
};

class Customer : public Process {
  public:
    Customer(int pri) : Process(pri) {};
    void Behavior() {
      double tripTime = 0.0;
      double tripDistance = 0.0;
      double payingDistance = 0.0;
      double payingWaiting = 0.0;
      double tripIncome = 0.0;

      if (Random()>0.6) {  // Customer called
        isOnPhone = 1;
      }
      myTime =Time;
      interupted = 0;
      
      timeout = new Timeout(Exponential(10), this); // set timeout for customer to wait
      getTaxi:
      if (Taxi.Busy()){
        if (isOnPhone) {
          customersOnPhone.Insert(this);
          myTime = Time;
          Passivate();
          Seize(Taxi);
        }
        else {
          customersOnStreet.Insert(this);
          myTime = Time;
          Passivate();
          Seize(Taxi);
        }
        myTime = Time;
      }
      else {
        myTime = Time;
        Seize(Taxi);
      }
      delete timeout;

      if (isOnPhone) {
        double waitTime = Exponential(7);
        Wait(waitTime);  // Going to customer
        if(interupted) {
          TripDistance(0.0);
          TripIncome(0.0);
          HistTripDistance(0.0);
          HistTripTime(0.0);
          delete this;
          activateNextTransaction();
          return;
        }
        tripDistance += waitTime * AVG_TRIP_SPEED;
        tripTime += waitTime;

        if (rand() > 0.1) { // If have to wait for customer
          myTime = Time;
          double waitTime = Exponential(5);
          Wait(waitTime);  // Wait for the customer
          if(interupted) {
            TripDistance(tripDistance);
            TripIncome(0.0);
            HistTripDistance(tripDistance);
            HistTripTime(tripTime);
            delete this;
            activateNextTransaction();
            return;
          }
          tripTime += waitTime;
          if(Random()<0.02) {  // Zakaznik neprisel
            myTime = Time;
            Release(Taxi);
            delete this;
            activateNextTransaction();
            return;
          }
          payingWaiting += waitTime;
        } 
      }

      double probability = Random(); // Decide what customer do
      while(42) { // till customer wants to another location
        myTime = Time;
        double waitTime = Exponential(11.9833);
        Wait(waitTime);  // Drives customer
        if(interupted) {
          myTime = Time;
          TripDistance(tripDistance);
          TripIncome(0.0);
          HistTripDistance(tripDistance);
          HistTripTime(tripTime);
          delete this;
          activateNextTransaction();
          return;
        }
        tripTime += waitTime;
        tripDistance += waitTime * AVG_TRIP_SPEED;
        payingDistance += waitTime * AVG_TRIP_SPEED;

        if (probability < 0.05) { // wait for customer and drive him somewhere else
          myTime =Time;
          probability = Random();
          waitTime = Exponential(10);
          Wait(waitTime);
          payingWaiting += waitTime;
        }
        else {
          break;
        }
      }
      
      if (Random() < 0.01) { // Problem with customer
        myTime =Time;
        double waitTime = Exponential(32);
        Wait(waitTime);
        if(interupted) {  // interupted
          myTime = Time;
          if (Random()<0.5) { // doesnt pay
            TripDistance(tripDistance);
            TripIncome(0.0);
            HistTripDistance(tripDistance);
            HistTripTime(tripTime);
          }
          delete this;
          activateNextTransaction();
          return;
        }
        if (Random()<0.5) { // doesnt pay
          Release(Taxi);
          TripDistance(tripDistance);
          TripIncome(0.0);
          HistTripDistance(tripDistance);
          HistTripTime(tripTime);
          delete this;
          activateNextTransaction();
          return;
        }
      }

      if (Random() < 0.4795) { // Gives tip
        myTime =Time;
        //Print("Customer: Pays, gives tip: %f\n", myTime);
        tripIncome = ENTER_FEE + (payingDistance * DISTANCE_FEE) + IMP_SUPERCHARGE + NYC_CHARGE + (0.5*WAITING_FEE) + AVG_TIP;
      }
      else {  // Doesnt give tip
        myTime =Time;
        //Print("Customer: Pays, doesnt gives tip: %f\n", myTime);
        tripIncome = ENTER_FEE + (payingDistance * DISTANCE_FEE) + IMP_SUPERCHARGE + NYC_CHARGE + (0.5*WAITING_FEE);
      }
      
      TripDistance(tripDistance);
      TripIncome(tripIncome);
      HistTripDistance(tripDistance);
      HistTripTime(tripTime);


      myTime =Time;
      //Print("Customer: Taxi is released Time: %f\n", myTime);
      Release(Taxi);  // Taxi is ready
      activateNextTransaction();
    }
  int interupted = 0;
      Event *timeout;
  private:
    int isOnPhone = 0;
};

class RepairDefect : public Process { // Car repair process
  public:
    RepairDefect() : Process() {};
    
    void Behavior() {
      Seize(Taxi, 1); // Seize with higger priority
      if (Taxi.Q2 -> Length()>0) {  // customer was in taxi
        Customer *cust = (Customer *)Taxi.Q2 -> GetFirst(); // get that customer
        cust -> interupted = 1; // set him as interupted
        cust -> Activate(); // Let him do action
      }
      Wait(Exponential(20));
      myTime =Time;
      Release(Taxi);
      activateNextTransaction();
    }
};

class Generator : public Event {  // Generates customers
  public:
    Generator(double interv, int pri) : Event() {
        Interval = interv;
        Pri = pri;
    };

    void Behavior() {
      if (!day) { // If not interupted by day
         actTime = Time+Exponential(Interval);
         (new Customer(Pri))->Activate();
      }
      day = 0;
      Activate(actTime);
    }
    int day = 0;
    double actTime = 0;

    double Interval;
    int Pri;
};

class	Defect : public Event { // Generates car defects
  public:
    Defect() : Event() {};
    
    void Behavior() {
      if (!day) { // if not interupted
         actTime = Time+Exponential(105120);  // calculate new defect time
         (new RepairDefect())->Activate();  // Repair defect
      }
      day = 0;
      Activate(actTime);  // Shedule event
    }
    double actTime = 0;
    int day = 0;

};

class LaunchBreak : public Process {
  public:
    LaunchBreak(Defect * def) : Process() {
      defect = def;
    };

    void Behavior() {
      while(42){
        getTaxi:
        if(!Taxi.Busy()) {  // Taxi is free
          Seize(Taxi);
        }
        else {  // Taxi have customer
          customersOnStreet.InsFirst(this);  // Be right after current customer
          Passivate();
          Seize(Taxi);
        }
      
        double launchBreakTime = Exponential(30);
        defect -> day = 1;
        defect -> actTime = defect -> actTime + launchBreakTime; // Move defect time by launchbreak
        defect -> Activate(); // Let defect reschedule
        Wait(launchBreakTime);
        launchbreaks++;
        Release(Taxi);
        activateNextTransaction();
        Passivate();
      }
    }
    Defect *defect;
    int endOfDay = 0;
    int actTime = 0;
};

class EndOfDay : public Process { // Process because waits for the customer to get to place
  public:
    EndOfDay(Generator * gen, Defect * def, LaunchBreak * lb) : Process() {
      generator = gen;
      defect = def;
      launchbreak = lb;
    }
    void Behavior() {
      while(42) {
        double timeEnd = Time;
        interupted = 0;
        getTaxi:
        if(!Taxi.Busy()) {  // Taxi is free
          Seize(Taxi);
        }
        else {  // Taxi have customer
          customersOnStreet.InsFirst(this);  // Be right after current customer
          Passivate();
          Seize(Taxi);
        }
        while(customersOnPhone.Length() > 0) {
          Customer * cust = (Customer *)customersOnPhone.GetFirst();
          delete cust -> timeout;
          delete *cust;
        }
        while(customersOnStreet.Length() > 0) {
          Customer * cust = (Customer *)customersOnStreet.GetFirst();
          delete cust -> timeout;
          delete *cust;
        }

        workdays++; // add workday
        Release(Taxi);
        activateNextTransaction();
        generator -> day = 1; // set that he have to add day
        generator -> actTime = timeEnd + 960; // activate at the beggining of the workday
        generator -> Activate();
        defect -> day = 1; // set that he have to add day
        defect -> actTime = defect -> actTime + 960; // move by the time car is standing
        defect -> Activate();
        (new LaunchBreak(defect)) -> Activate(timeEnd + 960 + (Normal(240,30)));  // Set next launchbreak
        Activate(timeEnd+1440); // activate at the end of next working day
      }
    }
    int interupted = 0;

    Generator * generator;
    Defect * defect;
    LaunchBreak * launchbreak;
};

void activateNextTransaction() {
  if (!customersOnStreet.Empty()) { // there are customers on street (priority)
    Process * ent = (Customer *)(customersOnStreet.GetFirst());
    ent -> Activate();
  } 
  else if (!customersOnPhone.Empty()) { // there are customers on phone
    Process * ent = (Customer *)(customersOnPhone.GetFirst());
    ent -> Activate();
  }
}

int main(int argc, char ** argv) {
  RandomSeed(time(NULL));
  float genetationTime = 10;
  // SetOutput("taxi_service.dat");
  Init(0, 360000); // Approx 1 year in worktime

  if (argc == 2) {
    genetationTime = atof(argv[1]);
  }

  Generator * gen = new Generator(genetationTime,0);
  gen -> Activate();  // Activate generator of customers

  double firstDefectTime = Exponential(105120);
  Defect * def = new Defect();
  def->actTime = firstDefectTime;
  def -> Activate(firstDefectTime);  // Set first defect event

  LaunchBreak * lb = new LaunchBreak(def);  // Set first launchbreak
  lb -> Activate(Normal(240,30));

  EndOfDay * eod = new EndOfDay(gen, def, lb);
  eod -> Activate(480);   // Set first end of day

  Run();

  Print("Customers generation time is: %f\n", genetationTime);
  Print("Number of customers left %d\n", quitters);
  Print("Number of workdays: %d \n", workdays);
  Print("Launchbreaks: %d\n", launchbreaks);
  Print("Total trip income: %f USD\n", TripIncome.Sum());
  Print("Total trip distance: %f Miles\n", TripDistance.Sum());
  Taxi.Output();
  customersOnPhone.Output();
  customersOnStreet.Output();
  TripIncome.Output();
  TripDistance.Output();
  HistTripDistance.Output();
  HistTripTime.Output();
}