<?php
require_once('Array2XML.php');

/*
	Vypise zakladnu napovedu.
*/
function printHelp(){
    echo "Skript typu filtr (parse.php v jazyce PHP 5.6) načte ze standardního vstupu zdrojový kód v IPPcode18(viz sekce 6), zkontroluje lexikální a syntaktickou správnost kódu a vypíše na standardní výstup XML reprezentaci programu dle specifikace v sekci 3.1.\n";
	echo "Parametry:\n";
	echo "--help vypíše na standardní výstup nápovědu skriptu (nenačítá žádný vstup), tento parametr nelze kombinovat s žádným dalším parametrem \n";
	echo "Spustenie skriptu:\n";
	echo "php5.6 parse.php [--help]\n";
	exit(0);
}

function error21(){
   	fwrite(STDERR,"Chyba 21: Lexikalna alebo syntakticka chyba.\n");
	exit(21);
}

/*
	Pouziva getopt() na ziskanie argumentov skriptu z prikazovej riadky.
	Tieto argumenty vrati pre dalsie pouzitie.
*/
function loadArgs($argv){
    
    $shortopts = "";
    $longopts = array(
        "help",
		"stats:",
		"comments",
		"loc",
    );
    $opts = getopt($shortopts, $longopts);
    
	//echo count($argv)+"\n";
	//echo count($opts)+"\n";
    if (isset($opts['help']) && count($argv) == 2 && count($opts) == 1){
        printHelp();
    }
	else if(count($argv) == 1){
		return $opts;
	}
	else if(count($argv) == 3 && count($opts) == 2  && ((isset($opts['stats']) && isset($opts['comments']) ) || (isset($opts['stats']) && isset($opts['loc']) ) ) && !(isset($opts['help'])) ){
		return $opts;
	}
	else if(count($argv) == 4 && count($opts) == 3  && (isset($opts['stats']) && isset($opts['comments']) && isset($opts['loc']) ) ){
		return $opts;
	}
    else {
		fwrite(STDERR,"Chyba 10: Wrong arguments, try --help \n");
        exit(10);    
    }

}


/* Kontroluje ci $arg splna kriteria premennej */

function isvar($arg){
	$parts = explode("@", $arg);
	if(is_array($parts) && count($parts) == 2){ // overenie GF@meno (pocet)
		if(strcmp($parts[0],"LF") == 0 || strcmp($parts[0],"TF") == 0 || strcmp($parts[0],"GF") == 0){ // overenie ci je to LF, TF, GF ak nie tak chyba
			$name = str_split($parts[1]);
					// OVERENIE PRVEHO ZNAKU MENA PREMENNEJ
					// VELKE PISMENA									MALE PISMENA									SPECIALNE ZNAKY
			if((ord($name[0]) >= 65 && ord($name[0]) <= 90 ) || (ord($name[0]) >= 97 && ord($name[0]) <= 122 ) || (ord($name[0]) == 95 || ord($name[0]) == 45 || ord($name[0]) == 36 || ord($name[0]) == 38 || ord($name[0]) == 37 || ord($name[0]) == 42)){
				for($i = 1; $i < count($name); $i++){
							// OVERENIE ZVYSKU ZNAKOV MENA PREMENNEJ
							//VELKE PISMENA 								MALE PISMENA										CISLA
					if((ord($name[$i]) >= 65 && ord($name[$i]) <= 90 ) || (ord($name[$i]) >= 97 && ord($name[$i]) <= 122 ) || (ord($name[$i]) >= 48 && ord($name[$i]) <= 57 ) || (ord($name[$i]) == 95 || ord($name[$i]) == 45 || ord($name[$i]) == 36 || ord($name[$i]) == 38 || ord($name[$i]) == 37 || ord($name[$i]) == 42)){
					}
					else {
						return false;
					}
					
				}
				return true;
			}
			else{
				return false;
			}
		}
		else{
			return false;
		}
	}
	else{
		return false;
	}
}

/* Kontroluje ci $arg splna kriteria label.
	Samotna kontrola je velmi podobna isvar()*/
	
function islabel($arg){
	$name = str_split($arg);
	// OVERENIE PRVEHO ZNAKU MENA PREMENNEJ (nesmie byt cislo)
	// VELKE PISMENA									MALE PISMENA									SPECIALNE ZNAKY
	if((ord($name[0]) >= 65 && ord($name[0]) <= 90 ) || (ord($name[0]) >= 97 && ord($name[0]) <= 122 ) || (ord($name[0]) == 95 || ord($name[0]) == 45 || ord($name[0]) == 36 || ord($name[0]) == 38 || ord($name[0]) == 37 || ord($name[0]) == 42)){
		for($i = 1; $i < count($name); $i++){

			// OVERENIE ZVYSKU ZNAKOV MENA PREMENNEJ
			//VELKE PISMENA 								MALE PISMENA										CISLA
			if((ord($name[$i]) >= 65 && ord($name[$i]) <= 90 ) || (ord($name[$i]) >= 97 && ord($name[$i]) <= 122 ) || (ord($name[$i]) >= 48 && ord($name[$i]) <= 57 ) || (ord($name[$i]) == 95 || ord($name[$i]) == 45 || ord($name[$i]) == 36 || ord($name[$i]) == 38 || ord($name[$i]) == 37 || ord($name[$i]) == 42)){

			}
			else {
				return false;
			}
					
		}
		return true;
	}
	else{
		return false;
	}	
}

// Jednoducha kontrola ci sa jedna o typ splnajuci IPPcode18. 
function istype($arg){
	if(strcmp($arg, "int") == 0 || strcmp($arg, "string") ==0 || strcmp($arg,"bool") ==0){
		return true;
	}
	else{
		return false;
	}
}



/* Overenie ci sa jedna o konstantu typov string, int alebo bool

	Kazda je overovana zvlast kedze ma ine potreby. 

	
*/
function iscontant($arg){
	$parts = explode("@", $arg);
	if(is_array($parts) && count($parts) == 2){ // overenie string,int,bool@meno (pocet)
		if(strcmp($parts[0],"int") == 0){ // overenie ci je to int
			$value = str_split($parts[1]);
			if(count($value) == 1){
				//0-9 - ak jednomiestne cislo
				if(ord($value[0]) >= 48 && ord($value[0]) <= 57){
					return true;
				}
				else{
					return false;
				}
			}
			// ak viac miestne cislo tak na zaciatku nesmie byt 0, moze + -
			//		-						+					1-9
			if(ord($value[0]) == 45 || ord($value[0]) == 43 || (ord($value[0]) >= 49 && ord($value[0]) <= 57)){
				for($i = 1; $i < count($value); $i++){
							// OVERENIE ZVYSKU cisel - uz moze byt 0 ale nesmie + a -
					if(ord($value[$i]) >= 48 && ord($value[$i]) <= 57){
					}
					else {
						return false;
					}	
				}
				return true;
			}
			else {
				return false;
			}
		}
		else if(strcmp($parts[0],"bool") == 0){ //overenie ci je to bool
			if(strcmp($parts[1],"true") == 0 || strcmp($parts[1],"false") == 0){
				return true;
			}
			else{
				return false;
			}
		
		}
		else if(strcmp($parts[0],"string") == 0){ //overenie ci je to string 
			//rozdelenie na list znakov
			$value = str_split($parts[1]);
			$escape = 0;
			// cyklus pre prechod  listu
			for($i = 0; $i < count($value); $i++){
				$ordchar = ord($value[$i]);
				$count = count($value);
				//nesmu byt biele znaky
					
				if((ord($value[$i]) > 0 && ord($value[$i]) <= 32) || ord($value[$i]) == 35){
					return false;
				}
				else {
					//ak narazime na \ tak musi nasledovat trojcislie 0-999
					if(ord($value[$i]) == 92){
						if((ord($value[$i+1]) >= 48 && ord($value[$i+1]) <= 57) && (ord($value[$i+2]) >= 48 && ord($value[$i+2]) <= 57) && (ord($value[$i+3]) >= 48 && ord($value[$i+3]) <= 57)){
							$i = $i +3;
						}
						else {
							return false;
						}
					}
				}
			}
			return true;
		}
		else{
			return false;
		}
	}
	else{
		return false;
	}
}

//Spaja kontrolu konstanty a premennej aby overil ci sa jedna o <symb> zo zadania
function issymbol($arg){
	if(iscontant($arg) || isvar($arg)){
		return true;
	}
	else{
		return false;
	}
}

// Overuje spravnost argumentov instrukcii, rozdelene do skupin podla toho ake argumenty treba skontrolovat
// 0 - nothing 
// 1 - <var> <symb>
// 2 - <var>
// 3 - <label>
// 4 - <symb>
// 5 - <var> <symb1> <symb2>
// 6 - <var> <type>
// 7 - <label> <symb1> <symb2>
function analyzeArgs($case, $arg1, $arg2, $arg3){
	if($case == 0 && $arg1 == "" && $arg2 == "" && $arg3 == ""){
		
	}
	else if($case == 1 && $arg1 != "" && $arg2 != "" && $arg3 ==""){
		if(isvar($arg1) && issymbol($arg2)){
			//echo "OKAY Variable and Symbol\n";
		}
		else{
			error21();
		}
	}
	else if($case == 2 && $arg1 != "" && $arg2 == "" && $arg3 ==""){ // MALO BY FUNGOVAT TODO ZAPIS DO XML
		
		if(isvar($arg1)){
			//echo "OKAY Variable\n";
		}
		else{
			error21();
		}
	}
	else if($case == 3 && $arg1 != "" && $arg2 == "" && $arg3 ==""){ // MALO BY FUNGOVAT TODO ZAPIS DO XML
		
		if(islabel($arg1)){
			//echo "OKAY Label Name\n";
		}
		else{
			error21();
		}
		
	}
	else if($case == 4 && $arg1 != "" && $arg2 == "" && $arg3 ==""){
		if(issymbol($arg1)){
			//echo "OKAY Symbol\n";
		}
		else{
			error21();
		}		
	}
	else if($case == 5 && $arg1 != "" && $arg2 != "" && $arg3 !=""){
		if(isvar($arg1) && issymbol($arg2) && issymbol($arg3)){
			//echo "OKAY Variable and Symbol and symbol\n";
		}
		else{
			error21();
		}
	}
	else if($case == 6 && $arg1 != "" && $arg2 != "" && $arg3 ==""){
		if(isvar($arg1) && istype($arg2)){
			//echo "OKAY Variable and Type\n";
		}
		else{
			error21();
		}
	}
	else if($case == 7 && $arg1 != "" && $arg2 != "" && $arg3 !=""){
		if(islabel($arg1) && issymbol($arg2) && issymbol($arg3)){
			//echo "OKAY Label and Symbol and symbol\n";
		}
		else{
			error21();
		}
	}
	else{
		error21();
	}
	
	
}

/*
	Jednoducha kontrola ci sa instrukcia zhoduje z instrukciami definovanymi v IPPcode18
	Vracia true ak ano, konci program ak nie kedze je to lex chyba.
*/
function analyze($instruction, $arg1, $arg2, $arg3){
	$opcodes = array(	array("MOVE",1),
						array("CREATEFRAME",0),
						array("PUSHFRAME",0),
						array("POPFRAME",0),
						array("DEFVAR",2),
						array("CALL",3),
						array("RETURN",0),
						array("PUSHS",4),
						array("POPS",2),
						array("ADD",5),
						array("SUB",5),
						array("MUL",5),
						array("IDIV",5),
						array("LT",5),
						array("GT",5),
						array("EQ",5),
						array("AND",5),
						array("OR",5),
						array("NOT",1),
						array("INT2CHAR",1),
						array("STRI2INT",5),
						array("READ",6),
						array("WRITE",4),
						array("CONCAT",5),
						array("STRLEN",1),
						array("GETCHAR",5),
						array("SETCHAR",5),
						array("TYPE",1),
						array("LABEL",3),
						array("JUMP",3),
						array("JUMPIFEQ",7),
						array("JUMPIFNEQ",7),
						array("DPRINT",4),
						array("BREAK",0)
					);

					
	$instruction = strtoupper($instruction);
	$match = 0;
	
	for($code = 0; $code < 34; $code++){
		if(strcmp($instruction,$opcodes[$code][0]) == 0){
			$match = 1;
			analyzeArgs($opcodes[$code][1], $arg1, $arg2, $arg3);
		}
	}
	if($match != 1){
	fwrite(STDERR,"Chyba 21\n");
	exit(21);
	}
	else if($match == 1){
		return true;
	}
}

$args = loadArgs($argv);

//var_dump($args);

//premenne pre rozsirenie, len pocitadla
$no_instructions = 0;
$no_comments = 0;

//fwrite(STDERR,"Smile. \n");
$lines = 0;

$program = array();

// prvy riadok musi byt .IPPcode18
$f = trim(fgets(STDIN));
if($f != ".IPPcode18"){
	//echo "test\n";
	error21();
}
else{
	$program['@attributes'] = array(
		'language' => 'IPPcode18'
	);
}

$program['instruction'] = array();


while($f = fgets(STDIN)){ // TRIM odreze \n pozor na to...
    //echo "$f";			//pouzit explode na rozdelenie riadku na jednotlive casti...
						// pouzit str_split pre prechadzanie po znakoch						
	
	
	$test_array = str_split($f);
	$temp_char_array = array();
	$stage = -1;
	$lastchar = "";
	$instruction = "";
	$arg1 = "";
	$arg2 = "";
	$arg3 = "";
	
	// Parsuje vstupny riadok
	// Rozdelene do 5 stadii
	// 0-3 reprezentuju stadium vytvarania instruction, arg1, arg2, arg3
	// 4 reprezentuje ignorovanie komentaru v IPPcode18
	// 5 konecne stadium ked su vsetky potrebne premenne naplnene, ak v tomto stadiu pride dalsi znak jedna sa o chybu
	foreach($test_array as $char){
		$ordchar = ord($char);
		//echo "Stage $stage, Char $ordchar \n";
		if(ord($char) == 35){
			$no_comments = $no_comments +1;
			if($stage == -1){
				$stage = 4;
				$lastchar =$char;
			}
			else if($stage == 0){
				$stage = 4;
				$lastchar =$char;
				$instruction = implode($temp_char_array);
				$temp_char_array = array();
			}
			else if($stage == 1){
				$stage = 4;
				$lastchar =$char;
				$arg1 = implode($temp_char_array);
				$temp_char_array = array();
			}
			else if($stage == 2){
				$stage = 4;
				$lastchar =$char;
				$arg2 = implode($temp_char_array);
				$temp_char_array = array();
			}
			else if($stage == 3){
				$stage = 4;
				$lastchar =$char;
				$arg3 = implode($temp_char_array);
				$temp_char_array = array();
			}
			else if($stage == 5){
				$stage = 4;
				$lastchar =$char;
			}
		}
		else if($stage == 5 && (ord($char) != 32 && ord($char) != 9 && ord($char) != 10)){
			fwrite(STDERR,"Chyba 21.\n");
			exit(21);
		}
		else if($stage == -1 && (ord($char) != 32 && ord($char) != 9 && ord($char) != 10)){
			$stage = 0;
			//echo "Test 1\n";
			$lastchar =$char;
			array_push($temp_char_array, $char);	
		}
		else if ($stage == 0 && (ord($char) != 32 && ord($char) != 9 && ord($char) != 10)){
			//echo "Test 2\n";
			$lastchar =$char;
			array_push($temp_char_array, $char);
		}
		else if ($stage == 0 && (ord($char) == 32 || ord($char) == 9) && (ord($lastchar) != 32 && ord($lastchar) != 9)){
			//echo "Test 3\n";
			$stage = 1;
			$lastchar =$char;
			$instruction = implode($temp_char_array);
			$temp_char_array = array();
		}
		else if ($stage == 1 && (ord($char) != 32 && ord($char) != 9 && ord($char) != 10)){
			//echo "Test 4\n";
			$lastchar =$char;
			array_push($temp_char_array, $char);
		}
		else if ($stage == 1 && (ord($char) == 32 || ord($char) == 9) && (ord($lastchar) != 32 && ord($lastchar) != 9)){
			//echo "Test 5\n";
			$stage = 2;
			$lastchar =$char;
			$arg1 = implode($temp_char_array);
			$temp_char_array = array();
		}
		else if ($stage == 2 && (ord($char) != 32 && ord($char) != 9 && ord($char) != 10)){
			//echo "Test 6\n";
			$lastchar =$char;
			array_push($temp_char_array, $char);
		}
		else if ($stage == 2 && (ord($char) == 32 || ord($char) == 9) && (ord($lastchar) != 32 && ord($lastchar) != 9)){
			//echo "Test 7\n";
			$stage = 3;
			$lastchar =$char;
			$arg2 = implode($temp_char_array);
			$temp_char_array = array();
		}
		else if ($stage == 3 && (ord($char) != 32 && ord($char) != 9 && ord($char) != 10)){
			//echo "Test 8\n";
			$lastchar =$char;
			array_push($temp_char_array, $char);
		}
		else if ($stage == 3 && (ord($char) == 32 || ord($char) == 9) && (ord($lastchar) != 32 && ord($lastchar) != 9)){
			//echo "Test 9\n";
			$stage = 5; // TU BOLA -1 teoreticky treba stage 5 aby vyskocil error ak po 3 argumentoch pride este nieco dalsie okrem komentara...
			$lastchar =$char;
			$arg3 = implode($temp_char_array);
			$temp_char_array = array();
		}
		else if ($stage == 0 && ord($char) == 10){
			$stage = -1;
			$lastchar =$char;
			$instruction = implode($temp_char_array);
			$temp_char_array = array();
		}
		else if ($stage == 1 && ord($char) == 10){
			$stage = -1;
			$lastchar =$char;
			$arg1 = implode($temp_char_array);
			$temp_char_array = array();
		}
		else if ($stage == 2 && ord($char) == 10){
			$stage = -1;
			$lastchar =$char;
			$arg2 = implode($temp_char_array);
			$temp_char_array = array();
		}
		else if ($stage == 3 && ord($char) == 10){
			$stage = -1;
			$lastchar =$char;
			$arg3 = implode($temp_char_array);
			$temp_char_array = array();
		}
		else if (ord($char) == 10){
			$stage = -1;
			$lastchar =$char;
		}
	}
	
	//echo "Instruction: $instruction \n";
	//echo "Arg1: $arg1, Arg2: $arg2, Arg3: $arg3 \n";
	
	//Ak mame instrukciu a nie prazdny riadok tak inkrementujeme pocitadlo.
	if($instruction != null){
	$lines++;
	$no_instructions++;
	}
	
	
	// Nasleduje vyuzitie Array2XML kniznice pre vytvorenie XML vystupu
	
	if($instruction != ""){
		if(analyze($instruction, $arg1, $arg2, $arg3)){ //analyza prejde v pohode tak pridanie do struktury XML na vypis
			if( strcmp(strtoupper($instruction),"CREATEFRAME") == 0 || strcmp(strtoupper($instruction),"PUSHFRAME") == 0 || strcmp(strtoupper($instruction),"POPFRAME") == 0 || strcmp(strtoupper($instruction),"RETURN") == 0 || strcmp(strtoupper($instruction),"BREAK") == 0){
				//echo "$lines \n";
				$program['instruction'][] = array( //empty node with attributes
					'@attributes' => array(
						'order' => $lines,
						'opcode' => strtoupper($instruction)
					)
				);
			}
			else if( strcmp(strtoupper($instruction),"CALL") == 0 || strcmp(strtoupper($instruction),"LABEL") == 0 || strcmp(strtoupper($instruction),"JUMP") == 0){
				$name = str_split($arg1);
				$arg_xml = array();
				
				for($i = 0; $i < count($name); $i++){
					if(ord($name[$i]) == 38){ // ak je to & tak potrebujeme urobit &amp
						array_push($arg_xml, $name[$i]);
						//array_push($arg_xml, "&amp");
					}
					else{
						array_push($arg_xml, $name[$i]);
					}
				}
				
				$program['instruction'][] = array( //empty node with attributes
					'@attributes' => array(
						'order' => $lines,
						'opcode' => strtoupper($instruction)
					),
					'arg1' => array(
						'@value' => implode($arg_xml),
						'@attributes' => array(
							'type' => 'label'
						)
					)
				);
				
			}
			else if( strcmp(strtoupper($instruction),"DEFVAR") == 0 || strcmp(strtoupper($instruction),"POPS") == 0){
				$program['instruction'][] = array( //empty node with attributes
					'@attributes' => array(
						'order' => $lines,
						'opcode' => strtoupper($instruction)
					),
					'arg1' => array(
						'@value' => $arg1,
						'@attributes' => array(
							'type' => 'var'
						)
					)
				);
			}
			else if (strcmp(strtoupper($instruction),"PUSHS") == 0 || strcmp(strtoupper($instruction),"WRITE") == 0 || strcmp(strtoupper($instruction),"DPRINT") == 0){
				$parts = explode("@", $arg1);
				
				if(strcmp(strtoupper($parts[0]),"GF") == 0 || strcmp(strtoupper($parts[0]),"LF") == 0 || strcmp(strtoupper($parts[0]),"TF") == 0){ // VAR
					$program['instruction'][] = array( //empty node with attributes
						'@attributes' => array(
							'order' => $lines,
							'opcode' => strtoupper($instruction)
						),
						'arg1' => array(
							'@value' => $arg1,
							'@attributes' => array(
								'type' => 'var'
							)
						)
					);
					
				}
				else if(strcmp($parts[0],"bool") == 0){ //value musi byt smallletters
					$program['instruction'][] = array( 
						'@attributes' => array(
							'order' => $lines,
							'opcode' => strtoupper($instruction)
						),
						'arg1' => array(
							'@value' => strtolower($parts[1]),
							'@attributes' => array(
								'type' => $parts[0]
							)
						)
					);
					
				}
				else{ //constant
					$program['instruction'][] = array( 
						'@attributes' => array(
							'order' => $lines,
							'opcode' => strtoupper($instruction)
						),
						'arg1' => array(
							'@value' => $parts[1],
							'@attributes' => array(
								'type' => $parts[0]
							)
						)
					);
				}
				
			}
			else if(strcmp(strtoupper($instruction),"MOVE") == 0 || strcmp(strtoupper($instruction),"INT2CHAR") == 0 || strcmp(strtoupper($instruction),"STRLEN") == 0 || strcmp(strtoupper($instruction),"TYPE") == 0 || strcmp(strtoupper($instruction),"NOT") == 0){
				$parts2 = explode("@", $arg2);
				
				if(isvar($arg2)){
					$program['instruction'][] = array( //empty node with attributes
						'@attributes' => array(
							'order' => $lines,
							'opcode' => strtoupper($instruction)
						),
						'arg1' => array(
							'@value' => $arg1,
							'@attributes' => array(
								'type' => 'var'
							)
						),
						'arg2' => array(
							'@value' => $arg2,
							'@attributes' => array(
								'type' => 'var'
							)
						)
					);
				}
				else if (iscontant($arg2)){
					$program['instruction'][] = array( //empty node with attributes
						'@attributes' => array(
							'order' => $lines,
							'opcode' => strtoupper($instruction)
						),
						'arg1' => array(
							'@value' => $arg1,
							'@attributes' => array(
								'type' => 'var'
							)
						),
						'arg2' => array(
							'@value' => $parts2[1],
							'@attributes' => array(
								'type' => $parts2[0]
							)
						)
					);
				}
					
			}
			else if (strcmp(strtoupper($instruction),"READ") == 0){
				if(istype($arg2)){
					$program['instruction'][] = array(
						'@attributes' => array(
							'order' => $lines,
							'opcode' => strtoupper($instruction)
						),
						'arg1' => array(
							'@value' => $arg1,
							'@attributes' => array(
								'type' => 'var'
							)
						),
						'arg2' => array(
							'@value' => $arg2,
							'@attributes' => array(
								'type' => 'type'
							)
						)
					);
				}
				
			}
			else if (strcmp(strtoupper($instruction),"JUMPIFEQ") == 0 || strcmp(strtoupper($instruction),"JUMPIFNEQ") == 0){
				$parts2 = explode("@", $arg2);
				$parts3 = explode("@", $arg3);
				
				if(isvar($arg2) && isvar($arg3)){
					$program['instruction'][] = array( 
						'@attributes' => array(
							'order' => $lines,
							'opcode' => strtoupper($instruction)
						),
						'arg1' => array(
							'@value' => $arg1,
							'@attributes' => array(
								'type' => 'label'
							)
						),
						'arg2' => array(
							'@value' => $arg2,
							'@attributes' => array(
								'type' => 'var'
							)
						),
						'arg3' => array(
							'@value' => $arg3,
							'@attributes' => array(
								'type' => 'var'
							)
						)
					);
				}
				else if(isvar($arg2) && iscontant($arg3)){
					
					$program['instruction'][] = array( 
						'@attributes' => array(
							'order' => $lines,
							'opcode' => strtoupper($instruction)
						),
						'arg1' => array(
							'@value' => $arg1,
							'@attributes' => array(
								'type' => 'label'
							)
						),
						'arg2' => array(
							'@value' => $arg2,
							'@attributes' => array(
								'type' => 'var'
							)
						),
						'arg3' => array(
							'@value' => $parts3[1],
							'@attributes' => array(
								'type' => $parts3[0]
							)
						)
					);
					
				}
				
				else if(iscontant($arg2) && isvar($arg3)){
					
					$program['instruction'][] = array( 
						'@attributes' => array(
							'order' => $lines,
							'opcode' => strtoupper($instruction)
						),
						'arg1' => array(
							'@value' => $arg1,
							'@attributes' => array(
								'type' => 'label'
							)
						),
						'arg2' => array(
							'@value' => $parts2[1],
							'@attributes' => array(
								'type' => $parts2[0]
							)
						),
						'arg3' => array(
							'@value' => $arg3,
							'@attributes' => array(
								'type' => 'var'
							)
						)
					);
				}
				else if(iscontant($arg2) && iscontant($arg3)){
					
					$program['instruction'][] = array( 
						'@attributes' => array(
							'order' => $lines,
							'opcode' => strtoupper($instruction)
						),
						'arg1' => array(
							'@value' => $arg1,
							'@attributes' => array(
								'type' => 'label'
							)
						),
						'arg2' => array(
							'@value' => $parts2[1],
							'@attributes' => array(
								'type' => $parts2[0]
							)
						),
						'arg3' => array(
							'@value' => $parts3[1],
							'@attributes' => array(
								'type' => $parts3[0]
							)
						)
					);
				}
				
			}
			else if(strcmp(strtoupper($instruction),"ADD") == 0 || strcmp(strtoupper($instruction),"SUB") == 0 || strcmp(strtoupper($instruction),"MUL") == 0 ||
					strcmp(strtoupper($instruction),"IDIV") == 0 || strcmp(strtoupper($instruction),"LT") == 0 || strcmp(strtoupper($instruction),"GT") == 0 ||
					strcmp(strtoupper($instruction),"EQ") == 0 || strcmp(strtoupper($instruction),"AND") == 0 || strcmp(strtoupper($instruction),"OR") == 0 ||
					strcmp(strtoupper($instruction),"STRI2INT") == 0 || strcmp(strtoupper($instruction),"CONCAT") == 0 ||
					strcmp(strtoupper($instruction),"GETCHAR") == 0 || strcmp(strtoupper($instruction),"SETCHAR") == 0){
						
				$parts2 = explode("@", $arg2);
				$parts3 = explode("@", $arg3);
				
				if(isvar($arg2) && isvar($arg3)){
					$program['instruction'][] = array( 
						'@attributes' => array(
							'order' => $lines,
							'opcode' => strtoupper($instruction)
						),
						'arg1' => array(
							'@value' => $arg1,
							'@attributes' => array(
								'type' => 'var'
							)
						),
						'arg2' => array(
							'@value' => $arg2,
							'@attributes' => array(
								'type' => 'var'
							)
						),
						'arg3' => array(
							'@value' => $arg3,
							'@attributes' => array(
								'type' => 'var'
							)
						)
					);
				}
				else if(isvar($arg2) && iscontant($arg3)){
					
					$program['instruction'][] = array( 
						'@attributes' => array(
							'order' => $lines,
							'opcode' => strtoupper($instruction)
						),
						'arg1' => array(
							'@value' => $arg1,
							'@attributes' => array(
								'type' => 'var'
							)
						),
						'arg2' => array(
							'@value' => $arg2,
							'@attributes' => array(
								'type' => 'var'
							)
						),
						'arg3' => array(
							'@value' => $parts3[1],
							'@attributes' => array(
								'type' => $parts3[0]
							)
						)
					);
					
				}
				
				else if(iscontant($arg2) && isvar($arg3)){
					
					$program['instruction'][] = array( 
						'@attributes' => array(
							'order' => $lines,
							'opcode' => strtoupper($instruction)
						),
						'arg1' => array(
							'@value' => $arg1,
							'@attributes' => array(
								'type' => 'var'
							)
						),
						'arg2' => array(
							'@value' => $parts2[1],
							'@attributes' => array(
								'type' => $parts2[0]
							)
						),
						'arg3' => array(
							'@value' => $arg3,
							'@attributes' => array(
								'type' => 'var'
							)
						)
					);
				}
				else if(iscontant($arg2) && iscontant($arg3)){
					
					$program['instruction'][] = array( 
						'@attributes' => array(
							'order' => $lines,
							'opcode' => strtoupper($instruction)
						),
						'arg1' => array(
							'@value' => $arg1,
							'@attributes' => array(
								'type' => 'var'
							)
						),
						'arg2' => array(
							'@value' => $parts2[1],
							'@attributes' => array(
								'type' => $parts2[0]
							)
						),
						'arg3' => array(
							'@value' => $parts3[1],
							'@attributes' => array(
								'type' => $parts3[0]
							)
						)
					);
				}
			
				
			}
		}
	}
}


//Array2XML::init($version /* ='1.0' */, $encoding /* ='UTF-8' */);
$xml = Array2XML::createXML('program', $program);
echo $xml->saveXML();

$content ="";
//echo count($args);


// Implementuje rozsirenie
// Podla nastavenych parametrov skriptu zistujem co vypisat do suboru.


if(count($args) == 2 && isset($args['loc'])){
	if(file_put_contents($args['stats'],$no_instructions)){
	
	}
	else{
		fwrite(STDERR, "Chyba 12: Chyba pri otvarani vystupneho suboru pre zapis\n");
		exit(12);
	}
}
else if(count($args) == 2 && isset($args['comments'])){
	if(file_put_contents($args['stats'],$no_comments)){
	
	}
	else{
		fwrite(STDERR, "Chyba 12: Chyba pri otvarani vystupneho suboru pre zapis\n");
		exit(12);
	}
}
else if (count($args) == 3 && isset($args['loc']) && isset($args['comments'])){
	$content .= $no_instructions;
	$content .= "\n";
	$content .= $no_comments;
	$content .= "\n";
	if(file_put_contents($args['stats'],$content)){
	
	}
	else{
		fwrite(STDERR, "Chyba 12: Chyba pri otvarani vystupneho suboru pre zapis\n");
		exit(12);
	}
	
}


//echo $no_instructions;
//echo $no_comments;

exit(0);
?>