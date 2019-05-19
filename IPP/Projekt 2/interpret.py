import xml.etree.ElementTree as ET
import getopt, sys

# Trieda pouzita pre ukladanie instrukcii do listu
class Instuction:
	def __init__(self, instruction):
		self.order = instruction.get('order') #poradie instrukcie
		self.opcode = instruction.get('opcode') #operacny kod instrukcie
		self.child_count = len(instruction) #pocet deti = poctu argumentov
		self.arg1_type = None
		self.arg1_value = None
		self.arg2_type = None
		self.arg2_value = None
		self.arg3_type = None
		self.arg3_value = None
		#podla poctu deti vieme kolko argumentov treba vyplnit datami
		if self.child_count == 1:
			self.arg1_type = instruction[0].attrib['type']
			self.arg1_value = instruction[0].text
		elif self.child_count == 2:
			self.arg1_type = instruction[0].attrib['type']
			self.arg1_value = instruction[0].text
			self.arg2_type = instruction[1].attrib['type']
			self.arg2_value = instruction[1].text
		elif self.child_count == 3:
			self.arg1_type = instruction[0].attrib['type']
			self.arg1_value = instruction[0].text	
			self.arg2_type = instruction[1].attrib['type']
			self.arg2_value = instruction[1].text
			self.arg3_type = instruction[2].attrib['type']
			self.arg3_value = instruction[2].text

# Trieda pre uchovanie priamej hodnoty premennej v IPPcode18
class IPPvariable:
	def __init__(self,type,value):
		self.type = type
		self.value = value
			
def arg_check(opts):
	#print(opts)
	for o, a in opts:
		#	Vypise zakladnu napovedu.
		if o == "--help" and len(opts) ==1:
			help_text = "Program načte XML reprezentaci programu ze zadaného souboru a tento program s využitím standardního vstupu a výstupu interpretuje. \n Parametry:\n--help vypíše na standardní výstup nápovědu skriptu (nenačítá žádný vstup), tento parametr nelze kombinovat s žádným dalším parametrem\n --source=file vstupní soubor s XML reprezentací zdrojového kódu \nSpustenie skriptu:\n python3 interpret.py --source=file [--help]";
			print (help_text)
			sys.exit(0)
		elif o == "--source" and len(opts) ==1:
		#ak source tak vrati nazov suboru
			return a
		else:
			sys.stderr.write("error\n")
			sys.exit(1)
# Overuje ci mame premennu alebo label
# Obe pozaduju rovnake vlastnosti. 
# Na zaciatku nesmie byt cislo
def isvar_or_label(arg_value):
	#prve pismeno
	if arg_value == None or arg_value == "":
		return 0
	if (ord(arg_value[0]) >= 65 and ord(arg_value[0]) <= 90 ) or (ord(arg_value[0]) >= 97 and ord(arg_value[0]) <= 122) or (ord(arg_value[0]) == 95 or ord(arg_value[0]) == 45 or ord(arg_value[0]) == 36 or ord(arg_value[0]) == 38 or ord(arg_value[0]) == 37 or ord(arg_value[0]) == 42):
		#ostatne pismena
		i = 1
		while(i<len(arg_value)):
			if (ord(arg_value[i]) >= 48 and ord(arg_value[i])<= 57)or (ord(arg_value[i]) >= 65 and ord(arg_value[i]) <= 90 ) or (ord(arg_value[i]) >= 97 and ord(arg_value[i]) <= 122) or (ord(arg_value[i]) == 95 or ord(arg_value[i]) == 45 or ord(arg_value[i]) == 36 or ord(arg_value[i]) == 38 or ord(arg_value[i]) == 37 or ord(arg_value[i]) == 42):
				i = i+1
			else:
				return 0
		return 1
	else:
		return 0
		
def istype(arg_value):
	if arg_value == "int" or arg_value == "string" or arg_value == "bool":
		return 1
	else:
		return 0


#vlastna funkcia pre overenie ci mame cele cislo
# Implementovana pretoze isdigit nesplnalo ocakavania
# Na zaciatku nesmie byt 0 a moze byt +-
# Dalej uz moze byt vsetko okrem +-
# Kedze ide o cele cislo . sa tiez nemoze objavit		
def custom_isint(arg_value):
	if len(arg_value) == 1:
		if ord(arg_value) >=48 and ord(arg_value) <= 57:
			return 1
		else:
			return 0
	else:
		if ord(arg_value[0]) == 45 or ord(arg_value[0]) == 43 or (ord(arg_value[0]) >= 49 and ord(arg_value[0]) <=57):
			i = 1
			while(i<len(arg_value)):
				if ord(arg_value[i]) >=48 and ord(arg_value[i]) <= 57:
					i = i+1
				else:
					return 0
			return 1
		else:
			return 0

def custom_isbool(arg_value):
	if arg_value == "true" or arg_value == "false":
		return 1
	else:
		return 0

# Overenie ci mame spravny string
# Nesmie obsahovat biele znaky. Tie musia byt zapisane pomocou Unicode \xyz xyz je 0-999

def custom_isstring(arg_value):
	if arg_value == None:
		return 1
	i = 0
	while( i < len(arg_value)):
		if (ord(arg_value[i]) > 0 and ord(arg_value[i]) <=32) or ord(arg_value[i]) == 35:
			return 0
		else:
		#kontrola ak pride \ ci nasledujuce tri znaky su cisla
			if ord(arg_value[i]) == 92:
				if (ord(arg_value[i+1]) >= 48 and ord(arg_value[i+1]) <= 57) and (ord(arg_value[i+2]) >= 48 and ord(arg_value[i+2]) <= 57) and (ord(arg_value[i+3]) >= 48 and ord(arg_value[i+3]) <= 57):
					i = i + 4
				else:
					return 0
			else:
				i = i + 1
	return 1

# Funkcia zistuje ci argumenty instrukcie splnuju ocakavania instrukcie
# Rozdelene do tychto skupin:		
# // 0 - nothing 
# // 1 - <var> <symb>
# // 2 - <var>
# // 3 - <label>
# // 4 - <symb>
# // 5 - <var> <symb1> <symb2>
# // 6 - <var> <type>
# // 7 - <label> <symb1> <symb2>
# V kazdom pripade pouzivame na overenie vlastne funkcie z hora.
def analyze_instruction_args(instruction_to_check, case):
	if case == 0 and instruction_to_check.arg1_type == None and instruction_to_check.arg2_type == None and instruction_to_check.arg3_type == None:
		return 1
	elif case == 1 and instruction_to_check.arg1_type == "var" and instruction_to_check.arg2_type != None and instruction_to_check.arg3_type == None:
		#overit ci to je var/ symb podla type atributu potom kontrolovat spravnost value
		#ak var tak splitnut
		arg1 = parse_variable(instruction_to_check.arg1_value)
		if len(arg1) != 2:
			return 0
		if isvar_or_label(arg1[1]):
			if instruction_to_check.arg2_type == "var":
				arg2 = parse_variable(instruction_to_check.arg2_value)
				if len(arg2) != 2:
					return 0
				if isvar_or_label(arg2[1]):
					return 1
				else:
					return 0
			elif instruction_to_check.arg2_type == "int" and custom_isint(instruction_to_check.arg2_value):
				return 1
			elif instruction_to_check.arg2_type == "string" and custom_isstring(instruction_to_check.arg2_value):
				return 1
			elif instruction_to_check.arg2_type =="bool" and custom_isbool(instruction_to_check.arg2_value):
				return 1
			else:
				return 0
		else:
			return 0
	elif case == 2 and instruction_to_check.arg1_type == "var" and instruction_to_check.arg2_type == None and instruction_to_check.arg3_type == None:
		arg1 = parse_variable(instruction_to_check.arg1_value)
		if len(arg1) != 2:
			return 0
		if isvar_or_label(arg1[1]):
			return 1
		else:
			return 0
	elif case == 3 and instruction_to_check.arg1_type == "label" and instruction_to_check.arg2_type == None and instruction_to_check.arg3_type == None:
		if isvar_or_label(instruction_to_check.arg1_value):
			return 1
		else:
			return 0
	elif case == 4 and instruction_to_check.arg1_type != None and instruction_to_check.arg2_type == None and instruction_to_check.arg3_type == None:
		if instruction_to_check.arg1_type == "var":
			arg1 = parse_variable(instruction_to_check.arg1_value)
			if len(arg1) != 2:
				return 0
			if isvar_or_label(arg1[1]):
				return 1
			else:
				return 0
		elif instruction_to_check.arg1_type == "int" and custom_isint(instruction_to_check.arg1_value):
			return 1
		elif instruction_to_check.arg1_type == "string" and custom_isstring(instruction_to_check.arg1_value):
			return 1
		elif instruction_to_check.arg1_type == "bool" and custom_isbool(instruction_to_check.arg1_value):
			return 1
		else:
			return 0
	elif case == 5 and instruction_to_check.arg1_type == "var" and instruction_to_check.arg2_type != None and instruction_to_check.arg3_type != None:
		arg1 = parse_variable(instruction_to_check.arg1_value)
		if len(arg1) != 2:
			return 0
		if isvar_or_label(arg1[1]):
			if instruction_to_check.arg2_type == "var":
				arg2 = parse_variable(instruction_to_check.arg2_value)
				if len(arg2) != 2:
					return 0
				if isvar_or_label(arg2[1]):
					if instruction_to_check.arg3_type == "var":
						arg3 = parse_variable(instruction_to_check.arg3_value)
						if len(arg3) != 2:
							return 0
						if isvar_or_label(arg3[1]):
							return 1
						else:
							return 0
					elif instruction_to_check.arg3_type == "int" and custom_isint(instruction_to_check.arg3_value):
						return 1
					elif instruction_to_check.arg3_type == "string" and custom_isstring(instruction_to_check.arg3_value):
						return 1
					elif instruction_to_check.arg3_type =="bool" and custom_isbool(instruction_to_check.arg3_value):
						return 1
					else:
						return 0
			elif instruction_to_check.arg2_type == "int" and custom_isint(instruction_to_check.arg2_value):
				if instruction_to_check.arg3_type == "var":
					arg3 = parse_variable(instruction_to_check.arg3_value)
					if len(arg3) != 2:
						return 0
					if isvar_or_label(arg3[1]):
						return 1
					else:
						return 0
				elif instruction_to_check.arg3_type == "int" and custom_isint(instruction_to_check.arg3_value):
					return 1
				elif instruction_to_check.arg3_type == "string" and custom_isstring(instruction_to_check.arg3_value):
					return 1
				elif instruction_to_check.arg3_type =="bool" and custom_isbool(instruction_to_check.arg3_value):
					return 1
				else:
					return 0
			elif instruction_to_check.arg2_type == "string" and custom_isstring(instruction_to_check.arg2_value):
				if instruction_to_check.arg3_type == "var":
					arg3 = parse_variable(instruction_to_check.arg3_value)
					if len(arg3) != 2:
						return 0
					if isvar_or_label(arg3[1]):
						return 1
					else:
						return 0
				elif instruction_to_check.arg3_type == "int" and custom_isint(instruction_to_check.arg3_value):
					return 1
				elif instruction_to_check.arg3_type == "string" and custom_isstring(instruction_to_check.arg3_value):
					return 1
				elif instruction_to_check.arg3_type =="bool" and custom_isbool(instruction_to_check.arg3_value):
					return 1
				else:
					return 0
			elif instruction_to_check.arg2_type =="bool" and custom_isbool(instruction_to_check.arg2_value):
				if instruction_to_check.arg3_type == "var":
					arg3 = parse_variable(instruction_to_check.arg3_value)
					if len(arg3) != 2:
						return 0
					if isvar_or_label(arg3[1]):
						return 1
					else:
						return 0
				elif instruction_to_check.arg3_type == "int" and custom_isint(instruction_to_check.arg3_value):
					return 1
				elif instruction_to_check.arg3_type == "string" and custom_isstring(instruction_to_check.arg3_value):
					return 1
				elif instruction_to_check.arg3_type =="bool" and custom_isbool(instruction_to_check.arg3_value):
					return 1
				else:
					return 0
			else:
				return 0
		else:
			return 0
	elif case == 6 and instruction_to_check.arg1_type == "var" and instruction_to_check.arg2_type == "type" and instruction_to_check.arg3_type == None:
		arg1 = parse_variable(instruction_to_check.arg1_value)
		if len(arg1) != 2:
			return 0
		if isvar_or_label(arg1[1]):
			if istype(instruction_to_check.arg2_value):
				return 1
			else:
				return 0
		else:
			return 0
	elif case == 7 and instruction_to_check.arg1_type == "label" and instruction_to_check.arg2_type != None and instruction_to_check.arg3_type != None:
		if isvar_or_label(instruction_to_check.arg1_value):
			if instruction_to_check.arg2_type == "var":
				arg2 = parse_variable(instruction_to_check.arg2_value)
				if len(arg2) != 2:
					return 0
				if isvar_or_label(arg2[1]):
					if instruction_to_check.arg3_type == "var":
						arg3 = parse_variable(instruction_to_check.arg3_value)
						if len(arg3)!= 2:
							return 0
						if isvar_or_label(arg3[1]):
							return 1
						else:
							return 0
					elif instruction_to_check.arg3_type == "int" and custom_isint(instruction_to_check.arg3_value):
						return 1
					elif instruction_to_check.arg3_type == "string" and custom_isstring(instruction_to_check.arg3_value):
						return 1
					elif instruction_to_check.arg3_type =="bool" and custom_isbool(instruction_to_check.arg3_value):
						return 1
					else:
						return 0
			elif instruction_to_check.arg2_type == "int" and custom_isint(instruction_to_check.arg2_value):
				if instruction_to_check.arg3_type == "var":
					arg3 = parse_variable(instruction_to_check.arg3_value)
					if len(arg3) != 2:
						return 0
					if isvar_or_label(arg3[1]):
						return 1
					else:
						return 0
				elif instruction_to_check.arg3_type == "int" and custom_isint(instruction_to_check.arg3_value):
					return 1
				elif instruction_to_check.arg3_type == "string" and custom_isstring(instruction_to_check.arg3_value):
					return 1
				elif instruction_to_check.arg3_type =="bool" and custom_isbool(instruction_to_check.arg3_value):
					return 1
				else:
					return 0
			elif instruction_to_check.arg2_type == "string" and custom_isstring(instruction_to_check.arg2_value):
				if instruction_to_check.arg3_type == "var":
					arg3 = parse_variable(instruction_to_check.arg3_value)
					if len(arg3) != 2:
						return 0
					if isvar_or_label(arg3[1]):
						return 1
					else:
						return 0
				elif instruction_to_check.arg3_type == "int" and custom_isint(instruction_to_check.arg3_value):
					return 1
				elif instruction_to_check.arg3_type == "string" and custom_isstring(instruction_to_check.arg3_value):
					return 1
				elif instruction_to_check.arg3_type =="bool" and custom_isbool(instruction_to_check.arg3_value):
					return 1
				else:
					return 0
			elif instruction_to_check.arg2_type =="bool" and custom_isbool(instruction_to_check.arg2_value):
				if instruction_to_check.arg3_type == "var":
					arg3 = parse_variable(instruction_to_check.arg3_value)
					if len(arg3) != 2:
						return 0
					if isvar_or_label(arg3[1]):
						return 1
					else:
						return 0
				elif instruction_to_check.arg3_type == "int" and custom_isint(instruction_to_check.arg3_value):
					return 1
				elif instruction_to_check.arg3_type == "string" and custom_isstring(instruction_to_check.arg3_value):
					return 1
				elif instruction_to_check.arg3_type =="bool" and custom_isbool(instruction_to_check.arg3_value):
					return 1
				else:
					return 0
			else:
				return 0
		else:
			return 0
	else:
		return 0
	# Jednoducha kontrola ci sa instrukcia zhoduje z instrukciami definovanymi v IPPcode18
	# Vracia true ak ano, konci program ak nie kedze je to lex chyba.
	
def instruction_check(instruction_to_check):
	opcodes = [('MOVE', 1),('CREATEFRAME', 0),('PUSHFRAME', 0),('POPFRAME', 0),('DEFVAR', 2),('CALL', 3),('RETURN', 0),('PUSHS', 4),('POPS', 2),('ADD', 5),('SUB', 5),('MUL', 5),('IDIV', 5),('LT', 5),('GT', 5),('EQ', 5),
	('AND', 5),('OR', 5),('NOT', 1),('INT2CHAR', 1),('STRI2INT', 5),('READ', 6),('WRITE', 4),('CONCAT', 5),('STRLEN', 1),('GETCHAR', 5),('SETCHAR', 5),('TYPE', 1),('LABEL', 3),('JUMP', 3),('JUMPIFEQ', 7),('JUMPIFNEQ', 7),
	('DPRINT', 4),('BREAK', 0)]
	temp_opcode = instruction_to_check.opcode.upper()
	match = 0
	for code, case in opcodes:
		if code == temp_opcode:
			match = 1
			# Nasledne analyzuj ci aj argumenty splnaju predpoklady IPPcode18
			if analyze_instruction_args(instruction_to_check, case) == 0:
				return 0
	return 1

	
#Pomocna funkcia na rychle rozdelenie premenneg (GF@nazov) na frame a meno
def parse_variable(string):
	temp = string.split('@')
	if temp[0] == "GF" or temp[0] == "LF" or temp[0] == "TF":
		return string.split('@')	
	else:
		sys.stderr.write("Chyba: Zle definovany ramec")
		sys.exit(32)

# Funkcia ktora je potrebna pre spravny vypis stringov
# Jej uloha je nahradit \xyz definijucu Unicode prislusnym znakom
# Vracia string, kde su vsetky Unicode nahradene prislusnym znakom.		
def parse_string(string):
	#parse variable name
	ch_list = []
	new_string = ""
	i = 0
	if string != None:
		while(i < len(string)):
			ascii_tojoin = []
			ascii_joined = ""
			if ord(string[i]) == 92:
				ascii_tojoin.append(string[i+1])
				ascii_tojoin.append(string[i+2])
				ascii_tojoin.append(string[i+3])
				ascii_joined = ascii_joined.join(ascii_tojoin)
				i = i+4
				ch_list.append(chr(int(ascii_joined)))
			else:
				ch_list.append(string[i])
				i = i+1
		return new_string.join(ch_list)
	else:
		return ""

def main():
	# Obsahuje Instruction class objekty
	instruction_list = []
	# Zasobnik pre hodnoty interpretovanych premennych
	data_stack = []
	
	# Slovnik premennych GF ramca
	GF_dict = {}
	# Slovnik premennych TF ramca
	TF_dict = {}
	# Pomocna premenna pre drzanie informacie o existencii TF ramca
	TF_created = 0
	# List obsahujuci ramce, ktore obsahuju LF premenne
	LF_list = []
	# Pomocna premenna pre drzanie informacie o existencii LF
	LF_created = 0
	#Slovnik pre vsetky navestidla format meno: pozicia
	LABEL_dict = {}
	# List kam sa uklada navratova hodnota po funkcii CALL
	position_stack = []

	opts, args = getopt.getopt(sys.argv[1:], "", ["help", "source="])

	xml_file = arg_check(opts)
	
	#Test ci vstupny subor splna XML formatovanie
	try:
		tree = ET.parse(xml_file)
	except:
		sys.stderr.write("Chyba: Zly XML format.\n")
		sys.exit(31)
		
	root = tree.getroot()
	

	if root.tag == 'program' and root.attrib['language'] == 'IPPcode18':
		last_order = 0
		for instruction in root: #prechadzame deti rootu
			#ak nazov tagu nie je instruction tak chyba
			if instruction.tag != 'instruction':
				sys.stderr.write("Chyba: Zly XML element.\n")
				sys.exit(32)
			
			# podla velkosti instruction zistujeme ci tagy deti splnaju nazvy argN kde N je 1-3
			if len(instruction) == 1:
				if instruction[0].tag != "arg1":
					sys.stderr.write("Chyba: Zly XML format\n")
					sys.exit(31)
			elif len(instruction) == 2:
				if instruction[0].tag != "arg1" or instruction[1].tag != "arg2":
					sys.stderr.write("Chyba: Zly XML format\n")
					sys.exit(31)
			elif len(instruction) == 3:
				if instruction[0].tag != "arg1" or instruction[1].tag != "arg2" or instruction[2].tag != "arg3":
					sys.stderr.write("Chyba: Zly XML format\n")
					sys.exit(31)
			# Vytvorenie objektu instukcie		
			temp = Instuction(instruction)
			#Ak poradie instukcii v XML subore nedava zmysel, tak je chyba
			if temp.order != None:
				if int(temp.order) <= last_order or int(temp.order) > last_order+1:
					sys.stderr.write("Chyba: Zly XML element\n")
					sys.exit(32)
				else:
					last_order = int(temp.order)
			else:
				sys.stderr.write("Chyba: Zly XML element\n")
				sys.exit(32)			
			
			if instruction_check(temp) != 1:
				sys.stderr.write("Chyba: Zly XML element\n")
				sys.exit(32)
				

			order_test = 4
			instruction_list.append(temp)
			
	else:
		sys.stderr.write("Chyba: Zly XML element alebo neznamy jazyk.\n")
		sys.exit(32)
		
	###### ZACIATOK INTERPRETACIE KODU ######
	
	position_counter = 0 #stale -1 oproti opcode
	
	
	# Potrebne prejst zoznam instrukcii a vyplnit slovnik navestidiel s menami a poziciami
	# Az potom interpretovanie kodu
	for current_instruction in instruction_list:
		if current_instruction.opcode.upper() == "LABEL":
			if current_instruction.arg1_value not in LABEL_dict:
				new_var = {current_instruction.arg1_value: current_instruction.order }
				LABEL_dict.update(new_var)
				#print(LABEL_dict)
			else:
				sys.stderr.write("Chyba: Pokus o redefinici navesti.\n")
				sys.exit(52)
			#print("LABEL OK")			
	
	
	while (position_counter < len(instruction_list)):
		current_instruction = instruction_list[position_counter]
		position_counter = position_counter+1
		#################################################
		if current_instruction.opcode.upper() == "DEFVAR":
			arg1 = parse_variable(current_instruction.arg1_value)
			if arg1[0] == "GF":
				if arg1[1] not in GF_dict:
					new_var = {arg1[1]: None }
					GF_dict.update(new_var)
					#print(GF_dict)
				else:
					sys.stderr.write("Chyba: Premenna uz existuje.\n")
					sys.exit(52)
			elif arg1[0] == "LF":
				if LF_created == 1:
					if len(LF_list) == 0:
						sys.stderr.write("Chyba: Ramec neexistuje.\n")
						sys.exit(55)						
					if arg1[1] not in LF_list[len(LF_list)-1]:
						new_var = {arg1[1]: None }
						LF_list[len(LF_list)-1].update(new_var)
						#print("LF_list:",LF_list)
						#print("LF_list_top:",LF_list[len(LF_list)-1])						
					else:
						sys.stderr.write("Chyba: Premenna uz existuje.\n")
						sys.exit(52)					
				else:
					sys.stderr.write("Chyba: Ramec neexistuje.\n")
					sys.exit(55)					
			elif arg1[0] == "TF":
				if TF_created == 1:					
					if arg1[1] not in TF_dict:
						new_var = {arg1[1]: None }
						TF_dict.update(new_var)
						#print("TF_dict: ",TF_dict)						
					else:
						sys.stderr.write("Chyba: Premenna uz existuje.\n")
						sys.exit(52)					
				else:
					sys.stderr.write("Chyba: Ramec neexistuje.\n")
					sys.exit(55)	
			#print("DEFVAR OK")
		################################################
		elif current_instruction.opcode.upper() == "MOVE":
			arg1 = parse_variable(current_instruction.arg1_value)
			if arg1[0] == "GF": ####################
				if arg1[1] not in GF_dict:
					sys.stderr.write("Chyba: Premenna neexistuje.\n")
					sys.exit(54)
				else:
					if current_instruction.arg2_type == "int" or current_instruction.arg2_type == "string" or current_instruction.arg2_type == "bool":
						if current_instruction.arg2_value == None:
							temp_var = IPPvariable(current_instruction.arg2_type, "")
							GF_dict[arg1[1]] = temp_var
							#print(GF_dict[arg1[1]].type, GF_dict[arg1[1]].value )							
						else:
							temp_var = IPPvariable(current_instruction.arg2_type, current_instruction.arg2_value)
							GF_dict[arg1[1]] = temp_var
							#print(GF_dict[arg1[1]].type, GF_dict[arg1[1]].value )
					elif current_instruction.arg2_type == "var":
						arg2 = parse_variable(current_instruction.arg2_value)
						if arg2[0] == "GF":
							if arg2[1] not in GF_dict:
								sys.stderr.write("Chyba: Premenna neexistuje. \n")
								sys.exit(54)
							else:
								if GF_dict[arg2[1]] == None:
									sys.stderr.write("Chyba: Premenna neinicializovana\n")
									sys.exit(56)
								else:
									temp_var = GF_dict[arg2[1]]
									GF_dict[arg1[1]] = temp_var
									#print(GF_dict[arg1[1]].type, GF_dict[arg1[1]].value, GF_dict[arg2[1]].type,GF_dict[arg2[1]].value)
						elif arg2[0] == "LF": ####################
							if LF_created == 1:
								if len(LF_list) == 0:
									sys.stderr.write("Chyba: Ramec neexistuje.\n")
									sys.exit(55)
								if arg2[1] not in LF_list[len(LF_list)-1]:
									sys.stderr.write("Chyba: Premenna neexistuje.\n")
									sys.exit(54)
								else:
									if LF_list[len(LF_list)-1][arg2[1]] == None:
										sys.stderr.write("Chyba: Premenna neinicializovana\n")
										sys.exit(56)
									else:
										temp_var = LF_list[len(LF_list)-1][arg2[1]]
										GF_dict[arg1[1]] = temp_var
							else:
								sys.stderr.write("Chyba: Ramec neexistuje.\n")
								sys.exit(55)								
						elif arg2[0] == "TF": ####################
							if TF_created == 1:
								if arg2[1] not in TF_dict:
									sys.stderr.write("Chyba: Premenna neexistuje.\n")
									sys.exit(54)
								else:
									if TF_dict[arg2[1]] == None:
										sys.stderr.write("Chyba: Premenna neinicializovana\n")
										sys.exit(56)
									else:
										temp_var = TF_dict[arg2[1]]
										GF_dict[arg1[1]] = temp_var
							else:
								sys.stderr.write("Chyba: Ramec neexistuje.\n")
								sys.exit(55)									
			elif arg1[0] == "LF": #####################
				if LF_created == 1:
					if len(LF_list) == 0:
						sys.stderr.write("Chyba: Ramec neexistuje.\n")
						sys.exit(55)						
					if arg1[1] not in LF_list[len(LF_list)-1]:
						sys.stderr.write("Chyba: Premenna neexistuje.\n")
						sys.exit(54)					
					else:
						if current_instruction.arg2_type == "int" or current_instruction.arg2_type == "string" or current_instruction.arg2_type == "bool":
							if current_instruction.arg2_value == None:
								temp_var = IPPvariable(current_instruction.arg2_type, "")
								LF_list[len(LF_list)-1][arg1[1]] = temp_var
								#print(LF_list[len(LF_list)-1][arg1[1]].type, LF_list[len(LF_list)-1][arg1[1]].value )							
							else:
								temp_var = IPPvariable(current_instruction.arg2_type, current_instruction.arg2_value)
								LF_list[len(LF_list)-1][arg1[1]] = temp_var
								#print(LF_list[len(LF_list)-1][arg1[1]].type, LF_list[len(LF_list)-1][arg1[1]].value )
						elif current_instruction.arg2_type == "var":
							arg2 = parse_variable(current_instruction.arg2_value)
							if arg2[0] == "GF": #############
								if arg2[1] not in GF_dict:
									sys.stderr.write("Chyba: Premenna neexistuje. \n")
									sys.exit(54)
								else:
									if GF_dict[arg2[1]] == None:
										sys.stderr.write("Chyba: Premenna neinicializovana\n")
										sys.exit(56)
									else:
										temp_var = GF_dict[arg2[1]]
										LF_list[len(LF_list)-1][arg1[1]] = temp_var
										#print(GF_dict[arg1[1]].type, GF_dict[arg1[1]].value, GF_dict[arg2[1]].type,GF_dict[arg2[1]].value)
							elif arg2[0] == "LF": ####################
								if LF_created == 1:
									if len(LF_list) == 0:
										sys.stderr.write("Chyba: Ramec neexistuje.\n")
										sys.exit(55)
									if arg2[1] not in LF_list[len(LF_list)-1]:
										sys.stderr.write("Chyba: Premenna neexistuje.\n")
										sys.exit(54)
									else:
										if LF_list[len(LF_list)-1][arg2[1]] == None:
											sys.stderr.write("Chyba: Premenna neinicializovana\n")
											sys.exit(56)
										else:
											temp_var = LF_list[len(LF_list)-1][arg2[1]]
											LF_list[len(LF_list)-1][arg1[1]] = temp_var
											#print(GF_dict[arg1[1]].type, GF_dict[arg1[1]].value, GF_dict[arg2[1]].type,GF_dict[arg2[1]].value)	
							elif arg2[0] == "TF": #############
								if arg2[1] not in TF_dict:
									sys.stderr.write("Chyba: Premenna neexistuje. \n")
									sys.exit(54)
								else:
									if GF_dict[arg2[1]] == None:
										sys.stderr.write("Chyba: Premenna neinicializovana\n")
										sys.exit(56)
									else:
										temp_var = TF_dict[arg2[1]]
										LF_list[len(LF_list)-1][arg1[1]] = temp_var
										#print(GF_dict[arg1[1]].type, GF_dict[arg1[1]].value, GF_dict[arg2[1]].type,GF_dict[arg2[1]].value)	
				else:
					sys.stderr.write("Chyba: Ramec neexistuje.\n")
					sys.exit(55)	
			elif arg1[0] == "TF": ################################
				if TF_created == 1:
					if arg1[1] not in TF_dict:
						sys.stderr.write("Chyba: Premenna neexistuje.\n")
						sys.exit(54)
					else:
						if current_instruction.arg2_type == "int" or current_instruction.arg2_type == "string" or current_instruction.arg2_type == "bool":
							if current_instruction.arg2_value == None:
								temp_var = IPPvariable(current_instruction.arg2_type, "")
								TF_dict[arg1[1]] = temp_var
								#print(TF_dict[arg1[1]].type, TF_dict[arg1[1]].value )							
							else:
								temp_var = IPPvariable(current_instruction.arg2_type, current_instruction.arg2_value)
								TF_dict[arg1[1]] = temp_var
								#print(TF_dict[arg1[1]].type, TF_dict[arg1[1]].value )
						elif current_instruction.arg2_type == "var":
							arg2 = parse_variable(current_instruction.arg2_value)
							if arg2[0] == "GF":
								if arg2[1] not in GF_dict:
									sys.stderr.write("Chyba: Premenna neexistuje. \n")
									sys.exit(54)
								else:
									if GF_dict[arg2[1]] == None:
										sys.stderr.write("Chyba: Premenna neinicializovana\n")
										sys.exit(56)
									else:
										temp_var = GF_dict[arg2[1]]
										TF_dict[arg1[1]] = temp_var
										#print(TF_dict[arg1[1]].type, TF_dict[arg1[1]].value, GF_dict[arg2[1]].type,GF_dict[arg2[1]].value)				
							elif arg2[0] == "LF": ####################
								if LF_created == 1:
									if len(LF_list) == 0:
										sys.stderr.write("Chyba: Ramec neexistuje.\n")
										sys.exit(55)
									if arg2[1] not in LF_list[len(LF_list)-1]:
										sys.stderr.write("Chyba: Premenna neexistuje.\n")
										sys.exit(54)
									else:
										if LF_list[len(LF_list)-1][arg2[1]] == None:
											sys.stderr.write("Chyba: Premenna neinicializovana\n")
											sys.exit(56)
										else:
											temp_var = LF_list[len(LF_list)-1][arg2[1]]
											TF_dict[arg1[1]][arg1[1]] = temp_var
								else:
									sys.stderr.write("Chyba: Ramec neexistuje.\n")
									sys.exit(55)								
							elif arg2[0] == "TF": ####################
								if TF_created == 1:
									if arg2[1] not in TF_dict:
										sys.stderr.write("Chyba: Premenna neexistuje.\n")
										sys.exit(54)
									else:
										if TF_dict[arg2[1]] == None:
											sys.stderr.write("Chyba: Premenna neinicializovana\n")
											sys.exit(56)
										else:
											temp_var = TF_dict[arg2[1]]
											TF_dict[arg1[1]][arg1[1]] = temp_var
								else:
									sys.stderr.write("Chyba: Ramec neexistuje.\n")
									sys.exit(55)	
									
				else:
					sys.stderr.write("Chyba: Ramec neexistuje.\n")
					sys.exit(55)	
			#print("MOVE OK")
		###############################################
		elif current_instruction.opcode.upper() == "ADD":
			arg1 = parse_variable(current_instruction.arg1_value)
			if arg1[0] == "GF":
				if arg1[1] not in GF_dict:
					sys.stderr.write("Chyba: Premenna neexistuje.\n")
					sys.exit(54)
				else:
					if current_instruction.arg2_type == "int" and current_instruction.arg3_type == "int":
						temp_value = int(current_instruction.arg2_value) + int(current_instruction.arg3_value)
						temp_var = IPPvariable("int", temp_value)
						GF_dict[arg1[1]] = temp_var
						#print(GF_dict[arg1[1]].type, GF_dict[arg1[1]].value )
						
					elif current_instruction.arg2_type == "var" and current_instruction.arg3_type == "int":
						arg2 = parse_variable(current_instruction.arg2_value)
						if arg2[0] == "GF":
							if arg2[1] not in GF_dict:
								sys.stderr.write("Chyba: Premenna neexistuje. \n")
								sys.exit(54)
							else:
								if GF_dict[arg2[1]] == None:
									sys.stderr.write("Chyba: Premenna neinicializovana\n")
									sys.exit(56)
								else:
									if GF_dict[arg2[1]].type != "int":
										sys.stderr.write("Chyba: Zly typ premennej\n")
										sys.exit(53)
									else:
										temp_value = int(GF_dict[arg2[1]].value) + int(current_instruction.arg3_value)
										temp_var = IPPvariable("int", temp_value)
										GF_dict[arg1[1]] = temp_var
										#print(GF_dict[arg1[1]].type, GF_dict[arg1[1]].value )
						elif arg2[0] == "LF": ####################
							if LF_created == 1:
								if len(LF_list) == 0:
									sys.stderr.write("Chyba: Ramec neexistuje.\n")
									sys.exit(55)
								if arg2[1] not in LF_list[len(LF_list)-1]:
									sys.stderr.write("Chyba: Premenna neexistuje.\n")
									sys.exit(54)
								else:
									if LF_list[len(LF_list)-1][arg2[1]] == None:
										sys.stderr.write("Chyba: Premenna neinicializovana\n")
										sys.exit(56)
									else:
										if LF_list[len(LF_list)-1][arg2[1]].type != "int":
											sys.stderr.write("Chyba: Zly typ premennej\n")
											sys.exit(53)
										else:
											temp_value = int(LF_list[len(LF_list)-1][arg2[1]].value) + int(current_instruction.arg3_value)
											temp_var = IPPvariable("int", temp_value)
											GF_dict[arg1[1]] = temp_var
											#print(GF_dict[arg1[1]].type, GF_dict[arg1[1]].value )
							else:
								sys.stderr.write("Chyba: Ramec neexistuje.\n")
								sys.exit(55)								
						elif arg2[0] == "TF": ####################
							if TF_created == 1:
								if arg2[1] not in TF_dict:
									sys.stderr.write("Chyba: Premenna neexistuje.\n")
									sys.exit(54)
								else:
									if TF_dict[arg2[1]] == None:
										sys.stderr.write("Chyba: Premenna neinicializovana\n")
										sys.exit(56)
									else:
										if TF_dict[arg2[1]].type != "int":
											sys.stderr.write("Chyba: Zly typ premennej\n")
											sys.exit(53)
										else:
											temp_value = int(TF_dict[arg2[1]].value) + int(current_instruction.arg3_value)
											temp_var = IPPvariable("int", temp_value)
											GF_dict[arg1[1]] = temp_var
											#print(GF_dict[arg1[1]].type, GF_dict[arg1[1]].value )
							else:
								sys.stderr.write("Chyba: Ramec neexistuje.\n")
								sys.exit(55)
										
					elif current_instruction.arg2_type == "int" and current_instruction.arg3_type == "var":
						arg2 = parse_variable(current_instruction.arg3_value)
						if arg2[0] == "GF":
							if arg2[1] not in GF_dict:
								sys.stderr.write("Chyba: Premenna neexistuje. \n")
								sys.exit(54)
							else:
								if GF_dict[arg2[1]] == None:
									sys.stderr.write("Chyba: Premenna neinicializovana\n")
									sys.exit(56)
								else:
									if GF_dict[arg2[1]].type != "int":
										sys.stderr.write("Chyba: Zly typ premennej\n")
										sys.exit(53)
									else:
										temp_value = int(GF_dict[arg2[1]].value) + int(current_instruction.arg2_value)
										temp_var = IPPvariable("int", temp_value)
										GF_dict[arg1[1]] = temp_var
										#print(GF_dict[arg1[1]].type, GF_dict[arg1[1]].value )
						elif arg2[0] == "LF": ####################
							if LF_created == 1:
								if len(LF_list) == 0:
									sys.stderr.write("Chyba: Ramec neexistuje.\n")
									sys.exit(55)
								if arg2[1] not in LF_list[len(LF_list)-1]:
									sys.stderr.write("Chyba: Premenna neexistuje.\n")
									sys.exit(54)
								else:
									if LF_list[len(LF_list)-1][arg2[1]] == None:
										sys.stderr.write("Chyba: Premenna neinicializovana\n")
										sys.exit(56)
									else:
										if LF_list[len(LF_list)-1][arg2[1]].type != "int":
											sys.stderr.write("Chyba: Zly typ premennej\n")
											sys.exit(53)
										else:
											temp_value = int(LF_list[len(LF_list)-1][arg2[1]].value) + int(current_instruction.arg2_value)
											temp_var = IPPvariable("int", temp_value)
											GF_dict[arg1[1]] = temp_var
											#print(GF_dict[arg1[1]].type, GF_dict[arg1[1]].value )
							else:
								sys.stderr.write("Chyba: Ramec neexistuje.\n")
								sys.exit(55)								
						elif arg2[0] == "TF": ####################
							if TF_created == 1:
								if arg2[1] not in TF_dict:
									sys.stderr.write("Chyba: Premenna neexistuje.\n")
									sys.exit(54)
								else:
									if TF_dict[arg2[1]] == None:
										sys.stderr.write("Chyba: Premenna neinicializovana\n")
										sys.exit(56)
									else:
										if TF_dict[arg2[1]].type != "int":
											sys.stderr.write("Chyba: Zly typ premennej\n")
											sys.exit(53)
										else:
											temp_value = int(TF_dict[arg2[1]].value) + int(current_instruction.arg2_value)
											temp_var = IPPvariable("int", temp_value)
											GF_dict[arg1[1]] = temp_var
											#print(GF_dict[arg1[1]].type, GF_dict[arg1[1]].value )
							else:
								sys.stderr.write("Chyba: Ramec neexistuje.\n")
								sys.exit(55)
										
					elif current_instruction.arg2_type == "var" and current_instruction.arg3_type == "var":
						arg2 = parse_variable(current_instruction.arg2_value)
						arg3 = parse_variable(current_instruction.arg3_value)
						if arg2[0] == "GF":
							if arg2[1] not in GF_dict:
								sys.stderr.write("Chyba: Premenna neexistuje. \n")
								sys.exit(54)
							else:
								if GF_dict[arg2[1]] == None:
									sys.stderr.write("Chyba: Premenna neinicializovana\n")
									sys.exit(56)
								else:
									if GF_dict[arg2[1]].type != "int":
										sys.stderr.write("Chyba: Zly typ premennej\n")
										sys.exit(53)
									else:
										###
										if arg3[0] == "GF":
											if arg3[1] not in GF_dict:
												sys.stderr.write("Chyba: Premenna neexistuje. \n")
												sys.exit(54)
											else:
												if GF_dict[arg3[1]] == None:
													sys.stderr.write("Chyba: Premenna neinicializovana\n")
													sys.exit(56)
												else:
													if GF_dict[arg3[1]].type != "int":
														sys.stderr.write("Chyba: Zly typ premennej\n")
														sys.exit(53)
													else:
														temp_value = int(GF_dict[arg2[1]].value) + int(GF_dict[arg3[1]].value)
														temp_var = IPPvariable("int", temp_value)
														GF_dict[arg1[1]] = temp_var
														#print(GF_dict[arg1[1]].type, GF_dict[arg1[1]].value )
##
										elif arg3[0] == "LF": ####################
											if LF_created == 1:
												if len(LF_list) == 0:
													sys.stderr.write("Chyba: Ramec neexistuje.\n")
													sys.exit(55)
												if arg3[1] not in LF_list[len(LF_list)-1]:
													sys.stderr.write("Chyba: Premenna neexistuje.\n")
													sys.exit(54)
												else:
													if LF_list[len(LF_list)-1][arg3[1]] == None:
														sys.stderr.write("Chyba: Premenna neinicializovana\n")
														sys.exit(56)
													else:
														if LF_list[len(LF_list)-1][arg3[1]].type != "int":
															sys.stderr.write("Chyba: Zly typ premennej\n")
															sys.exit(53)
														else:
															temp_value = int(GF_dict[arg2[1]].value) + int(LF_list[len(LF_list)-1][arg3[1]].value)
															temp_var = IPPvariable("int", temp_value)
															GF_dict[arg1[1]] = temp_var
															#print(GF_dict[arg1[1]].type, GF_dict[arg1[1]].value )
											else:
												sys.stderr.write("Chyba: Ramec neexistuje.\n")
												sys.exit(55)								
										elif arg3[0] == "TF": ####################
											if TF_created == 1:
												if arg3[1] not in TF_dict:
													sys.stderr.write("Chyba: Premenna neexistuje.\n")
													sys.exit(54)
												else:
													if TF_dict[arg3[1]] == None:
														sys.stderr.write("Chyba: Premenna neinicializovana\n")
														sys.exit(56)
													else:
														if TF_dict[arg3[1]].type != "int":
															sys.stderr.write("Chyba: Zly typ premennej\n")
															sys.exit(53)
														else:
															temp_value = int(GF_dict[arg2[1]].value) + int(TF_dict[arg3[1]].value)
															temp_var = IPPvariable("int", temp_value)
															GF_dict[arg1[1]] = temp_var
															#print(GF_dict[arg1[1]].type, GF_dict[arg1[1]].value )
											else:
												sys.stderr.write("Chyba: Ramec neexistuje.\n")
												sys.exit(55)
						elif arg2[0] == "LF": ####################
							if LF_created == 1:
								if len(LF_list) == 0:
									sys.stderr.write("Chyba: Ramec neexistuje.\n")
									sys.exit(55)
								if arg2[1] not in LF_list[len(LF_list)-1]:
									sys.stderr.write("Chyba: Premenna neexistuje.\n")
									sys.exit(54)
								else:
									if LF_list[len(LF_list)-1][arg2[1]] == None:
										sys.stderr.write("Chyba: Premenna neinicializovana\n")
										sys.exit(56)
									else:
										if LF_list[len(LF_list)-1][arg2[1]].type != "int":
											sys.stderr.write("Chyba: Zly typ premennej\n")
											sys.exit(53)
										else:
											if arg3[0] == "GF":
												if arg3[1] not in GF_dict:
													sys.stderr.write("Chyba: Premenna neexistuje. \n")
													sys.exit(54)
												else:
													if GF_dict[arg3[1]] == None:
														sys.stderr.write("Chyba: Premenna neinicializovana\n")
														sys.exit(56)
													else:
														if GF_dict[arg3[1]].type != "int":
															sys.stderr.write("Chyba: Zly typ premennej\n")
															sys.exit(53)
														else:
															temp_value = int(LF_list[len(LF_list)-1][arg2[1]].value) + int(GF_dict[arg3[1]].value)
															temp_var = IPPvariable("int", temp_value)
															GF_dict[arg1[1]] = temp_var
															#print(GF_dict[arg1[1]].type, GF_dict[arg1[1]].value )
	##
											elif arg3[0] == "LF": ####################
												if LF_created == 1:
													if len(LF_list) == 0:
														sys.stderr.write("Chyba: Ramec neexistuje.\n")
														sys.exit(55)
													if arg3[1] not in LF_list[len(LF_list)-1]:
														sys.stderr.write("Chyba: Premenna neexistuje.\n")
														sys.exit(54)
													else:
														if LF_list[len(LF_list)-1][arg3[1]] == None:
															sys.stderr.write("Chyba: Premenna neinicializovana\n")
															sys.exit(56)
														else:
															if LF_list[len(LF_list)-1][arg3[1]].type != "int":
																sys.stderr.write("Chyba: Zly typ premennej\n")
																sys.exit(53)
															else:
																temp_value = int(LF_list[len(LF_list)-1][arg2[1]].value) + int(LF_list[len(LF_list)-1][arg3[1]].value)
																temp_var = IPPvariable("int", temp_value)
																GF_dict[arg1[1]] = temp_var
																#print(GF_dict[arg1[1]].type, GF_dict[arg1[1]].value )
												else:
													sys.stderr.write("Chyba: Ramec neexistuje.\n")
													sys.exit(55)								
											elif arg3[0] == "TF": ####################
												if TF_created == 1:
													if arg3[1] not in TF_dict:
														sys.stderr.write("Chyba: Premenna neexistuje.\n")
														sys.exit(54)
													else:
														if TF_dict[arg3[1]] == None:
															sys.stderr.write("Chyba: Premenna neinicializovana\n")
															sys.exit(56)
														else:
															if TF_dict[arg3[1]].type != "int":
																sys.stderr.write("Chyba: Zly typ premennej\n")
																sys.exit(53)
															else:
																temp_value = int(LF_list[len(LF_list)-1][arg2[1]].value) + int(TF_dict[arg3[1]].value)
																temp_var = IPPvariable("int", temp_value)
																GF_dict[arg1[1]] = temp_var
																#print(GF_dict[arg1[1]].type, GF_dict[arg1[1]].value )
												else:
													sys.stderr.write("Chyba: Ramec neexistuje.\n")
													sys.exit(55)
							else:
								sys.stderr.write("Chyba: Ramec neexistuje.\n")
								sys.exit(55)								
						elif arg2[0] == "TF": ####################
							if TF_created == 1:
								if arg2[1] not in TF_dict:
									sys.stderr.write("Chyba: Premenna neexistuje.\n")
									sys.exit(54)
								else:
									if TF_dict[arg2[1]] == None:
										sys.stderr.write("Chyba: Premenna neinicializovana\n")
										sys.exit(56)
									else:
										if TF_dict[arg2[1]].type != "int":
											sys.stderr.write("Chyba: Zly typ premennej\n")
											sys.exit(53)
										else:
											if arg3[0] == "GF":
												if arg3[1] not in GF_dict:
													sys.stderr.write("Chyba: Premenna neexistuje. \n")
													sys.exit(54)
												else:
													if GF_dict[arg3[1]] == None:
														sys.stderr.write("Chyba: Premenna neinicializovana\n")
														sys.exit(56)
													else:
														if GF_dict[arg3[1]].type != "int":
															sys.stderr.write("Chyba: Zly typ premennej\n")
															sys.exit(53)
														else:
															temp_value = int(TF_dict[arg2[1]].value) + int(GF_dict[arg3[1]].value)
															temp_var = IPPvariable("int", temp_value)
															GF_dict[arg1[1]] = temp_var
															#print(GF_dict[arg1[1]].type, GF_dict[arg1[1]].value )
	##
											elif arg3[0] == "LF": ####################
												if LF_created == 1:
													if len(LF_list) == 0:
														sys.stderr.write("Chyba: Ramec neexistuje.\n")
														sys.exit(55)
													if arg3[1] not in LF_list[len(LF_list)-1]:
														sys.stderr.write("Chyba: Premenna neexistuje.\n")
														sys.exit(54)
													else:
														if LF_list[len(LF_list)-1][arg3[1]] == None:
															sys.stderr.write("Chyba: Premenna neinicializovana\n")
															sys.exit(56)
														else:
															if LF_list[len(LF_list)-1][arg3[1]].type != "int":
																sys.stderr.write("Chyba: Zly typ premennej\n")
																sys.exit(53)
															else:
																temp_value = int(TF_dict[arg2[1]].value) + int(LF_list[len(LF_list)-1][arg3[1]].value)
																temp_var = IPPvariable("int", temp_value)
																GF_dict[arg1[1]] = temp_var
																#print(GF_dict[arg1[1]].type, GF_dict[arg1[1]].value )
												else:
													sys.stderr.write("Chyba: Ramec neexistuje.\n")
													sys.exit(55)								
											elif arg3[0] == "TF": ####################
												if TF_created == 1:
													if arg3[1] not in TF_dict:
														sys.stderr.write("Chyba: Premenna neexistuje.\n")
														sys.exit(54)
													else:
														if TF_dict[arg3[1]] == None:
															sys.stderr.write("Chyba: Premenna neinicializovana\n")
															sys.exit(56)
														else:
															if TF_dict[arg3[1]].type != "int":
																sys.stderr.write("Chyba: Zly typ premennej\n")
																sys.exit(53)
															else:
																temp_value = int(TF_dict[arg2[1]].value) + int(TF_dict[arg3[1]].value)
																temp_var = IPPvariable("int", temp_value)
																GF_dict[arg1[1]] = temp_var
																#print(GF_dict[arg1[1]].type, GF_dict[arg1[1]].value )
												else:
													sys.stderr.write("Chyba: Ramec neexistuje.\n")
													sys.exit(55)
							else:
								sys.stderr.write("Chyba: Ramec neexistuje.\n")
								sys.exit(55)														
					else:
						sys.stderr.write("Chyba: Zly typ premennej \n")
						sys.exit(53)
			elif arg1[0] == "LF": #####################
				if LF_created == 1:
					if len(LF_list) == 0:
						sys.stderr.write("Chyba: Ramec neexistuje.\n")
						sys.exit(55)						
					if arg1[1] not in LF_list[len(LF_list)-1]:
						sys.stderr.write("Chyba: Premenna neexistuje.\n")
						sys.exit(54)					
					else:
						if current_instruction.arg2_type == "int" and current_instruction.arg3_type == "int":
							temp_value = int(current_instruction.arg2_value) + int(current_instruction.arg3_value)
							temp_var = IPPvariable("int", temp_value)
							LF_list[len(LF_list)-1][arg1[1]] = temp_var
							#print(LF_list[len(LF_list)-1][arg1[1]].type, LF_list[len(LF_list)-1][arg1[1]].value )
							
						elif current_instruction.arg2_type == "var" and current_instruction.arg3_type == "int":
							arg2 = parse_variable(current_instruction.arg2_value)
							if arg2[0] == "GF":
								if arg2[1] not in GF_dict:
									sys.stderr.write("Chyba: Premenna neexistuje. \n")
									sys.exit(54)
								else:
									if GF_dict[arg2[1]] == None:
										sys.stderr.write("Chyba: Premenna neinicializovana\n")
										sys.exit(56)
									else:
										if GF_dict[arg2[1]].type != "int":
											sys.stderr.write("Chyba: Zly typ premennej\n")
											sys.exit(53)
										else:
											temp_value = int(GF_dict[arg2[1]].value) + int(current_instruction.arg3_value)
											temp_var = IPPvariable("int", temp_value)
											LF_list[len(LF_list)-1][arg1[1]] = temp_var
											#print(LF_list[len(LF_list)-1][arg1[1]].type, LF_list[len(LF_list)-1][arg1[1]].value )
							elif arg2[0] == "LF": ####################
								if LF_created == 1:
									if len(LF_list) == 0:
										sys.stderr.write("Chyba: Ramec neexistuje.\n")
										sys.exit(55)
									if arg2[1] not in LF_list[len(LF_list)-1]:
										sys.stderr.write("Chyba: Premenna neexistuje.\n")
										sys.exit(54)
									else:
										if LF_list[len(LF_list)-1][arg2[1]] == None:
											sys.stderr.write("Chyba: Premenna neinicializovana\n")
											sys.exit(56)
										else:
											if LF_list[len(LF_list)-1][arg2[1]].type != "int":
												sys.stderr.write("Chyba: Zly typ premennej\n")
												sys.exit(53)
											else:
												temp_value = int(LF_list[len(LF_list)-1][arg2[1]].value) + int(current_instruction.arg3_value)
												temp_var = IPPvariable("int", temp_value)
												LF_list[len(LF_list)-1][arg1[1]] = temp_var
												#print(LF_list[len(LF_list)-1][arg1[1]].type, LF_list[len(LF_list)-1][arg1[1]].value )
								else:
									sys.stderr.write("Chyba: Ramec neexistuje.\n")
									sys.exit(55)								
							elif arg2[0] == "TF": ####################
								if TF_created == 1:
									if arg2[1] not in TF_dict:
										sys.stderr.write("Chyba: Premenna neexistuje.\n")
										sys.exit(54)
									else:
										if TF_dict[arg2[1]] == None:
											sys.stderr.write("Chyba: Premenna neinicializovana\n")
											sys.exit(56)
										else:
											if TF_dict[arg2[1]].type != "int":
												sys.stderr.write("Chyba: Zly typ premennej\n")
												sys.exit(53)
											else:
												temp_value = int(TF_dict[arg2[1]].value) + int(current_instruction.arg3_value)
												temp_var = IPPvariable("int", temp_value)
												LF_list[len(LF_list)-1][arg1[1]] = temp_var
												#print(LF_list[len(LF_list)-1][arg1[1]].type, LF_list[len(LF_list)-1][arg1[1]].value )
								else:
									sys.stderr.write("Chyba: Ramec neexistuje.\n")
									sys.exit(55)
											
						elif current_instruction.arg2_type == "int" and current_instruction.arg3_type == "var":
							arg2 = parse_variable(current_instruction.arg3_value)
							if arg2[0] == "GF":
								if arg2[1] not in GF_dict:
									sys.stderr.write("Chyba: Premenna neexistuje. \n")
									sys.exit(54)
								else:
									if GF_dict[arg2[1]] == None:
										sys.stderr.write("Chyba: Premenna neinicializovana\n")
										sys.exit(56)
									else:
										if GF_dict[arg2[1]].type != "int":
											sys.stderr.write("Chyba: Zly typ premennej\n")
											sys.exit(53)
										else:
											temp_value = int(GF_dict[arg2[1]].value) + int(current_instruction.arg2_value)
											temp_var = IPPvariable("int", temp_value)
											LF_list[len(LF_list)-1][arg1[1]] = temp_var
											#print(LF_list[len(LF_list)-1][arg1[1]].type, LF_list[len(LF_list)-1][arg1[1]].value )
							elif arg2[0] == "LF": ####################
								if LF_created == 1:
									if len(LF_list) == 0:
										sys.stderr.write("Chyba: Ramec neexistuje.\n")
										sys.exit(55)
									if arg2[1] not in LF_list[len(LF_list)-1]:
										sys.stderr.write("Chyba: Premenna neexistuje.\n")
										sys.exit(54)
									else:
										if LF_list[len(LF_list)-1][arg2[1]] == None:
											sys.stderr.write("Chyba: Premenna neinicializovana\n")
											sys.exit(56)
										else:
											if LF_list[len(LF_list)-1][arg2[1]].type != "int":
												sys.stderr.write("Chyba: Zly typ premennej\n")
												sys.exit(53)
											else:
												temp_value = int(LF_list[len(LF_list)-1][arg2[1]].value) + int(current_instruction.arg2_value)
												temp_var = IPPvariable("int", temp_value)
												LF_list[len(LF_list)-1][arg1[1]] = temp_var
												#print(LF_list[len(LF_list)-1][arg1[1]].type, LF_list[len(LF_list)-1][arg1[1]].value )
								else:
									sys.stderr.write("Chyba: Ramec neexistuje.\n")
									sys.exit(55)								
							elif arg2[0] == "TF": ####################
								if TF_created == 1:
									if arg2[1] not in TF_dict:
										sys.stderr.write("Chyba: Premenna neexistuje.\n")
										sys.exit(54)
									else:
										if TF_dict[arg2[1]] == None:
											sys.stderr.write("Chyba: Premenna neinicializovana\n")
											sys.exit(56)
										else:
											if TF_dict[arg2[1]].type != "int":
												sys.stderr.write("Chyba: Zly typ premennej\n")
												sys.exit(53)
											else:
												temp_value = int(TF_dict[arg2[1]].value) + int(current_instruction.arg2_value)
												temp_var = IPPvariable("int", temp_value)
												LF_list[len(LF_list)-1][arg1[1]] = temp_var
												#print(LF_list[len(LF_list)-1][arg1[1]].type, LF_list[len(LF_list)-1][arg1[1]].value )
								else:
									sys.stderr.write("Chyba: Ramec neexistuje.\n")
									sys.exit(55)
											
						elif current_instruction.arg2_type == "var" and current_instruction.arg3_type == "var":
							arg2 = parse_variable(current_instruction.arg2_value)
							arg3 = parse_variable(current_instruction.arg3_value)
							if arg2[0] == "GF":
								if arg2[1] not in GF_dict:
									sys.stderr.write("Chyba: Premenna neexistuje. \n")
									sys.exit(54)
								else:
									if GF_dict[arg2[1]] == None:
										sys.stderr.write("Chyba: Premenna neinicializovana\n")
										sys.exit(56)
									else:
										if GF_dict[arg2[1]].type != "int":
											sys.stderr.write("Chyba: Zly typ premennej\n")
											sys.exit(53)
										else:
											###
											if arg3[0] == "GF":
												if arg3[1] not in GF_dict:
													sys.stderr.write("Chyba: Premenna neexistuje. \n")
													sys.exit(54)
												else:
													if GF_dict[arg3[1]] == None:
														sys.stderr.write("Chyba: Premenna neinicializovana\n")
														sys.exit(56)
													else:
														if GF_dict[arg3[1]].type != "int":
															sys.stderr.write("Chyba: Zly typ premennej\n")
															sys.exit(53)
														else:
															temp_value = int(GF_dict[arg2[1]].value) + int(GF_dict[arg3[1]].value)
															temp_var = IPPvariable("int", temp_value)
															LF_list[len(LF_list)-1][arg1[1]] = temp_var
															#print(LF_list[len(LF_list)-1][arg1[1]].type, LF_list[len(LF_list)-1][arg1[1]].value )
	##
											elif arg3[0] == "LF": ####################
												if LF_created == 1:
													if len(LF_list) == 0:
														sys.stderr.write("Chyba: Ramec neexistuje.\n")
														sys.exit(55)
													if arg3[1] not in LF_list[len(LF_list)-1]:
														sys.stderr.write("Chyba: Premenna neexistuje.\n")
														sys.exit(54)
													else:
														if LF_list[len(LF_list)-1][arg3[1]] == None:
															sys.stderr.write("Chyba: Premenna neinicializovana\n")
															sys.exit(56)
														else:
															if LF_list[len(LF_list)-1][arg3[1]].type != "int":
																sys.stderr.write("Chyba: Zly typ premennej\n")
																sys.exit(53)
															else:
																temp_value = int(GF_dict[arg2[1]].value) + int(LF_list[len(LF_list)-1][arg3[1]].value)
																temp_var = IPPvariable("int", temp_value)
																LF_list[len(LF_list)-1][arg1[1]] = temp_var
																#print(LF_list[len(LF_list)-1][arg1[1]].type, LF_list[len(LF_list)-1][arg1[1]].value )
												else:
													sys.stderr.write("Chyba: Ramec neexistuje.\n")
													sys.exit(55)								
											elif arg3[0] == "TF": ####################
												if TF_created == 1:
													if arg3[1] not in TF_dict:
														sys.stderr.write("Chyba: Premenna neexistuje.\n")
														sys.exit(54)
													else:
														if TF_dict[arg3[1]] == None:
															sys.stderr.write("Chyba: Premenna neinicializovana\n")
															sys.exit(56)
														else:
															if TF_dict[arg3[1]].type != "int":
																sys.stderr.write("Chyba: Zly typ premennej\n")
																sys.exit(53)
															else:
																temp_value = int(GF_dict[arg2[1]].value) + int(TF_dict[arg3[1]].value)
																temp_var = IPPvariable("int", temp_value)
																LF_list[len(LF_list)-1][arg1[1]] = temp_var
																#print(LF_list[len(LF_list)-1][arg1[1]].type, LF_list[len(LF_list)-1][arg1[1]].value )
												else:
													sys.stderr.write("Chyba: Ramec neexistuje.\n")
													sys.exit(55)
							elif arg2[0] == "LF": ####################
								if LF_created == 1:
									if len(LF_list) == 0:
										sys.stderr.write("Chyba: Ramec neexistuje.\n")
										sys.exit(55)
									if arg2[1] not in LF_list[len(LF_list)-1]:
										sys.stderr.write("Chyba: Premenna neexistuje.\n")
										sys.exit(54)
									else:
										if LF_list[len(LF_list)-1][arg2[1]] == None:
											sys.stderr.write("Chyba: Premenna neinicializovana\n")
											sys.exit(56)
										else:
											if LF_list[len(LF_list)-1][arg2[1]].type != "int":
												sys.stderr.write("Chyba: Zly typ premennej\n")
												sys.exit(53)
											else:
												if arg3[0] == "GF":
													if arg3[1] not in GF_dict:
														sys.stderr.write("Chyba: Premenna neexistuje. \n")
														sys.exit(54)
													else:
														if GF_dict[arg3[1]] == None:
															sys.stderr.write("Chyba: Premenna neinicializovana\n")
															sys.exit(56)
														else:
															if GF_dict[arg3[1]].type != "int":
																sys.stderr.write("Chyba: Zly typ premennej\n")
																sys.exit(53)
															else:
																temp_value = int(LF_list[len(LF_list)-1][arg2[1]].value) + int(GF_dict[arg3[1]].value)
																temp_var = IPPvariable("int", temp_value)
																LF_list[len(LF_list)-1][arg1[1]] = temp_var
																#print(LF_list[len(LF_list)-1][arg1[1]].type, LF_list[len(LF_list)-1][arg1[1]].value )
		##
												elif arg3[0] == "LF": ####################
													if LF_created == 1:
														if len(LF_list) == 0:
															sys.stderr.write("Chyba: Ramec neexistuje.\n")
															sys.exit(55)
														if arg3[1] not in LF_list[len(LF_list)-1]:
															sys.stderr.write("Chyba: Premenna neexistuje.\n")
															sys.exit(54)
														else:
															if LF_list[len(LF_list)-1][arg3[1]] == None:
																sys.stderr.write("Chyba: Premenna neinicializovana\n")
																sys.exit(56)
															else:
																if LF_list[len(LF_list)-1][arg3[1]].type != "int":
																	sys.stderr.write("Chyba: Zly typ premennej\n")
																	sys.exit(53)
																else:
																	temp_value = int(LF_list[len(LF_list)-1][arg2[1]].value) + int(LF_list[len(LF_list)-1][arg3[1]].value)
																	temp_var = IPPvariable("int", temp_value)
																	LF_list[len(LF_list)-1][arg1[1]] = temp_var
																	#print(LF_list[len(LF_list)-1][arg1[1]].type, LF_list[len(LF_list)-1][arg1[1]].value )
													else:
														sys.stderr.write("Chyba: Ramec neexistuje.\n")
														sys.exit(55)								
												elif arg3[0] == "TF": ####################
													if TF_created == 1:
														if arg3[1] not in TF_dict:
															sys.stderr.write("Chyba: Premenna neexistuje.\n")
															sys.exit(54)
														else:
															if TF_dict[arg3[1]] == None:
																sys.stderr.write("Chyba: Premenna neinicializovana\n")
																sys.exit(56)
															else:
																if TF_dict[arg3[1]].type != "int":
																	sys.stderr.write("Chyba: Zly typ premennej\n")
																	sys.exit(53)
																else:
																	temp_value = int(LF_list[len(LF_list)-1][arg2[1]].value) + int(TF_dict[arg3[1]].value)
																	temp_var = IPPvariable("int", temp_value)
																	LF_list[len(LF_list)-1][arg1[1]] = temp_var
																	#print(LF_list[len(LF_list)-1][arg1[1]].type, LF_list[len(LF_list)-1][arg1[1]].value )
													else:
														sys.stderr.write("Chyba: Ramec neexistuje.\n")
														sys.exit(55)
								else:
									sys.stderr.write("Chyba: Ramec neexistuje.\n")
									sys.exit(55)								
							elif arg2[0] == "TF": ####################
								if TF_created == 1:
									if arg2[1] not in TF_dict:
										sys.stderr.write("Chyba: Premenna neexistuje.\n")
										sys.exit(54)
									else:
										if TF_dict[arg2[1]] == None:
											sys.stderr.write("Chyba: Premenna neinicializovana\n")
											sys.exit(56)
										else:
											if TF_dict[arg2[1]].type != "int":
												sys.stderr.write("Chyba: Zly typ premennej\n")
												sys.exit(53)
											else:
												if arg3[0] == "GF":
													if arg3[1] not in GF_dict:
														sys.stderr.write("Chyba: Premenna neexistuje. \n")
														sys.exit(54)
													else:
														if GF_dict[arg3[1]] == None:
															sys.stderr.write("Chyba: Premenna neinicializovana\n")
															sys.exit(56)
														else:
															if GF_dict[arg3[1]].type != "int":
																sys.stderr.write("Chyba: Zly typ premennej\n")
																sys.exit(53)
															else:
																temp_value = int(TF_dict[arg2[1]].value) + int(GF_dict[arg3[1]].value)
																temp_var = IPPvariable("int", temp_value)
																LF_list[len(LF_list)-1][arg1[1]] = temp_var
																#print(LF_list[len(LF_list)-1][arg1[1]].type, LF_list[len(LF_list)-1][arg1[1]].value )
		##
												elif arg3[0] == "LF": ####################
													if LF_created == 1:
														if len(LF_list) == 0:
															sys.stderr.write("Chyba: Ramec neexistuje.\n")
															sys.exit(55)
														if arg3[1] not in LF_list[len(LF_list)-1]:
															sys.stderr.write("Chyba: Premenna neexistuje.\n")
															sys.exit(54)
														else:
															if LF_list[len(LF_list)-1][arg3[1]] == None:
																sys.stderr.write("Chyba: Premenna neinicializovana\n")
																sys.exit(56)
															else:
																if LF_list[len(LF_list)-1][arg3[1]].type != "int":
																	sys.stderr.write("Chyba: Zly typ premennej\n")
																	sys.exit(53)
																else:
																	temp_value = int(TF_dict[arg2[1]].value) + int(LF_list[len(LF_list)-1][arg3[1]].value)
																	temp_var = IPPvariable("int", temp_value)
																	LF_list[len(LF_list)-1][arg1[1]] = temp_var
																	#print(LF_list[len(LF_list)-1][arg1[1]].type, LF_list[len(LF_list)-1][arg1[1]].value )
													else:
														sys.stderr.write("Chyba: Ramec neexistuje.\n")
														sys.exit(55)								
												elif arg3[0] == "TF": ####################
													if TF_created == 1:
														if arg3[1] not in TF_dict:
															sys.stderr.write("Chyba: Premenna neexistuje.\n")
															sys.exit(54)
														else:
															if TF_dict[arg3[1]] == None:
																sys.stderr.write("Chyba: Premenna neinicializovana\n")
																sys.exit(56)
															else:
																if TF_dict[arg3[1]].type != "int":
																	sys.stderr.write("Chyba: Zly typ premennej\n")
																	sys.exit(53)
																else:
																	temp_value = int(TF_dict[arg2[1]].value) + int(TF_dict[arg3[1]].value)
																	temp_var = IPPvariable("int", temp_value)
																	LF_list[len(LF_list)-1][arg1[1]] = temp_var
																	#print(LF_list[len(LF_list)-1][arg1[1]].type, LF_list[len(LF_list)-1][arg1[1]].value )
													else:
														sys.stderr.write("Chyba: Ramec neexistuje.\n")
														sys.exit(55)
								else:
									sys.stderr.write("Chyba: Ramec neexistuje.\n")
									sys.exit(55)														
						else:
							sys.stderr.write("Chyba: Zly typ premennej \n")
							sys.exit(53)

				else:
					sys.stderr.write("Chyba: Ramec neexistuje.\n")
					sys.exit(55)	
			elif arg1[0] == "TF": ################################
				if TF_created == 1:
					if arg1[1] not in TF_dict:
						sys.stderr.write("Chyba: Premenna neexistuje.\n")
						sys.exit(54)
					else:
						if current_instruction.arg2_type == "int" and current_instruction.arg3_type == "int":
							temp_value = int(current_instruction.arg2_value) + int(current_instruction.arg3_value)
							temp_var = IPPvariable("int", temp_value)
							TF_dict[arg1[1]] = temp_var
							#print(TF_dict[arg1[1]].type, TF_dict[arg1[1]].value )
							
						elif current_instruction.arg2_type == "var" and current_instruction.arg3_type == "int":
							arg2 = parse_variable(current_instruction.arg2_value)
							if arg2[0] == "GF":
								if arg2[1] not in GF_dict:
									sys.stderr.write("Chyba: Premenna neexistuje. \n")
									sys.exit(54)
								else:
									if GF_dict[arg2[1]] == None:
										sys.stderr.write("Chyba: Premenna neinicializovana\n")
										sys.exit(56)
									else:
										if GF_dict[arg2[1]].type != "int":
											sys.stderr.write("Chyba: Zly typ premennej\n")
											sys.exit(53)
										else:
											temp_value = int(GF_dict[arg2[1]].value) + int(current_instruction.arg3_value)
											temp_var = IPPvariable("int", temp_value)
											TF_dict[arg1[1]] = temp_var
											#print(TF_dict[arg1[1]].type, TF_dict[arg1[1]].value )
							elif arg2[0] == "LF": ####################
								if LF_created == 1:
									if len(LF_list) == 0:
										sys.stderr.write("Chyba: Ramec neexistuje.\n")
										sys.exit(55)
									if arg2[1] not in LF_list[len(LF_list)-1]:
										sys.stderr.write("Chyba: Premenna neexistuje.\n")
										sys.exit(54)
									else:
										if LF_list[len(LF_list)-1][arg2[1]] == None:
											sys.stderr.write("Chyba: Premenna neinicializovana\n")
											sys.exit(56)
										else:
											if LF_list[len(LF_list)-1][arg2[1]].type != "int":
												sys.stderr.write("Chyba: Zly typ premennej\n")
												sys.exit(53)
											else:
												temp_value = int(LF_list[len(LF_list)-1][arg2[1]].value) + int(current_instruction.arg3_value)
												temp_var = IPPvariable("int", temp_value)
												TF_dict[arg1[1]] = temp_var
												#print(TF_dict[arg1[1]].type, TF_dict[arg1[1]].value )
								else:
									sys.stderr.write("Chyba: Ramec neexistuje.\n")
									sys.exit(55)								
							elif arg2[0] == "TF": ####################
								if TF_created == 1:
									if arg2[1] not in TF_dict:
										sys.stderr.write("Chyba: Premenna neexistuje.\n")
										sys.exit(54)
									else:
										if TF_dict[arg2[1]] == None:
											sys.stderr.write("Chyba: Premenna neinicializovana\n")
											sys.exit(56)
										else:
											if TF_dict[arg2[1]].type != "int":
												sys.stderr.write("Chyba: Zly typ premennej\n")
												sys.exit(53)
											else:
												temp_value = int(TF_dict[arg2[1]].value) + int(current_instruction.arg3_value)
												temp_var = IPPvariable("int", temp_value)
												TF_dict[arg1[1]] = temp_var
												#print(TF_dict[arg1[1]].type, TF_dict[arg1[1]].value )
								else:
									sys.stderr.write("Chyba: Ramec neexistuje.\n")
									sys.exit(55)
											
						elif current_instruction.arg2_type == "int" and current_instruction.arg3_type == "var":
							arg2 = parse_variable(current_instruction.arg3_value)
							if arg2[0] == "GF":
								if arg2[1] not in GF_dict:
									sys.stderr.write("Chyba: Premenna neexistuje. \n")
									sys.exit(54)
								else:
									if GF_dict[arg2[1]] == None:
										sys.stderr.write("Chyba: Premenna neinicializovana\n")
										sys.exit(56)
									else:
										if GF_dict[arg2[1]].type != "int":
											sys.stderr.write("Chyba: Zly typ premennej\n")
											sys.exit(53)
										else:
											temp_value = int(GF_dict[arg2[1]].value) + int(current_instruction.arg2_value)
											temp_var = IPPvariable("int", temp_value)
											TF_dict[arg1[1]] = temp_var
											#print(TF_dict[arg1[1]].type, TF_dict[arg1[1]].value )
							elif arg2[0] == "LF": ####################
								if LF_created == 1:
									if len(LF_list) == 0:
										sys.stderr.write("Chyba: Ramec neexistuje.\n")
										sys.exit(55)
									if arg2[1] not in LF_list[len(LF_list)-1]:
										sys.stderr.write("Chyba: Premenna neexistuje.\n")
										sys.exit(54)
									else:
										if LF_list[len(LF_list)-1][arg2[1]] == None:
											sys.stderr.write("Chyba: Premenna neinicializovana\n")
											sys.exit(56)
										else:
											if LF_list[len(LF_list)-1][arg2[1]].type != "int":
												sys.stderr.write("Chyba: Zly typ premennej\n")
												sys.exit(53)
											else:
												temp_value = int(LF_list[len(LF_list)-1][arg2[1]].value) + int(current_instruction.arg2_value)
												temp_var = IPPvariable("int", temp_value)
												TF_dict[arg1[1]] = temp_var
												#print(TF_dict[arg1[1]].type, TF_dict[arg1[1]].value )
								else:
									sys.stderr.write("Chyba: Ramec neexistuje.\n")
									sys.exit(55)								
							elif arg2[0] == "TF": ####################
								if TF_created == 1:
									if arg2[1] not in TF_dict:
										sys.stderr.write("Chyba: Premenna neexistuje.\n")
										sys.exit(54)
									else:
										if TF_dict[arg2[1]] == None:
											sys.stderr.write("Chyba: Premenna neinicializovana\n")
											sys.exit(56)
										else:
											if TF_dict[arg2[1]].type != "int":
												sys.stderr.write("Chyba: Zly typ premennej\n")
												sys.exit(53)
											else:
												temp_value = int(TF_dict[arg2[1]].value) + int(current_instruction.arg2_value)
												temp_var = IPPvariable("int", temp_value)
												TF_dict[arg1[1]] = temp_var
												#print(TF_dict[arg1[1]].type, TF_dict[arg1[1]].value )
								else:
									sys.stderr.write("Chyba: Ramec neexistuje.\n")
									sys.exit(55)
											
						elif current_instruction.arg2_type == "var" and current_instruction.arg3_type == "var":
							arg2 = parse_variable(current_instruction.arg2_value)
							arg3 = parse_variable(current_instruction.arg3_value)
							if arg2[0] == "GF":
								if arg2[1] not in GF_dict:
									sys.stderr.write("Chyba: Premenna neexistuje. \n")
									sys.exit(54)
								else:
									if GF_dict[arg2[1]] == None:
										sys.stderr.write("Chyba: Premenna neinicializovana\n")
										sys.exit(56)
									else:
										if GF_dict[arg2[1]].type != "int":
											sys.stderr.write("Chyba: Zly typ premennej\n")
											sys.exit(53)
										else:
											###
											if arg3[0] == "GF":
												if arg3[1] not in GF_dict:
													sys.stderr.write("Chyba: Premenna neexistuje. \n")
													sys.exit(54)
												else:
													if GF_dict[arg3[1]] == None:
														sys.stderr.write("Chyba: Premenna neinicializovana\n")
														sys.exit(56)
													else:
														if GF_dict[arg3[1]].type != "int":
															sys.stderr.write("Chyba: Zly typ premennej\n")
															sys.exit(53)
														else:
															temp_value = int(GF_dict[arg2[1]].value) + int(GF_dict[arg3[1]].value)
															temp_var = IPPvariable("int", temp_value)
															TF_dict[arg1[1]] = temp_var
															#print(TF_dict[arg1[1]].type, TF_dict[arg1[1]].value )
	##
											elif arg3[0] == "LF": ####################
												if LF_created == 1:
													if len(LF_list) == 0:
														sys.stderr.write("Chyba: Ramec neexistuje.\n")
														sys.exit(55)
													if arg3[1] not in LF_list[len(LF_list)-1]:
														sys.stderr.write("Chyba: Premenna neexistuje.\n")
														sys.exit(54)
													else:
														if LF_list[len(LF_list)-1][arg3[1]] == None:
															sys.stderr.write("Chyba: Premenna neinicializovana\n")
															sys.exit(56)
														else:
															if LF_list[len(LF_list)-1][arg3[1]].type != "int":
																sys.stderr.write("Chyba: Zly typ premennej\n")
																sys.exit(53)
															else:
																temp_value = int(GF_dict[arg2[1]].value) + int(LF_list[len(LF_list)-1][arg3[1]].value)
																temp_var = IPPvariable("int", temp_value)
																TF_dict[arg1[1]] = temp_var
																#print(TF_dict[arg1[1]].type, TF_dict[arg1[1]].value )
												else:
													sys.stderr.write("Chyba: Ramec neexistuje.\n")
													sys.exit(55)								
											elif arg3[0] == "TF": ####################
												if TF_created == 1:
													if arg3[1] not in TF_dict:
														sys.stderr.write("Chyba: Premenna neexistuje.\n")
														sys.exit(54)
													else:
														if TF_dict[arg3[1]] == None:
															sys.stderr.write("Chyba: Premenna neinicializovana\n")
															sys.exit(56)
														else:
															if TF_dict[arg3[1]].type != "int":
																sys.stderr.write("Chyba: Zly typ premennej\n")
																sys.exit(53)
															else:
																temp_value = int(GF_dict[arg2[1]].value) + int(TF_dict[arg3[1]].value)
																temp_var = IPPvariable("int", temp_value)
																TF_dict[arg1[1]] = temp_var
																#print(TF_dict[arg1[1]].type, TF_dict[arg1[1]].value )
												else:
													sys.stderr.write("Chyba: Ramec neexistuje.\n")
													sys.exit(55)
							elif arg2[0] == "LF": ####################
								if LF_created == 1:
									if len(LF_list) == 0:
										sys.stderr.write("Chyba: Ramec neexistuje.\n")
										sys.exit(55)
									if arg2[1] not in LF_list[len(LF_list)-1]:
										sys.stderr.write("Chyba: Premenna neexistuje.\n")
										sys.exit(54)
									else:
										if LF_list[len(LF_list)-1][arg2[1]] == None:
											sys.stderr.write("Chyba: Premenna neinicializovana\n")
											sys.exit(56)
										else:
											if LF_list[len(LF_list)-1][arg2[1]].type != "int":
												sys.stderr.write("Chyba: Zly typ premennej\n")
												sys.exit(53)
											else:
												if arg3[0] == "GF":
													if arg3[1] not in GF_dict:
														sys.stderr.write("Chyba: Premenna neexistuje. \n")
														sys.exit(54)
													else:
														if GF_dict[arg3[1]] == None:
															sys.stderr.write("Chyba: Premenna neinicializovana\n")
															sys.exit(56)
														else:
															if GF_dict[arg3[1]].type != "int":
																sys.stderr.write("Chyba: Zly typ premennej\n")
																sys.exit(53)
															else:
																temp_value = int(LF_list[len(LF_list)-1][arg2[1]].value) + int(GF_dict[arg3[1]].value)
																temp_var = IPPvariable("int", temp_value)
																TF_dict[arg1[1]] = temp_var
																#print(TF_dict[arg1[1]].type, TF_dict[arg1[1]].value )
		##
												elif arg3[0] == "LF": ####################
													if LF_created == 1:
														if len(LF_list) == 0:
															sys.stderr.write("Chyba: Ramec neexistuje.\n")
															sys.exit(55)
														if arg3[1] not in LF_list[len(LF_list)-1]:
															sys.stderr.write("Chyba: Premenna neexistuje.\n")
															sys.exit(54)
														else:
															if LF_list[len(LF_list)-1][arg3[1]] == None:
																sys.stderr.write("Chyba: Premenna neinicializovana\n")
																sys.exit(56)
															else:
																if LF_list[len(LF_list)-1][arg3[1]].type != "int":
																	sys.stderr.write("Chyba: Zly typ premennej\n")
																	sys.exit(53)
																else:
																	temp_value = int(LF_list[len(LF_list)-1][arg2[1]].value) + int(LF_list[len(LF_list)-1][arg3[1]].value)
																	temp_var = IPPvariable("int", temp_value)
																	TF_dict[arg1[1]] = temp_var
																	#print(TF_dict[arg1[1]].type, TF_dict[arg1[1]].value )
													else:
														sys.stderr.write("Chyba: Ramec neexistuje.\n")
														sys.exit(55)								
												elif arg3[0] == "TF": ####################
													if TF_created == 1:
														if arg3[1] not in TF_dict:
															sys.stderr.write("Chyba: Premenna neexistuje.\n")
															sys.exit(54)
														else:
															if TF_dict[arg3[1]] == None:
																sys.stderr.write("Chyba: Premenna neinicializovana\n")
																sys.exit(56)
															else:
																if TF_dict[arg3[1]].type != "int":
																	sys.stderr.write("Chyba: Zly typ premennej\n")
																	sys.exit(53)
																else:
																	temp_value = int(LF_list[len(LF_list)-1][arg2[1]].value) + int(TF_dict[arg3[1]].value)
																	temp_var = IPPvariable("int", temp_value)
																	TF_dict[arg1[1]] = temp_var
																	#print(TF_dict[arg1[1]].type, TF_dict[arg1[1]].value )
													else:
														sys.stderr.write("Chyba: Ramec neexistuje.\n")
														sys.exit(55)
								else:
									sys.stderr.write("Chyba: Ramec neexistuje.\n")
									sys.exit(55)								
							elif arg2[0] == "TF": ####################
								if TF_created == 1:
									if arg2[1] not in TF_dict:
										sys.stderr.write("Chyba: Premenna neexistuje.\n")
										sys.exit(54)
									else:
										if TF_dict[arg2[1]] == None:
											sys.stderr.write("Chyba: Premenna neinicializovana\n")
											sys.exit(56)
										else:
											if TF_dict[arg2[1]].type != "int":
												sys.stderr.write("Chyba: Zly typ premennej\n")
												sys.exit(53)
											else:
												if arg3[0] == "GF":
													if arg3[1] not in GF_dict:
														sys.stderr.write("Chyba: Premenna neexistuje. \n")
														sys.exit(54)
													else:
														if GF_dict[arg3[1]] == None:
															sys.stderr.write("Chyba: Premenna neinicializovana\n")
															sys.exit(56)
														else:
															if GF_dict[arg3[1]].type != "int":
																sys.stderr.write("Chyba: Zly typ premennej\n")
																sys.exit(53)
															else:
																temp_value = int(TF_dict[arg2[1]].value) + int(GF_dict[arg3[1]].value)
																temp_var = IPPvariable("int", temp_value)
																TF_dict[arg1[1]] = temp_var
																#print(TF_dict[arg1[1]].type, TF_dict[arg1[1]].value )
		##
												elif arg3[0] == "LF": ####################
													if LF_created == 1:
														if len(LF_list) == 0:
															sys.stderr.write("Chyba: Ramec neexistuje.\n")
															sys.exit(55)
														if arg3[1] not in LF_list[len(LF_list)-1]:
															sys.stderr.write("Chyba: Premenna neexistuje.\n")
															sys.exit(54)
														else:
															if LF_list[len(LF_list)-1][arg3[1]] == None:
																sys.stderr.write("Chyba: Premenna neinicializovana\n")
																sys.exit(56)
															else:
																if LF_list[len(LF_list)-1][arg3[1]].type != "int":
																	sys.stderr.write("Chyba: Zly typ premennej\n")
																	sys.exit(53)
																else:
																	temp_value = int(TF_dict[arg2[1]].value) + int(LF_list[len(LF_list)-1][arg3[1]].value)
																	temp_var = IPPvariable("int", temp_value)
																	TF_dict[arg1[1]] = temp_var
																	#print(TF_dict[arg1[1]].type, TF_dict[arg1[1]].value )
													else:
														sys.stderr.write("Chyba: Ramec neexistuje.\n")
														sys.exit(55)								
												elif arg3[0] == "TF": ####################
													if TF_created == 1:
														if arg3[1] not in TF_dict:
															sys.stderr.write("Chyba: Premenna neexistuje.\n")
															sys.exit(54)
														else:
															if TF_dict[arg3[1]] == None:
																sys.stderr.write("Chyba: Premenna neinicializovana\n")
																sys.exit(56)
															else:
																if TF_dict[arg3[1]].type != "int":
																	sys.stderr.write("Chyba: Zly typ premennej\n")
																	sys.exit(53)
																else:
																	temp_value = int(TF_dict[arg2[1]].value) + int(TF_dict[arg3[1]].value)
																	temp_var = IPPvariable("int", temp_value)
																	TF_dict[arg1[1]] = temp_var
																	#print(TF_dict[arg1[1]].type, TF_dict[arg1[1]].value )
													else:
														sys.stderr.write("Chyba: Ramec neexistuje.\n")
														sys.exit(55)
								else:
									sys.stderr.write("Chyba: Ramec neexistuje.\n")
									sys.exit(55)						
				else:
					sys.stderr.write("Chyba: Ramec neexistuje.\n")
					sys.exit(55)	
			#print("ADD OK")			
		##############################################
		elif current_instruction.opcode.upper() == "SUB":
			arg1 = parse_variable(current_instruction.arg1_value)
			if arg1[0] == "GF":
				if arg1[1] not in GF_dict:
					sys.stderr.write("Chyba: Premenna neexistuje.\n")
					sys.exit(54)
				else:
					if current_instruction.arg2_type == "int" and current_instruction.arg3_type == "int":
						temp_value = int(current_instruction.arg2_value) - int(current_instruction.arg3_value)
						temp_var = IPPvariable("int", temp_value)
						GF_dict[arg1[1]] = temp_var
						#print(GF_dict[arg1[1]].type, GF_dict[arg1[1]].value )
						
					elif current_instruction.arg2_type == "var" and current_instruction.arg3_type == "int":
						arg2 = parse_variable(current_instruction.arg2_value)
						if arg2[0] == "GF":
							if arg2[1] not in GF_dict:
								sys.stderr.write("Chyba: Premenna neexistuje. \n")
								sys.exit(54)
							else:
								if GF_dict[arg2[1]] == None:
									sys.stderr.write("Chyba: Premenna neinicializovana\n")
									sys.exit(56)
								else:
									if GF_dict[arg2[1]].type != "int":
										sys.stderr.write("Chyba: Zly typ premennej\n")
										sys.exit(53)
									else:
										temp_value = int(GF_dict[arg2[1]].value) - int(current_instruction.arg3_value)
										temp_var = IPPvariable("int", temp_value)
										GF_dict[arg1[1]] = temp_var
										#print(GF_dict[arg1[1]].type, GF_dict[arg1[1]].value )
						elif arg2[0] == "LF": ####################
							if LF_created == 1:
								if len(LF_list) == 0:
									sys.stderr.write("Chyba: Ramec neexistuje.\n")
									sys.exit(55)
								if arg2[1] not in LF_list[len(LF_list)-1]:
									sys.stderr.write("Chyba: Premenna neexistuje.\n")
									sys.exit(54)
								else:
									if LF_list[len(LF_list)-1][arg2[1]] == None:
										sys.stderr.write("Chyba: Premenna neinicializovana\n")
										sys.exit(56)
									else:
										if LF_list[len(LF_list)-1][arg2[1]].type != "int":
											sys.stderr.write("Chyba: Zly typ premennej\n")
											sys.exit(53)
										else:
											temp_value = int(LF_list[len(LF_list)-1][arg2[1]].value) - int(current_instruction.arg3_value)
											temp_var = IPPvariable("int", temp_value)
											GF_dict[arg1[1]] = temp_var
											#print(GF_dict[arg1[1]].type, GF_dict[arg1[1]].value )
							else:
								sys.stderr.write("Chyba: Ramec neexistuje.\n")
								sys.exit(55)								
						elif arg2[0] == "TF": ####################
							if TF_created == 1:
								if arg2[1] not in TF_dict:
									sys.stderr.write("Chyba: Premenna neexistuje.\n")
									sys.exit(54)
								else:
									if TF_dict[arg2[1]] == None:
										sys.stderr.write("Chyba: Premenna neinicializovana\n")
										sys.exit(56)
									else:
										if TF_dict[arg2[1]].type != "int":
											sys.stderr.write("Chyba: Zly typ premennej\n")
											sys.exit(53)
										else:
											temp_value = int(TF_dict[arg2[1]].value) - int(current_instruction.arg3_value)
											temp_var = IPPvariable("int", temp_value)
											GF_dict[arg1[1]] = temp_var
											#print(GF_dict[arg1[1]].type, GF_dict[arg1[1]].value )
							else:
								sys.stderr.write("Chyba: Ramec neexistuje.\n")
								sys.exit(55)
										
					elif current_instruction.arg2_type == "int" and current_instruction.arg3_type == "var":
						arg2 = parse_variable(current_instruction.arg3_value)
						if arg2[0] == "GF":
							if arg2[1] not in GF_dict:
								sys.stderr.write("Chyba: Premenna neexistuje. \n")
								sys.exit(54)
							else:
								if GF_dict[arg2[1]] == None:
									sys.stderr.write("Chyba: Premenna neinicializovana\n")
									sys.exit(56)
								else:
									if GF_dict[arg2[1]].type != "int":
										sys.stderr.write("Chyba: Zly typ premennej\n")
										sys.exit(53)
									else:
										temp_value =  int(current_instruction.arg2_value) - int(GF_dict[arg2[1]].value)
										temp_var = IPPvariable("int", temp_value)
										GF_dict[arg1[1]] = temp_var
										#print(GF_dict[arg1[1]].type, GF_dict[arg1[1]].value )
						elif arg2[0] == "LF": ####################
							if LF_created == 1:
								if len(LF_list) == 0:
									sys.stderr.write("Chyba: Ramec neexistuje.\n")
									sys.exit(55)
								if arg2[1] not in LF_list[len(LF_list)-1]:
									sys.stderr.write("Chyba: Premenna neexistuje.\n")
									sys.exit(54)
								else:
									if LF_list[len(LF_list)-1][arg2[1]] == None:
										sys.stderr.write("Chyba: Premenna neinicializovana\n")
										sys.exit(56)
									else:
										if LF_list[len(LF_list)-1][arg2[1]].type != "int":
											sys.stderr.write("Chyba: Zly typ premennej\n")
											sys.exit(53)
										else:
											temp_value = int(current_instruction.arg2_value) - int(LF_list[len(LF_list)-1][arg2[1]].value)
											temp_var = IPPvariable("int", temp_value)
											GF_dict[arg1[1]] = temp_var
											#print(GF_dict[arg1[1]].type, GF_dict[arg1[1]].value )
							else:
								sys.stderr.write("Chyba: Ramec neexistuje.\n")
								sys.exit(55)								
						elif arg2[0] == "TF": ####################
							if TF_created == 1:
								if arg2[1] not in TF_dict:
									sys.stderr.write("Chyba: Premenna neexistuje.\n")
									sys.exit(54)
								else:
									if TF_dict[arg2[1]] == None:
										sys.stderr.write("Chyba: Premenna neinicializovana\n")
										sys.exit(56)
									else:
										if TF_dict[arg2[1]].type != "int":
											sys.stderr.write("Chyba: Zly typ premennej\n")
											sys.exit(53)
										else:
											temp_value = int(current_instruction.arg2_value) - int(TF_dict[arg2[1]].value)
											temp_var = IPPvariable("int", temp_value)
											GF_dict[arg1[1]] = temp_var
											#print(GF_dict[arg1[1]].type, GF_dict[arg1[1]].value )
							else:
								sys.stderr.write("Chyba: Ramec neexistuje.\n")
								sys.exit(55)
										
					elif current_instruction.arg2_type == "var" and current_instruction.arg3_type == "var":
						arg2 = parse_variable(current_instruction.arg2_value)
						arg3 = parse_variable(current_instruction.arg3_value)
						if arg2[0] == "GF":
							if arg2[1] not in GF_dict:
								sys.stderr.write("Chyba: Premenna neexistuje. \n")
								sys.exit(54)
							else:
								if GF_dict[arg2[1]] == None:
									sys.stderr.write("Chyba: Premenna neinicializovana\n")
									sys.exit(56)
								else:
									if GF_dict[arg2[1]].type != "int":
										sys.stderr.write("Chyba: Zly typ premennej\n")
										sys.exit(53)
									else:
										###
										if arg3[0] == "GF":
											if arg3[1] not in GF_dict:
												sys.stderr.write("Chyba: Premenna neexistuje. \n")
												sys.exit(54)
											else:
												if GF_dict[arg3[1]] == None:
													sys.stderr.write("Chyba: Premenna neinicializovana\n")
													sys.exit(56)
												else:
													if GF_dict[arg3[1]].type != "int":
														sys.stderr.write("Chyba: Zly typ premennej\n")
														sys.exit(53)
													else:
														temp_value = int(GF_dict[arg2[1]].value) - int(GF_dict[arg3[1]].value)
														temp_var = IPPvariable("int", temp_value)
														GF_dict[arg1[1]] = temp_var
														#print(GF_dict[arg1[1]].type, GF_dict[arg1[1]].value )
##
										elif arg3[0] == "LF": ####################
											if LF_created == 1:
												if len(LF_list) == 0:
													sys.stderr.write("Chyba: Ramec neexistuje.\n")
													sys.exit(55)
												if arg3[1] not in LF_list[len(LF_list)-1]:
													sys.stderr.write("Chyba: Premenna neexistuje.\n")
													sys.exit(54)
												else:
													if LF_list[len(LF_list)-1][arg3[1]] == None:
														sys.stderr.write("Chyba: Premenna neinicializovana\n")
														sys.exit(56)
													else:
														if LF_list[len(LF_list)-1][arg3[1]].type != "int":
															sys.stderr.write("Chyba: Zly typ premennej\n")
															sys.exit(53)
														else:
															temp_value = int(GF_dict[arg2[1]].value) - int(LF_list[len(LF_list)-1][arg3[1]].value)
															temp_var = IPPvariable("int", temp_value)
															GF_dict[arg1[1]] = temp_var
															#print(GF_dict[arg1[1]].type, GF_dict[arg1[1]].value )
											else:
												sys.stderr.write("Chyba: Ramec neexistuje.\n")
												sys.exit(55)								
										elif arg3[0] == "TF": ####################
											if TF_created == 1:
												if arg3[1] not in TF_dict:
													sys.stderr.write("Chyba: Premenna neexistuje.\n")
													sys.exit(54)
												else:
													if TF_dict[arg3[1]] == None:
														sys.stderr.write("Chyba: Premenna neinicializovana\n")
														sys.exit(56)
													else:
														if TF_dict[arg3[1]].type != "int":
															sys.stderr.write("Chyba: Zly typ premennej\n")
															sys.exit(53)
														else:
															temp_value = int(GF_dict[arg2[1]].value) - int(TF_dict[arg3[1]].value)
															temp_var = IPPvariable("int", temp_value)
															GF_dict[arg1[1]] = temp_var
															#print(GF_dict[arg1[1]].type, GF_dict[arg1[1]].value )
											else:
												sys.stderr.write("Chyba: Ramec neexistuje.\n")
												sys.exit(55)
						elif arg2[0] == "LF": ####################
							if LF_created == 1:
								if len(LF_list) == 0:
									sys.stderr.write("Chyba: Ramec neexistuje.\n")
									sys.exit(55)
								if arg2[1] not in LF_list[len(LF_list)-1]:
									sys.stderr.write("Chyba: Premenna neexistuje.\n")
									sys.exit(54)
								else:
									if LF_list[len(LF_list)-1][arg2[1]] == None:
										sys.stderr.write("Chyba: Premenna neinicializovana\n")
										sys.exit(56)
									else:
										if LF_list[len(LF_list)-1][arg2[1]].type != "int":
											sys.stderr.write("Chyba: Zly typ premennej\n")
											sys.exit(53)
										else:
											if arg3[0] == "GF":
												if arg3[1] not in GF_dict:
													sys.stderr.write("Chyba: Premenna neexistuje. \n")
													sys.exit(54)
												else:
													if GF_dict[arg3[1]] == None:
														sys.stderr.write("Chyba: Premenna neinicializovana\n")
														sys.exit(56)
													else:
														if GF_dict[arg3[1]].type != "int":
															sys.stderr.write("Chyba: Zly typ premennej\n")
															sys.exit(53)
														else:
															temp_value = int(LF_list[len(LF_list)-1][arg2[1]].value) - int(GF_dict[arg3[1]].value)
															temp_var = IPPvariable("int", temp_value)
															GF_dict[arg1[1]] = temp_var
															#print(GF_dict[arg1[1]].type, GF_dict[arg1[1]].value )
	##
											elif arg3[0] == "LF": ####################
												if LF_created == 1:
													if len(LF_list) == 0:
														sys.stderr.write("Chyba: Ramec neexistuje.\n")
														sys.exit(55)
													if arg3[1] not in LF_list[len(LF_list)-1]:
														sys.stderr.write("Chyba: Premenna neexistuje.\n")
														sys.exit(54)
													else:
														if LF_list[len(LF_list)-1][arg3[1]] == None:
															sys.stderr.write("Chyba: Premenna neinicializovana\n")
															sys.exit(56)
														else:
															if LF_list[len(LF_list)-1][arg3[1]].type != "int":
																sys.stderr.write("Chyba: Zly typ premennej\n")
																sys.exit(53)
															else:
																temp_value = int(LF_list[len(LF_list)-1][arg2[1]].value) - int(LF_list[len(LF_list)-1][arg3[1]].value)
																temp_var = IPPvariable("int", temp_value)
																GF_dict[arg1[1]] = temp_var
																#print(GF_dict[arg1[1]].type, GF_dict[arg1[1]].value )
												else:
													sys.stderr.write("Chyba: Ramec neexistuje.\n")
													sys.exit(55)								
											elif arg3[0] == "TF": ####################
												if TF_created == 1:
													if arg3[1] not in TF_dict:
														sys.stderr.write("Chyba: Premenna neexistuje.\n")
														sys.exit(54)
													else:
														if TF_dict[arg3[1]] == None:
															sys.stderr.write("Chyba: Premenna neinicializovana\n")
															sys.exit(56)
														else:
															if TF_dict[arg3[1]].type != "int":
																sys.stderr.write("Chyba: Zly typ premennej\n")
																sys.exit(53)
															else:
																temp_value = int(LF_list[len(LF_list)-1][arg2[1]].value) - int(TF_dict[arg3[1]].value)
																temp_var = IPPvariable("int", temp_value)
																GF_dict[arg1[1]] = temp_var
																#print(GF_dict[arg1[1]].type, GF_dict[arg1[1]].value )
												else:
													sys.stderr.write("Chyba: Ramec neexistuje.\n")
													sys.exit(55)
							else:
								sys.stderr.write("Chyba: Ramec neexistuje.\n")
								sys.exit(55)								
						elif arg2[0] == "TF": ####################
							if TF_created == 1:
								if arg2[1] not in TF_dict:
									sys.stderr.write("Chyba: Premenna neexistuje.\n")
									sys.exit(54)
								else:
									if TF_dict[arg2[1]] == None:
										sys.stderr.write("Chyba: Premenna neinicializovana\n")
										sys.exit(56)
									else:
										if TF_dict[arg2[1]].type != "int":
											sys.stderr.write("Chyba: Zly typ premennej\n")
											sys.exit(53)
										else:
											if arg3[0] == "GF":
												if arg3[1] not in GF_dict:
													sys.stderr.write("Chyba: Premenna neexistuje. \n")
													sys.exit(54)
												else:
													if GF_dict[arg3[1]] == None:
														sys.stderr.write("Chyba: Premenna neinicializovana\n")
														sys.exit(56)
													else:
														if GF_dict[arg3[1]].type != "int":
															sys.stderr.write("Chyba: Zly typ premennej\n")
															sys.exit(53)
														else:
															temp_value = int(TF_dict[arg2[1]].value) - int(GF_dict[arg3[1]].value)
															temp_var = IPPvariable("int", temp_value)
															GF_dict[arg1[1]] = temp_var
															#print(GF_dict[arg1[1]].type, GF_dict[arg1[1]].value )
	##
											elif arg3[0] == "LF": ####################
												if LF_created == 1:
													if len(LF_list) == 0:
														sys.stderr.write("Chyba: Ramec neexistuje.\n")
														sys.exit(55)
													if arg3[1] not in LF_list[len(LF_list)-1]:
														sys.stderr.write("Chyba: Premenna neexistuje.\n")
														sys.exit(54)
													else:
														if LF_list[len(LF_list)-1][arg3[1]] == None:
															sys.stderr.write("Chyba: Premenna neinicializovana\n")
															sys.exit(56)
														else:
															if LF_list[len(LF_list)-1][arg3[1]].type != "int":
																sys.stderr.write("Chyba: Zly typ premennej\n")
																sys.exit(53)
															else:
																temp_value = int(TF_dict[arg2[1]].value) - int(LF_list[len(LF_list)-1][arg3[1]].value)
																temp_var = IPPvariable("int", temp_value)
																GF_dict[arg1[1]] = temp_var
																#print(GF_dict[arg1[1]].type, GF_dict[arg1[1]].value )
												else:
													sys.stderr.write("Chyba: Ramec neexistuje.\n")
													sys.exit(55)								
											elif arg3[0] == "TF": ####################
												if TF_created == 1:
													if arg3[1] not in TF_dict:
														sys.stderr.write("Chyba: Premenna neexistuje.\n")
														sys.exit(54)
													else:
														if TF_dict[arg3[1]] == None:
															sys.stderr.write("Chyba: Premenna neinicializovana\n")
															sys.exit(56)
														else:
															if TF_dict[arg3[1]].type != "int":
																sys.stderr.write("Chyba: Zly typ premennej\n")
																sys.exit(53)
															else:
																temp_value = int(TF_dict[arg2[1]].value) - int(TF_dict[arg3[1]].value)
																temp_var = IPPvariable("int", temp_value)
																GF_dict[arg1[1]] = temp_var
																#print(GF_dict[arg1[1]].type, GF_dict[arg1[1]].value )
												else:
													sys.stderr.write("Chyba: Ramec neexistuje.\n")
													sys.exit(55)
							else:
								sys.stderr.write("Chyba: Ramec neexistuje.\n")
								sys.exit(55)														
					else:
						sys.stderr.write("Chyba: Zly typ premennej \n")
						sys.exit(53)
			elif arg1[0] == "LF": #####################
				if LF_created == 1:
					if len(LF_list) == 0:
						sys.stderr.write("Chyba: Ramec neexistuje.\n")
						sys.exit(55)						
					if arg1[1] not in LF_list[len(LF_list)-1]:
						sys.stderr.write("Chyba: Premenna neexistuje.\n")
						sys.exit(54)					
					else:
						if current_instruction.arg2_type == "int" and current_instruction.arg3_type == "int":
							temp_value = int(current_instruction.arg2_value) - int(current_instruction.arg3_value)
							temp_var = IPPvariable("int", temp_value)
							LF_list[len(LF_list)-1][arg1[1]] = temp_var
							#print(LF_list[len(LF_list)-1][arg1[1]].type, LF_list[len(LF_list)-1][arg1[1]].value )
							
						elif current_instruction.arg2_type == "var" and current_instruction.arg3_type == "int":
							arg2 = parse_variable(current_instruction.arg2_value)
							if arg2[0] == "GF":
								if arg2[1] not in GF_dict:
									sys.stderr.write("Chyba: Premenna neexistuje. \n")
									sys.exit(54)
								else:
									if GF_dict[arg2[1]] == None:
										sys.stderr.write("Chyba: Premenna neinicializovana\n")
										sys.exit(56)
									else:
										if GF_dict[arg2[1]].type != "int":
											sys.stderr.write("Chyba: Zly typ premennej\n")
											sys.exit(53)
										else:
											temp_value = int(GF_dict[arg2[1]].value) - int(current_instruction.arg3_value)
											temp_var = IPPvariable("int", temp_value)
											LF_list[len(LF_list)-1][arg1[1]] = temp_var
											#print(LF_list[len(LF_list)-1][arg1[1]].type, LF_list[len(LF_list)-1][arg1[1]].value )
							elif arg2[0] == "LF": ####################
								if LF_created == 1:
									if len(LF_list) == 0:
										sys.stderr.write("Chyba: Ramec neexistuje.\n")
										sys.exit(55)
									if arg2[1] not in LF_list[len(LF_list)-1]:
										sys.stderr.write("Chyba: Premenna neexistuje.\n")
										sys.exit(54)
									else:
										if LF_list[len(LF_list)-1][arg2[1]] == None:
											sys.stderr.write("Chyba: Premenna neinicializovana\n")
											sys.exit(56)
										else:
											if LF_list[len(LF_list)-1][arg2[1]].type != "int":
												sys.stderr.write("Chyba: Zly typ premennej\n")
												sys.exit(53)
											else:
												temp_value = int(LF_list[len(LF_list)-1][arg2[1]].value) - int(current_instruction.arg3_value)
												temp_var = IPPvariable("int", temp_value)
												LF_list[len(LF_list)-1][arg1[1]] = temp_var
												#print(LF_list[len(LF_list)-1][arg1[1]].type, LF_list[len(LF_list)-1][arg1[1]].value )
								else:
									sys.stderr.write("Chyba: Ramec neexistuje.\n")
									sys.exit(55)								
							elif arg2[0] == "TF": ####################
								if TF_created == 1:
									if arg2[1] not in TF_dict:
										sys.stderr.write("Chyba: Premenna neexistuje.\n")
										sys.exit(54)
									else:
										if TF_dict[arg2[1]] == None:
											sys.stderr.write("Chyba: Premenna neinicializovana\n")
											sys.exit(56)
										else:
											if TF_dict[arg2[1]].type != "int":
												sys.stderr.write("Chyba: Zly typ premennej\n")
												sys.exit(53)
											else:
												temp_value = int(TF_dict[arg2[1]].value) - int(current_instruction.arg3_value)
												temp_var = IPPvariable("int", temp_value)
												LF_list[len(LF_list)-1][arg1[1]] = temp_var
												#print(LF_list[len(LF_list)-1][arg1[1]].type, LF_list[len(LF_list)-1][arg1[1]].value )
								else:
									sys.stderr.write("Chyba: Ramec neexistuje.\n")
									sys.exit(55)
											
						elif current_instruction.arg2_type == "int" and current_instruction.arg3_type == "var":
							arg2 = parse_variable(current_instruction.arg3_value)
							if arg2[0] == "GF":
								if arg2[1] not in GF_dict:
									sys.stderr.write("Chyba: Premenna neexistuje. \n")
									sys.exit(54)
								else:
									if GF_dict[arg2[1]] == None:
										sys.stderr.write("Chyba: Premenna neinicializovana\n")
										sys.exit(56)
									else:
										if GF_dict[arg2[1]].type != "int":
											sys.stderr.write("Chyba: Zly typ premennej\n")
											sys.exit(53)
										else:
											temp_value =  int(current_instruction.arg2_value) - int(GF_dict[arg2[1]].value)
											temp_var = IPPvariable("int", temp_value)
											LF_list[len(LF_list)-1][arg1[1]] = temp_var
											#print(LF_list[len(LF_list)-1][arg1[1]].type, LF_list[len(LF_list)-1][arg1[1]].value )
							elif arg2[0] == "LF": ####################
								if LF_created == 1:
									if len(LF_list) == 0:
										sys.stderr.write("Chyba: Ramec neexistuje.\n")
										sys.exit(55)
									if arg2[1] not in LF_list[len(LF_list)-1]:
										sys.stderr.write("Chyba: Premenna neexistuje.\n")
										sys.exit(54)
									else:
										if LF_list[len(LF_list)-1][arg2[1]] == None:
											sys.stderr.write("Chyba: Premenna neinicializovana\n")
											sys.exit(56)
										else:
											if LF_list[len(LF_list)-1][arg2[1]].type != "int":
												sys.stderr.write("Chyba: Zly typ premennej\n")
												sys.exit(53)
											else:
												temp_value = int(current_instruction.arg2_value)- int(LF_list[len(LF_list)-1][arg2[1]].value)
												temp_var = IPPvariable("int", temp_value)
												LF_list[len(LF_list)-1][arg1[1]] = temp_var
												#print(LF_list[len(LF_list)-1][arg1[1]].type, LF_list[len(LF_list)-1][arg1[1]].value )
								else:
									sys.stderr.write("Chyba: Ramec neexistuje.\n")
									sys.exit(55)								
							elif arg2[0] == "TF": ####################
								if TF_created == 1:
									if arg2[1] not in TF_dict:
										sys.stderr.write("Chyba: Premenna neexistuje.\n")
										sys.exit(54)
									else:
										if TF_dict[arg2[1]] == None:
											sys.stderr.write("Chyba: Premenna neinicializovana\n")
											sys.exit(56)
										else:
											if TF_dict[arg2[1]].type != "int":
												sys.stderr.write("Chyba: Zly typ premennej\n")
												sys.exit(53)
											else:
												temp_value = int(current_instruction.arg2_value) - int(TF_dict[arg2[1]].value)
												temp_var = IPPvariable("int", temp_value)
												LF_list[len(LF_list)-1][arg1[1]] = temp_var
												#print(LF_list[len(LF_list)-1][arg1[1]].type, LF_list[len(LF_list)-1][arg1[1]].value )
								else:
									sys.stderr.write("Chyba: Ramec neexistuje.\n")
									sys.exit(55)
											
						elif current_instruction.arg2_type == "var" and current_instruction.arg3_type == "var":
							arg2 = parse_variable(current_instruction.arg2_value)
							arg3 = parse_variable(current_instruction.arg3_value)
							if arg2[0] == "GF":
								if arg2[1] not in GF_dict:
									sys.stderr.write("Chyba: Premenna neexistuje. \n")
									sys.exit(54)
								else:
									if GF_dict[arg2[1]] == None:
										sys.stderr.write("Chyba: Premenna neinicializovana\n")
										sys.exit(56)
									else:
										if GF_dict[arg2[1]].type != "int":
											sys.stderr.write("Chyba: Zly typ premennej\n")
											sys.exit(53)
										else:
											###
											if arg3[0] == "GF":
												if arg3[1] not in GF_dict:
													sys.stderr.write("Chyba: Premenna neexistuje. \n")
													sys.exit(54)
												else:
													if GF_dict[arg3[1]] == None:
														sys.stderr.write("Chyba: Premenna neinicializovana\n")
														sys.exit(56)
													else:
														if GF_dict[arg3[1]].type != "int":
															sys.stderr.write("Chyba: Zly typ premennej\n")
															sys.exit(53)
														else:
															temp_value = int(GF_dict[arg2[1]].value) - int(GF_dict[arg3[1]].value)
															temp_var = IPPvariable("int", temp_value)
															LF_list[len(LF_list)-1][arg1[1]] = temp_var
															#print(LF_list[len(LF_list)-1][arg1[1]].type, LF_list[len(LF_list)-1][arg1[1]].value )
	##
											elif arg3[0] == "LF": ####################
												if LF_created == 1:
													if len(LF_list) == 0:
														sys.stderr.write("Chyba: Ramec neexistuje.\n")
														sys.exit(55)
													if arg3[1] not in LF_list[len(LF_list)-1]:
														sys.stderr.write("Chyba: Premenna neexistuje.\n")
														sys.exit(54)
													else:
														if LF_list[len(LF_list)-1][arg3[1]] == None:
															sys.stderr.write("Chyba: Premenna neinicializovana\n")
															sys.exit(56)
														else:
															if LF_list[len(LF_list)-1][arg3[1]].type != "int":
																sys.stderr.write("Chyba: Zly typ premennej\n")
																sys.exit(53)
															else:
																temp_value = int(GF_dict[arg2[1]].value) - int(LF_list[len(LF_list)-1][arg3[1]].value)
																temp_var = IPPvariable("int", temp_value)
																LF_list[len(LF_list)-1][arg1[1]] = temp_var
																#print(LF_list[len(LF_list)-1][arg1[1]].type, LF_list[len(LF_list)-1][arg1[1]].value )
												else:
													sys.stderr.write("Chyba: Ramec neexistuje.\n")
													sys.exit(55)								
											elif arg3[0] == "TF": ####################
												if TF_created == 1:
													if arg3[1] not in TF_dict:
														sys.stderr.write("Chyba: Premenna neexistuje.\n")
														sys.exit(54)
													else:
														if TF_dict[arg3[1]] == None:
															sys.stderr.write("Chyba: Premenna neinicializovana\n")
															sys.exit(56)
														else:
															if TF_dict[arg3[1]].type != "int":
																sys.stderr.write("Chyba: Zly typ premennej\n")
																sys.exit(53)
															else:
																temp_value = int(GF_dict[arg2[1]].value) - int(TF_dict[arg3[1]].value)
																temp_var = IPPvariable("int", temp_value)
																LF_list[len(LF_list)-1][arg1[1]] = temp_var
																#print(LF_list[len(LF_list)-1][arg1[1]].type, LF_list[len(LF_list)-1][arg1[1]].value )
												else:
													sys.stderr.write("Chyba: Ramec neexistuje.\n")
													sys.exit(55)
							elif arg2[0] == "LF": ####################
								if LF_created == 1:
									if len(LF_list) == 0:
										sys.stderr.write("Chyba: Ramec neexistuje.\n")
										sys.exit(55)
									if arg2[1] not in LF_list[len(LF_list)-1]:
										sys.stderr.write("Chyba: Premenna neexistuje.\n")
										sys.exit(54)
									else:
										if LF_list[len(LF_list)-1][arg2[1]] == None:
											sys.stderr.write("Chyba: Premenna neinicializovana\n")
											sys.exit(56)
										else:
											if LF_list[len(LF_list)-1][arg2[1]].type != "int":
												sys.stderr.write("Chyba: Zly typ premennej\n")
												sys.exit(53)
											else:
												if arg3[0] == "GF":
													if arg3[1] not in GF_dict:
														sys.stderr.write("Chyba: Premenna neexistuje. \n")
														sys.exit(54)
													else:
														if GF_dict[arg3[1]] == None:
															sys.stderr.write("Chyba: Premenna neinicializovana\n")
															sys.exit(56)
														else:
															if GF_dict[arg3[1]].type != "int":
																sys.stderr.write("Chyba: Zly typ premennej\n")
																sys.exit(53)
															else:
																temp_value = int(LF_list[len(LF_list)-1][arg2[1]].value) - int(GF_dict[arg3[1]].value)
																temp_var = IPPvariable("int", temp_value)
																LF_list[len(LF_list)-1][arg1[1]] = temp_var
																#print(LF_list[len(LF_list)-1][arg1[1]].type, LF_list[len(LF_list)-1][arg1[1]].value )
		##
												elif arg3[0] == "LF": ####################
													if LF_created == 1:
														if len(LF_list) == 0:
															sys.stderr.write("Chyba: Ramec neexistuje.\n")
															sys.exit(55)
														if arg3[1] not in LF_list[len(LF_list)-1]:
															sys.stderr.write("Chyba: Premenna neexistuje.\n")
															sys.exit(54)
														else:
															if LF_list[len(LF_list)-1][arg3[1]] == None:
																sys.stderr.write("Chyba: Premenna neinicializovana\n")
																sys.exit(56)
															else:
																if LF_list[len(LF_list)-1][arg3[1]].type != "int":
																	sys.stderr.write("Chyba: Zly typ premennej\n")
																	sys.exit(53)
																else:
																	temp_value = int(LF_list[len(LF_list)-1][arg2[1]].value) - int(LF_list[len(LF_list)-1][arg3[1]].value)
																	temp_var = IPPvariable("int", temp_value)
																	LF_list[len(LF_list)-1][arg1[1]] = temp_var
																	#print(LF_list[len(LF_list)-1][arg1[1]].type, LF_list[len(LF_list)-1][arg1[1]].value )
													else:
														sys.stderr.write("Chyba: Ramec neexistuje.\n")
														sys.exit(55)								
												elif arg3[0] == "TF": ####################
													if TF_created == 1:
														if arg3[1] not in TF_dict:
															sys.stderr.write("Chyba: Premenna neexistuje.\n")
															sys.exit(54)
														else:
															if TF_dict[arg3[1]] == None:
																sys.stderr.write("Chyba: Premenna neinicializovana\n")
																sys.exit(56)
															else:
																if TF_dict[arg3[1]].type != "int":
																	sys.stderr.write("Chyba: Zly typ premennej\n")
																	sys.exit(53)
																else:
																	temp_value = int(LF_list[len(LF_list)-1][arg2[1]].value) - int(TF_dict[arg3[1]].value)
																	temp_var = IPPvariable("int", temp_value)
																	LF_list[len(LF_list)-1][arg1[1]] = temp_var
																	#print(LF_list[len(LF_list)-1][arg1[1]].type, LF_list[len(LF_list)-1][arg1[1]].value )
													else:
														sys.stderr.write("Chyba: Ramec neexistuje.\n")
														sys.exit(55)
								else:
									sys.stderr.write("Chyba: Ramec neexistuje.\n")
									sys.exit(55)								
							elif arg2[0] == "TF": ####################
								if TF_created == 1:
									if arg2[1] not in TF_dict:
										sys.stderr.write("Chyba: Premenna neexistuje.\n")
										sys.exit(54)
									else:
										if TF_dict[arg2[1]] == None:
											sys.stderr.write("Chyba: Premenna neinicializovana\n")
											sys.exit(56)
										else:
											if TF_dict[arg2[1]].type != "int":
												sys.stderr.write("Chyba: Zly typ premennej\n")
												sys.exit(53)
											else:
												if arg3[0] == "GF":
													if arg3[1] not in GF_dict:
														sys.stderr.write("Chyba: Premenna neexistuje. \n")
														sys.exit(54)
													else:
														if GF_dict[arg3[1]] == None:
															sys.stderr.write("Chyba: Premenna neinicializovana\n")
															sys.exit(56)
														else:
															if GF_dict[arg3[1]].type != "int":
																sys.stderr.write("Chyba: Zly typ premennej\n")
																sys.exit(53)
															else:
																temp_value = int(TF_dict[arg2[1]].value) - int(GF_dict[arg3[1]].value)
																temp_var = IPPvariable("int", temp_value)
																LF_list[len(LF_list)-1][arg1[1]] = temp_var
																#print(LF_list[len(LF_list)-1][arg1[1]].type, LF_list[len(LF_list)-1][arg1[1]].value )
		##
												elif arg3[0] == "LF": ####################
													if LF_created == 1:
														if len(LF_list) == 0:
															sys.stderr.write("Chyba: Ramec neexistuje.\n")
															sys.exit(55)
														if arg3[1] not in LF_list[len(LF_list)-1]:
															sys.stderr.write("Chyba: Premenna neexistuje.\n")
															sys.exit(54)
														else:
															if LF_list[len(LF_list)-1][arg3[1]] == None:
																sys.stderr.write("Chyba: Premenna neinicializovana\n")
																sys.exit(56)
															else:
																if LF_list[len(LF_list)-1][arg3[1]].type != "int":
																	sys.stderr.write("Chyba: Zly typ premennej\n")
																	sys.exit(53)
																else:
																	temp_value = int(TF_dict[arg2[1]].value) - int(LF_list[len(LF_list)-1][arg3[1]].value)
																	temp_var = IPPvariable("int", temp_value)
																	LF_list[len(LF_list)-1][arg1[1]] = temp_var
																	#print(LF_list[len(LF_list)-1][arg1[1]].type, LF_list[len(LF_list)-1][arg1[1]].value )
													else:
														sys.stderr.write("Chyba: Ramec neexistuje.\n")
														sys.exit(55)								
												elif arg3[0] == "TF": ####################
													if TF_created == 1:
														if arg3[1] not in TF_dict:
															sys.stderr.write("Chyba: Premenna neexistuje.\n")
															sys.exit(54)
														else:
															if TF_dict[arg3[1]] == None:
																sys.stderr.write("Chyba: Premenna neinicializovana\n")
																sys.exit(56)
															else:
																if TF_dict[arg3[1]].type != "int":
																	sys.stderr.write("Chyba: Zly typ premennej\n")
																	sys.exit(53)
																else:
																	temp_value = int(TF_dict[arg2[1]].value) - int(TF_dict[arg3[1]].value)
																	temp_var = IPPvariable("int", temp_value)
																	LF_list[len(LF_list)-1][arg1[1]] = temp_var
																	#print(LF_list[len(LF_list)-1][arg1[1]].type, LF_list[len(LF_list)-1][arg1[1]].value )
													else:
														sys.stderr.write("Chyba: Ramec neexistuje.\n")
														sys.exit(55)
								else:
									sys.stderr.write("Chyba: Ramec neexistuje.\n")
									sys.exit(55)														
						else:
							sys.stderr.write("Chyba: Zly typ premennej \n")
							sys.exit(53)

				else:
					sys.stderr.write("Chyba: Ramec neexistuje.\n")
					sys.exit(55)	
			elif arg1[0] == "TF": ################################
				if TF_created == 1:
					if arg1[1] not in TF_dict:
						sys.stderr.write("Chyba: Premenna neexistuje.\n")
						sys.exit(54)
					else:
						if current_instruction.arg2_type == "int" and current_instruction.arg3_type == "int":
							temp_value = int(current_instruction.arg2_value) - int(current_instruction.arg3_value)
							temp_var = IPPvariable("int", temp_value)
							TF_dict[arg1[1]] = temp_var
							#print(TF_dict[arg1[1]].type, TF_dict[arg1[1]].value )
							
						elif current_instruction.arg2_type == "var" and current_instruction.arg3_type == "int":
							arg2 = parse_variable(current_instruction.arg2_value)
							if arg2[0] == "GF":
								if arg2[1] not in GF_dict:
									sys.stderr.write("Chyba: Premenna neexistuje. \n")
									sys.exit(54)
								else:
									if GF_dict[arg2[1]] == None:
										sys.stderr.write("Chyba: Premenna neinicializovana\n")
										sys.exit(56)
									else:
										if GF_dict[arg2[1]].type != "int":
											sys.stderr.write("Chyba: Zly typ premennej\n")
											sys.exit(53)
										else:
											temp_value = int(GF_dict[arg2[1]].value) - int(current_instruction.arg3_value)
											temp_var = IPPvariable("int", temp_value)
											TF_dict[arg1[1]] = temp_var
											#print(TF_dict[arg1[1]].type, TF_dict[arg1[1]].value )
							elif arg2[0] == "LF": ####################
								if LF_created == 1:
									if len(LF_list) == 0:
										sys.stderr.write("Chyba: Ramec neexistuje.\n")
										sys.exit(55)
									if arg2[1] not in LF_list[len(LF_list)-1]:
										sys.stderr.write("Chyba: Premenna neexistuje.\n")
										sys.exit(54)
									else:
										if LF_list[len(LF_list)-1][arg2[1]] == None:
											sys.stderr.write("Chyba: Premenna neinicializovana\n")
											sys.exit(56)
										else:
											if LF_list[len(LF_list)-1][arg2[1]].type != "int":
												sys.stderr.write("Chyba: Zly typ premennej\n")
												sys.exit(53)
											else:
												temp_value = int(LF_list[len(LF_list)-1][arg2[1]].value) - int(current_instruction.arg3_value)
												temp_var = IPPvariable("int", temp_value)
												TF_dict[arg1[1]] = temp_var
												#print(TF_dict[arg1[1]].type, TF_dict[arg1[1]].value )
								else:
									sys.stderr.write("Chyba: Ramec neexistuje.\n")
									sys.exit(55)								
							elif arg2[0] == "TF": ####################
								if TF_created == 1:
									if arg2[1] not in TF_dict:
										sys.stderr.write("Chyba: Premenna neexistuje.\n")
										sys.exit(54)
									else:
										if TF_dict[arg2[1]] == None:
											sys.stderr.write("Chyba: Premenna neinicializovana\n")
											sys.exit(56)
										else:
											if TF_dict[arg2[1]].type != "int":
												sys.stderr.write("Chyba: Zly typ premennej\n")
												sys.exit(53)
											else:
												temp_value = int(TF_dict[arg2[1]].value) - int(current_instruction.arg3_value)
												temp_var = IPPvariable("int", temp_value)
												TF_dict[arg1[1]] = temp_var
												#print(TF_dict[arg1[1]].type, TF_dict[arg1[1]].value )
								else:
									sys.stderr.write("Chyba: Ramec neexistuje.\n")
									sys.exit(55)
											
						elif current_instruction.arg2_type == "int" and current_instruction.arg3_type == "var":
							arg2 = parse_variable(current_instruction.arg3_value)
							if arg2[0] == "GF":
								if arg2[1] not in GF_dict:
									sys.stderr.write("Chyba: Premenna neexistuje. \n")
									sys.exit(54)
								else:
									if GF_dict[arg2[1]] == None:
										sys.stderr.write("Chyba: Premenna neinicializovana\n")
										sys.exit(56)
									else:
										if GF_dict[arg2[1]].type != "int":
											sys.stderr.write("Chyba: Zly typ premennej\n")
											sys.exit(53)
										else:
											temp_value =  int(current_instruction.arg2_value) - int(GF_dict[arg2[1]].value)
											temp_var = IPPvariable("int", temp_value)
											TF_dict[arg1[1]] = temp_var
											#print(TF_dict[arg1[1]].type, TF_dict[arg1[1]].value )
							elif arg2[0] == "LF": ####################
								if LF_created == 1:
									if len(LF_list) == 0:
										sys.stderr.write("Chyba: Ramec neexistuje.\n")
										sys.exit(55)
									if arg2[1] not in LF_list[len(LF_list)-1]:
										sys.stderr.write("Chyba: Premenna neexistuje.\n")
										sys.exit(54)
									else:
										if LF_list[len(LF_list)-1][arg2[1]] == None:
											sys.stderr.write("Chyba: Premenna neinicializovana\n")
											sys.exit(56)
										else:
											if LF_list[len(LF_list)-1][arg2[1]].type != "int":
												sys.stderr.write("Chyba: Zly typ premennej\n")
												sys.exit(53)
											else:
												temp_value = int(current_instruction.arg2_value) - int(LF_list[len(LF_list)-1][arg2[1]].value)
												temp_var = IPPvariable("int", temp_value)
												TF_dict[arg1[1]] = temp_var
												#print(TF_dict[arg1[1]].type, TF_dict[arg1[1]].value )
								else:
									sys.stderr.write("Chyba: Ramec neexistuje.\n")
									sys.exit(55)								
							elif arg2[0] == "TF": ####################
								if TF_created == 1:
									if arg2[1] not in TF_dict:
										sys.stderr.write("Chyba: Premenna neexistuje.\n")
										sys.exit(54)
									else:
										if TF_dict[arg2[1]] == None:
											sys.stderr.write("Chyba: Premenna neinicializovana\n")
											sys.exit(56)
										else:
											if TF_dict[arg2[1]].type != "int":
												sys.stderr.write("Chyba: Zly typ premennej\n")
												sys.exit(53)
											else:
												temp_value = int(current_instruction.arg2_value) - int(TF_dict[arg2[1]].value)
												temp_var = IPPvariable("int", temp_value)
												TF_dict[arg1[1]] = temp_var
												#print(TF_dict[arg1[1]].type, TF_dict[arg1[1]].value )
								else:
									sys.stderr.write("Chyba: Ramec neexistuje.\n")
									sys.exit(55)
											
						elif current_instruction.arg2_type == "var" and current_instruction.arg3_type == "var":
							arg2 = parse_variable(current_instruction.arg2_value)
							arg3 = parse_variable(current_instruction.arg3_value)
							if arg2[0] == "GF":
								if arg2[1] not in GF_dict:
									sys.stderr.write("Chyba: Premenna neexistuje. \n")
									sys.exit(54)
								else:
									if GF_dict[arg2[1]] == None:
										sys.stderr.write("Chyba: Premenna neinicializovana\n")
										sys.exit(56)
									else:
										if GF_dict[arg2[1]].type != "int":
											sys.stderr.write("Chyba: Zly typ premennej\n")
											sys.exit(53)
										else:
											###
											if arg3[0] == "GF":
												if arg3[1] not in GF_dict:
													sys.stderr.write("Chyba: Premenna neexistuje. \n")
													sys.exit(54)
												else:
													if GF_dict[arg3[1]] == None:
														sys.stderr.write("Chyba: Premenna neinicializovana\n")
														sys.exit(56)
													else:
														if GF_dict[arg3[1]].type != "int":
															sys.stderr.write("Chyba: Zly typ premennej\n")
															sys.exit(53)
														else:
															temp_value = int(GF_dict[arg2[1]].value) - int(GF_dict[arg3[1]].value)
															temp_var = IPPvariable("int", temp_value)
															TF_dict[arg1[1]] = temp_var
															#print(TF_dict[arg1[1]].type, TF_dict[arg1[1]].value )
	##
											elif arg3[0] == "LF": ####################
												if LF_created == 1:
													if len(LF_list) == 0:
														sys.stderr.write("Chyba: Ramec neexistuje.\n")
														sys.exit(55)
													if arg3[1] not in LF_list[len(LF_list)-1]:
														sys.stderr.write("Chyba: Premenna neexistuje.\n")
														sys.exit(54)
													else:
														if LF_list[len(LF_list)-1][arg3[1]] == None:
															sys.stderr.write("Chyba: Premenna neinicializovana\n")
															sys.exit(56)
														else:
															if LF_list[len(LF_list)-1][arg3[1]].type != "int":
																sys.stderr.write("Chyba: Zly typ premennej\n")
																sys.exit(53)
															else:
																temp_value = int(GF_dict[arg2[1]].value) - int(LF_list[len(LF_list)-1][arg3[1]].value)
																temp_var = IPPvariable("int", temp_value)
																TF_dict[arg1[1]] = temp_var
																#print(TF_dict[arg1[1]].type, TF_dict[arg1[1]].value )
												else:
													sys.stderr.write("Chyba: Ramec neexistuje.\n")
													sys.exit(55)								
											elif arg3[0] == "TF": ####################
												if TF_created == 1:
													if arg3[1] not in TF_dict:
														sys.stderr.write("Chyba: Premenna neexistuje.\n")
														sys.exit(54)
													else:
														if TF_dict[arg3[1]] == None:
															sys.stderr.write("Chyba: Premenna neinicializovana\n")
															sys.exit(56)
														else:
															if TF_dict[arg3[1]].type != "int":
																sys.stderr.write("Chyba: Zly typ premennej\n")
																sys.exit(53)
															else:
																temp_value = int(GF_dict[arg2[1]].value) - int(TF_dict[arg3[1]].value)
																temp_var = IPPvariable("int", temp_value)
																TF_dict[arg1[1]] = temp_var
																#print(TF_dict[arg1[1]].type, TF_dict[arg1[1]].value )
												else:
													sys.stderr.write("Chyba: Ramec neexistuje.\n")
													sys.exit(55)
							elif arg2[0] == "LF": ####################
								if LF_created == 1:
									if len(LF_list) == 0:
										sys.stderr.write("Chyba: Ramec neexistuje.\n")
										sys.exit(55)
									if arg2[1] not in LF_list[len(LF_list)-1]:
										sys.stderr.write("Chyba: Premenna neexistuje.\n")
										sys.exit(54)
									else:
										if LF_list[len(LF_list)-1][arg2[1]] == None:
											sys.stderr.write("Chyba: Premenna neinicializovana\n")
											sys.exit(56)
										else:
											if LF_list[len(LF_list)-1][arg2[1]].type != "int":
												sys.stderr.write("Chyba: Zly typ premennej\n")
												sys.exit(53)
											else:
												if arg3[0] == "GF":
													if arg3[1] not in GF_dict:
														sys.stderr.write("Chyba: Premenna neexistuje. \n")
														sys.exit(54)
													else:
														if GF_dict[arg3[1]] == None:
															sys.stderr.write("Chyba: Premenna neinicializovana\n")
															sys.exit(56)
														else:
															if GF_dict[arg3[1]].type != "int":
																sys.stderr.write("Chyba: Zly typ premennej\n")
																sys.exit(53)
															else:
																temp_value = int(LF_list[len(LF_list)-1][arg2[1]].value) - int(GF_dict[arg3[1]].value)
																temp_var = IPPvariable("int", temp_value)
																TF_dict[arg1[1]] = temp_var
																#print(TF_dict[arg1[1]].type, TF_dict[arg1[1]].value )
		##
												elif arg3[0] == "LF": ####################
													if LF_created == 1:
														if len(LF_list) == 0:
															sys.stderr.write("Chyba: Ramec neexistuje.\n")
															sys.exit(55)
														if arg3[1] not in LF_list[len(LF_list)-1]:
															sys.stderr.write("Chyba: Premenna neexistuje.\n")
															sys.exit(54)
														else:
															if LF_list[len(LF_list)-1][arg3[1]] == None:
																sys.stderr.write("Chyba: Premenna neinicializovana\n")
																sys.exit(56)
															else:
																if LF_list[len(LF_list)-1][arg3[1]].type != "int":
																	sys.stderr.write("Chyba: Zly typ premennej\n")
																	sys.exit(53)
																else:
																	temp_value = int(LF_list[len(LF_list)-1][arg2[1]].value) - int(LF_list[len(LF_list)-1][arg3[1]].value)
																	temp_var = IPPvariable("int", temp_value)
																	TF_dict[arg1[1]] = temp_var
																	#print(TF_dict[arg1[1]].type, TF_dict[arg1[1]].value )
													else:
														sys.stderr.write("Chyba: Ramec neexistuje.\n")
														sys.exit(55)								
												elif arg3[0] == "TF": ####################
													if TF_created == 1:
														if arg3[1] not in TF_dict:
															sys.stderr.write("Chyba: Premenna neexistuje.\n")
															sys.exit(54)
														else:
															if TF_dict[arg3[1]] == None:
																sys.stderr.write("Chyba: Premenna neinicializovana\n")
																sys.exit(56)
															else:
																if TF_dict[arg3[1]].type != "int":
																	sys.stderr.write("Chyba: Zly typ premennej\n")
																	sys.exit(53)
																else:
																	temp_value = int(LF_list[len(LF_list)-1][arg2[1]].value) - int(TF_dict[arg3[1]].value)
																	temp_var = IPPvariable("int", temp_value)
																	TF_dict[arg1[1]] = temp_var
																	#print(TF_dict[arg1[1]].type, TF_dict[arg1[1]].value )
													else:
														sys.stderr.write("Chyba: Ramec neexistuje.\n")
														sys.exit(55)
								else:
									sys.stderr.write("Chyba: Ramec neexistuje.\n")
									sys.exit(55)								
							elif arg2[0] == "TF": ####################
								if TF_created == 1:
									if arg2[1] not in TF_dict:
										sys.stderr.write("Chyba: Premenna neexistuje.\n")
										sys.exit(54)
									else:
										if TF_dict[arg2[1]] == None:
											sys.stderr.write("Chyba: Premenna neinicializovana\n")
											sys.exit(56)
										else:
											if TF_dict[arg2[1]].type != "int":
												sys.stderr.write("Chyba: Zly typ premennej\n")
												sys.exit(53)
											else:
												if arg3[0] == "GF":
													if arg3[1] not in GF_dict:
														sys.stderr.write("Chyba: Premenna neexistuje. \n")
														sys.exit(54)
													else:
														if GF_dict[arg3[1]] == None:
															sys.stderr.write("Chyba: Premenna neinicializovana\n")
															sys.exit(56)
														else:
															if GF_dict[arg3[1]].type != "int":
																sys.stderr.write("Chyba: Zly typ premennej\n")
																sys.exit(53)
															else:
																temp_value = int(TF_dict[arg2[1]].value) - int(GF_dict[arg3[1]].value)
																temp_var = IPPvariable("int", temp_value)
																TF_dict[arg1[1]] = temp_var
																#print(TF_dict[arg1[1]].type, TF_dict[arg1[1]].value )
		##
												elif arg3[0] == "LF": ####################
													if LF_created == 1:
														if len(LF_list) == 0:
															sys.stderr.write("Chyba: Ramec neexistuje.\n")
															sys.exit(55)
														if arg3[1] not in LF_list[len(LF_list)-1]:
															sys.stderr.write("Chyba: Premenna neexistuje.\n")
															sys.exit(54)
														else:
															if LF_list[len(LF_list)-1][arg3[1]] == None:
																sys.stderr.write("Chyba: Premenna neinicializovana\n")
																sys.exit(56)
															else:
																if LF_list[len(LF_list)-1][arg3[1]].type != "int":
																	sys.stderr.write("Chyba: Zly typ premennej\n")
																	sys.exit(53)
																else:
																	temp_value = int(TF_dict[arg2[1]].value) - int(LF_list[len(LF_list)-1][arg3[1]].value)
																	temp_var = IPPvariable("int", temp_value)
																	TF_dict[arg1[1]] = temp_var
																	#print(TF_dict[arg1[1]].type, TF_dict[arg1[1]].value )
													else:
														sys.stderr.write("Chyba: Ramec neexistuje.\n")
														sys.exit(55)								
												elif arg3[0] == "TF": ####################
													if TF_created == 1:
														if arg3[1] not in TF_dict:
															sys.stderr.write("Chyba: Premenna neexistuje.\n")
															sys.exit(54)
														else:
															if TF_dict[arg3[1]] == None:
																sys.stderr.write("Chyba: Premenna neinicializovana\n")
																sys.exit(56)
															else:
																if TF_dict[arg3[1]].type != "int":
																	sys.stderr.write("Chyba: Zly typ premennej\n")
																	sys.exit(53)
																else:
																	temp_value = int(TF_dict[arg2[1]].value) - int(TF_dict[arg3[1]].value)
																	temp_var = IPPvariable("int", temp_value)
																	TF_dict[arg1[1]] = temp_var
																	#print(TF_dict[arg1[1]].type, TF_dict[arg1[1]].value )
													else:
														sys.stderr.write("Chyba: Ramec neexistuje.\n")
														sys.exit(55)
								else:
									sys.stderr.write("Chyba: Ramec neexistuje.\n")
									sys.exit(55)						
				else:
					sys.stderr.write("Chyba: Ramec neexistuje.\n")
					sys.exit(55)
			#print("SUB OK")	
	###############################################################
		elif current_instruction.opcode.upper() == "MUL":
			arg1 = parse_variable(current_instruction.arg1_value)
			if arg1[0] == "GF":
				if arg1[1] not in GF_dict:
					sys.stderr.write("Chyba: Premenna neexistuje.\n")
					sys.exit(54)
				else:
					if current_instruction.arg2_type == "int" and current_instruction.arg3_type == "int":
						temp_value = int(current_instruction.arg2_value) * int(current_instruction.arg3_value)
						temp_var = IPPvariable("int", temp_value)
						GF_dict[arg1[1]] = temp_var
						#print(GF_dict[arg1[1]].type, GF_dict[arg1[1]].value )
						
					elif current_instruction.arg2_type == "var" and current_instruction.arg3_type == "int":
						arg2 = parse_variable(current_instruction.arg2_value)
						if arg2[0] == "GF":
							if arg2[1] not in GF_dict:
								sys.stderr.write("Chyba: Premenna neexistuje. \n")
								sys.exit(54)
							else:
								if GF_dict[arg2[1]] == None:
									sys.stderr.write("Chyba: Premenna neinicializovana\n")
									sys.exit(56)
								else:
									if GF_dict[arg2[1]].type != "int":
										sys.stderr.write("Chyba: Zly typ premennej\n")
										sys.exit(53)
									else:
										temp_value = int(GF_dict[arg2[1]].value) * int(current_instruction.arg3_value)
										temp_var = IPPvariable("int", temp_value)
										GF_dict[arg1[1]] = temp_var
										#print(GF_dict[arg1[1]].type, GF_dict[arg1[1]].value )
										
					elif current_instruction.arg2_type == "int" and current_instruction.arg3_type == "var":
						arg2 = parse_variable(current_instruction.arg3_value)
						if arg2[0] == "GF":
							if arg2[1] not in GF_dict:
								sys.stderr.write("Chyba: Premenna neexistuje. \n")
								sys.exit(54)
							else:
								if GF_dict[arg2[1]] == None:
									sys.stderr.write("Chyba: Premenna neinicializovana\n")
									sys.exit(56)
								else:
									if GF_dict[arg2[1]].type != "int":
										sys.stderr.write("Chyba: Zly typ premennej\n")
										sys.exit(53)
									else:
										temp_value = int(current_instruction.arg2_value) * int(GF_dict[arg2[1]].value)
										temp_var = IPPvariable("int", temp_value)
										GF_dict[arg1[1]] = temp_var
										#print(GF_dict[arg1[1]].type, GF_dict[arg1[1]].value )
										
					elif current_instruction.arg2_type == "var" and current_instruction.arg3_type == "var":
						arg2 = parse_variable(current_instruction.arg2_value)
						arg3 = parse_variable(current_instruction.arg3_value)
						if arg2[0] == "GF":
							if arg2[1] not in GF_dict:
								sys.stderr.write("Chyba: Premenna neexistuje. \n")
								sys.exit(54)
							else:
								if GF_dict[arg2[1]] == None:
									sys.stderr.write("Chyba: Premenna neinicializovana\n")
									sys.exit(56)
								else:
									if GF_dict[arg2[1]].type != "int":
										sys.stderr.write("Chyba: Zly typ premennej\n")
										sys.exit(53)
									else:
										###
										if arg3[0] == "GF":
											if arg3[1] not in GF_dict:
												sys.stderr.write("Chyba: Premenna neexistuje. \n")
												sys.exit(54)
											else:
												if GF_dict[arg3[1]] == None:
													sys.stderr.write("Chyba: Premenna neinicializovana\n")
													sys.exit(56)
												else:
													if GF_dict[arg3[1]].type != "int":
														sys.stderr.write("Chyba: Zly typ premennej\n")
														sys.exit(53)
													else:
														temp_value = int(GF_dict[arg2[1]].value) * int(GF_dict[arg3[1]].value)
														temp_var = IPPvariable("int", temp_value)
														GF_dict[arg1[1]] = temp_var
														#print(GF_dict[arg1[1]].type, GF_dict[arg1[1]].value )											
					else:
						sys.stderr.write("Chyba: Zly typ premennej \n")
						sys.exit(53)
			#print("MUL OK")		
#################################################################
		elif current_instruction.opcode.upper() == "IDIV":
			arg1 = parse_variable(current_instruction.arg1_value)
			if arg1[0] == "GF":
				if arg1[1] not in GF_dict:
					sys.stderr.write("Chyba: Premenna neexistuje.\n")
					sys.exit(54)
				else:
					if current_instruction.arg2_type == "int" and current_instruction.arg3_type == "int":
						if int(current_instruction.arg3_value) == 0:
							sys.stderr.write("Chyba: Delenie nulou. \n")
							sys.exit(57)
						temp_value = int(current_instruction.arg2_value) // int(current_instruction.arg3_value)
						temp_var = IPPvariable("int", temp_value)
						GF_dict[arg1[1]] = temp_var
						#print(GF_dict[arg1[1]].type, GF_dict[arg1[1]].value )
						
					elif current_instruction.arg2_type == "var" and current_instruction.arg3_type == "int":
						arg2 = parse_variable(current_instruction.arg2_value)
						if arg2[0] == "GF":
							if arg2[1] not in GF_dict:
								sys.stderr.write("Chyba: Premenna neexistuje. \n")
								sys.exit(54)
							else:
								if GF_dict[arg2[1]] == None:
									sys.stderr.write("Chyba: Premenna neinicializovana\n")
									sys.exit(56)
								else:
									if GF_dict[arg2[1]].type != "int":
										sys.stderr.write("Chyba: Zly typ premennej\n")
										sys.exit(53)
									else:
										if int(current_instruction.arg3_value) == 0:
											sys.stderr.write("Chyba: Delenie nulou. \n")
											sys.exit(57)
										temp_value = int(GF_dict[arg2[1]].value) // int(current_instruction.arg3_value)
										temp_var = IPPvariable("int", temp_value)
										GF_dict[arg1[1]] = temp_var
										#print(GF_dict[arg1[1]].type, GF_dict[arg1[1]].value )
										
					elif current_instruction.arg2_type == "int" and current_instruction.arg3_type == "var":
						arg2 = parse_variable(current_instruction.arg3_value)
						if arg2[0] == "GF":
							if arg2[1] not in GF_dict:
								sys.stderr.write("Chyba: Premenna neexistuje. \n")
								sys.exit(54)
							else:
								if GF_dict[arg2[1]] == None:
									sys.stderr.write("Chyba: Premenna neinicializovana\n")
									sys.exit(56)
								else:
									if GF_dict[arg2[1]].type != "int":
										sys.stderr.write("Chyba: Zly typ premennej\n")
										sys.exit(53)
									else:
										if int(GF_dict[arg2[1]].value) == 0:
											sys.stderr.write("Chyba: Delenie nulou. \n")
											sys.exit(57)											
										temp_value = int(current_instruction.arg2_value) // int(GF_dict[arg2[1]].value)
										temp_var = IPPvariable("int", temp_value)
										GF_dict[arg1[1]] = temp_var
										#print(GF_dict[arg1[1]].type, GF_dict[arg1[1]].value )
										
					elif current_instruction.arg2_type == "var" and current_instruction.arg3_type == "var":
						arg2 = parse_variable(current_instruction.arg2_value)
						arg3 = parse_variable(current_instruction.arg3_value)
						if arg2[0] == "GF":
							if arg2[1] not in GF_dict:
								sys.stderr.write("Chyba: Premenna neexistuje. \n")
								sys.exit(54)
							else:
								if GF_dict[arg2[1]] == None:
									sys.stderr.write("Chyba: Premenna neinicializovana\n")
									sys.exit(56)
								else:
									if GF_dict[arg2[1]].type != "int":
										sys.stderr.write("Chyba: Zly typ premennej\n")
										sys.exit(53)
									else:
										###
										if arg3[0] == "GF":
											if arg3[1] not in GF_dict:
												sys.stderr.write("Chyba: Premenna neexistuje. \n")
												sys.exit(54)
											else:
												if GF_dict[arg3[1]] == None:
													sys.stderr.write("Chyba: Premenna neinicializovana\n")
													sys.exit(56)
												else:
													if GF_dict[arg3[1]].type != "int":
														sys.stderr.write("Chyba: Zly typ premennej\n")
														sys.exit(53)
													else:
														if int(GF_dict[arg3[1]].value) == 0:
															sys.stderr.write("Chyba: Delenie nulou. \n")
															sys.exit(57)
														temp_value = int(GF_dict[arg2[1]].value) // int(GF_dict[arg3[1]].value)
														temp_var = IPPvariable("int", temp_value)
														GF_dict[arg1[1]] = temp_var
														#print(GF_dict[arg1[1]].type, GF_dict[arg1[1]].value )											
					else:
						sys.stderr.write("Chyba: Zly typ premennej \n")
						sys.exit(53)
			#print("IDIV OK")
###############################################################
		elif current_instruction.opcode.upper() == "LT":
			arg1 = parse_variable(current_instruction.arg1_value)
			if arg1[0] == "GF":
				if arg1[1] not in GF_dict:
					sys.stderr.write("Chyba: Premenna neexistuje.\n")
					sys.exit(54)
				else:
					if current_instruction.arg2_type == current_instruction.arg3_type and (current_instruction.arg2_type == "int" or current_instruction.arg2_type == "string" or current_instruction.arg2_type == "bool"):
						if current_instruction.arg2_type == "int":
							if int(current_instruction.arg2_value) < int(current_instruction.arg3_value):
								temp_var = IPPvariable("bool","true")
								GF_dict[arg1[1]] = temp_var
							else:
								temp_var = IPPvariable("bool","false")
								GF_dict[arg1[1]] = temp_var	
							#print(GF_dict[arg1[1]].type, GF_dict[arg1[1]].value)
							
						else:
							if current_instruction.arg2_value < current_instruction.arg3_value:
								temp_var = IPPvariable("bool","true")
								GF_dict[arg1[1]] = temp_var
							else:
								temp_var = IPPvariable("bool","false")
								GF_dict[arg1[1]] = temp_var	
							#print(GF_dict[arg1[1]].type, GF_dict[arg1[1]].value)
		
					elif current_instruction.arg2_type == "var" and (current_instruction.arg3_type == "int" or current_instruction.arg3_type == "string" or current_instruction.arg3_type == "bool"):
						arg2 = parse_variable(current_instruction.arg2_value)
						if arg2[0] == "GF":
							if arg2[1] not in GF_dict:
								sys.stderr.write("Chyba: Premenna neexistuje. \n")
								sys.exit(54)
							else:
								if GF_dict[arg2[1]] == None:
									sys.stderr.write("Chyba: Premenna neinicializovana\n")
									sys.exit(56)
								else:
									if GF_dict[arg2[1]].type != current_instruction.arg3_type:
										sys.stderr.write("Chyba: Zly typ premennej\n")
										sys.exit(53)
									else:
										if current_instruction.arg3_type == "int":
											if int(GF_dict[arg2[1]].value) < int(current_instruction.arg3_value):
												temp_var = IPPvariable("bool","true")
												GF_dict[arg1[1]] = temp_var
											else:
												temp_var = IPPvariable("bool","false")
												GF_dict[arg1[1]] = temp_var	
											#print(GF_dict[arg1[1]].type, GF_dict[arg1[1]].value)
							
										else:
											if GF_dict[arg2[1]].value < current_instruction.arg3_value:
												temp_var = IPPvariable("bool","true")
												GF_dict[arg1[1]] = temp_var
											else:
												temp_var = IPPvariable("bool","false")
												GF_dict[arg1[1]] = temp_var	
											#print(GF_dict[arg1[1]].type, GF_dict[arg1[1]].value)
											
					elif (current_instruction.arg2_type == "int" or current_instruction.arg2_type == "string" or current_instruction.arg2_type == "bool") and current_instruction.arg3_type == "var":
						arg2 = parse_variable(current_instruction.arg3_value)
						if arg2[0] == "GF":
							if arg2[1] not in GF_dict:
								sys.stderr.write("Chyba: Premenna neexistuje. \n")
								sys.exit(54)
							else:
								if GF_dict[arg2[1]] == None:
									sys.stderr.write("Chyba: Premenna neinicializovana\n")
									sys.exit(56)
								else:
									if GF_dict[arg2[1]].type != current_instruction.arg2_type:
										sys.stderr.write("Chyba: Zly typ premennej\n")
										sys.exit(53)
									else:
										if current_instruction.arg2_type == "int":
											if int(current_instruction.arg2_value) < int(GF_dict[arg2[1]].value):
												temp_var = IPPvariable("bool","true")
												GF_dict[arg1[1]] = temp_var
											else:
												temp_var = IPPvariable("bool","false")
												GF_dict[arg1[1]] = temp_var	
											#print(GF_dict[arg1[1]].type, GF_dict[arg1[1]].value)
							
										else:
											if current_instruction.arg2_value < GF_dict[arg2[1]].value:
												temp_var = IPPvariable("bool","true")
												GF_dict[arg1[1]] = temp_var
											else:
												temp_var = IPPvariable("bool","false")
												GF_dict[arg1[1]] = temp_var	
											#print(GF_dict[arg1[1]].type, GF_dict[arg1[1]].value)

					elif current_instruction.arg2_type == "var" and current_instruction.arg3_type == "var":
						arg2 = parse_variable(current_instruction.arg2_value)
						arg3 = parse_variable(current_instruction.arg3_value)
						if arg2[0] == "GF":
							if arg2[1] not in GF_dict:
								sys.stderr.write("Chyba: Premenna neexistuje. \n")
								sys.exit(54)
							else:
								if GF_dict[arg2[1]] == None:
									sys.stderr.write("Chyba: Premenna neinicializovana\n")
									sys.exit(56)
								else:
									###
									if arg3[0] == "GF":
										if arg3[1] not in GF_dict:
											sys.stderr.write("Chyba: Premenna neexistuje. \n")
											sys.exit(54)
										else:
											if GF_dict[arg3[1]] == None:
												sys.stderr.write("Chyba: Premenna neinicializovana\n")
												sys.exit(56)
											else:
												if  GF_dict[arg2[1]].type != GF_dict[arg3[1]].type and (GF_dict[arg2[1]].type == "int" or GF_dict[arg2[1]].type == "string" or GF_dict[arg2[1]].type == "bool"):
													sys.stderr.write("Chyba: Zly typ premennej\n")
													sys.exit(53)
												else:
													if GF_dict[arg2[1]].type == "int":
														if int(GF_dict[arg2[1]].value) < int(GF_dict[arg3[1]].value):
															temp_var = IPPvariable("bool","true")
															GF_dict[arg1[1]] = temp_var
														else:
															temp_var = IPPvariable("bool","false")
															GF_dict[arg1[1]] = temp_var	
														#print(GF_dict[arg1[1]].type, GF_dict[arg1[1]].value)
							
													else:
														if GF_dict[arg2[1]].value < GF_dict[arg3[1]].value:
															temp_var = IPPvariable("bool","true")
															GF_dict[arg1[1]] = temp_var
														else:
															temp_var = IPPvariable("bool","false")
															GF_dict[arg1[1]] = temp_var	
														#print(GF_dict[arg1[1]].type, GF_dict[arg1[1]].value)
					else:
						sys.stderr.write("Chyba: Zly typ premennej\n")
						sys.exit(53)											
####################################################################################		
		elif current_instruction.opcode.upper() == "GT":
			arg1 = parse_variable(current_instruction.arg1_value)
			if arg1[0] == "GF":
				if arg1[1] not in GF_dict:
					sys.stderr.write("Chyba: Premenna neexistuje.\n")
					sys.exit(54)
				else:
					if current_instruction.arg2_type == current_instruction.arg3_type and (current_instruction.arg2_type == "int" or current_instruction.arg2_type == "string" or current_instruction.arg2_type == "bool"):
						if current_instruction.arg2_type == "int":
							if int(current_instruction.arg2_value) > int(current_instruction.arg3_value):
								temp_var = IPPvariable("bool","true")
								GF_dict[arg1[1]] = temp_var
							else:
								temp_var = IPPvariable("bool","false")
								GF_dict[arg1[1]] = temp_var	
							#print(GF_dict[arg1[1]].type, GF_dict[arg1[1]].value)
							
						else:
							if current_instruction.arg2_value > current_instruction.arg3_value:
								temp_var = IPPvariable("bool","true")
								GF_dict[arg1[1]] = temp_var
							else:
								temp_var = IPPvariable("bool","false")
								GF_dict[arg1[1]] = temp_var	
							#print(GF_dict[arg1[1]].type, GF_dict[arg1[1]].value)
		
					elif current_instruction.arg2_type == "var" and (current_instruction.arg3_type == "int" or current_instruction.arg3_type == "string" or current_instruction.arg3_type == "bool"):
						arg2 = parse_variable(current_instruction.arg2_value)
						if arg2[0] == "GF":
							if arg2[1] not in GF_dict:
								sys.stderr.write("Chyba: Premenna neexistuje. \n")
								sys.exit(54)
							else:
								if GF_dict[arg2[1]] == None:
									sys.stderr.write("Chyba: Premenna neinicializovana\n")
									sys.exit(56)
								else:
									if GF_dict[arg2[1]].type != current_instruction.arg3_type:
										sys.stderr.write("Chyba: Zly typ premennej\n")
										sys.exit(53)
									else:
										if current_instruction.arg3_type == "int":
											if int(GF_dict[arg2[1]].value) > int(current_instruction.arg3_value):
												temp_var = IPPvariable("bool","true")
												GF_dict[arg1[1]] = temp_var
											else:
												temp_var = IPPvariable("bool","false")
												GF_dict[arg1[1]] = temp_var	
											#print(GF_dict[arg1[1]].type, GF_dict[arg1[1]].value)
							
										else:
											if GF_dict[arg2[1]].value > current_instruction.arg3_value:
												temp_var = IPPvariable("bool","true")
												GF_dict[arg1[1]] = temp_var
											else:
												temp_var = IPPvariable("bool","false")
												GF_dict[arg1[1]] = temp_var	
											#print(GF_dict[arg1[1]].type, GF_dict[arg1[1]].value)
											
					elif (current_instruction.arg2_type == "int" or current_instruction.arg2_type == "string" or current_instruction.arg2_type == "bool") and current_instruction.arg3_type == "var":
						arg2 = parse_variable(current_instruction.arg3_value)
						if arg2[0] == "GF":
							if arg2[1] not in GF_dict:
								sys.stderr.write("Chyba: Premenna neexistuje. \n")
								sys.exit(54)
							else:
								if GF_dict[arg2[1]] == None:
									sys.stderr.write("Chyba: Premenna neinicializovana\n")
									sys.exit(56)
								else:
									if GF_dict[arg2[1]].type != current_instruction.arg2_type:
										sys.stderr.write("Chyba: Zly typ premennej\n")
										sys.exit(53)
									else:
										if current_instruction.arg2_type == "int":
											if int(current_instruction.arg2_value) > int(GF_dict[arg2[1]].value):
												temp_var = IPPvariable("bool","true")
												GF_dict[arg1[1]] = temp_var
											else:
												temp_var = IPPvariable("bool","false")
												GF_dict[arg1[1]] = temp_var	
											#print(GF_dict[arg1[1]].type, GF_dict[arg1[1]].value)
							
										else:
											if current_instruction.arg2_value > GF_dict[arg2[1]].value:
												temp_var = IPPvariable("bool","true")
												GF_dict[arg1[1]] = temp_var
											else:
												temp_var = IPPvariable("bool","false")
												GF_dict[arg1[1]] = temp_var	
											#print(GF_dict[arg1[1]].type, GF_dict[arg1[1]].value)

					elif current_instruction.arg2_type == "var" and current_instruction.arg3_type == "var":
						arg2 = parse_variable(current_instruction.arg2_value)
						arg3 = parse_variable(current_instruction.arg3_value)
						if arg2[0] == "GF":
							if arg2[1] not in GF_dict:
								sys.stderr.write("Chyba: Premenna neexistuje. \n")
								sys.exit(54)
							else:
								if GF_dict[arg2[1]] == None:
									sys.stderr.write("Chyba: Premenna neinicializovana\n")
									sys.exit(56)
								else:
									###
									if arg3[0] == "GF":
										if arg3[1] not in GF_dict:
											sys.stderr.write("Chyba: Premenna neexistuje. \n")
											sys.exit(54)
										else:
											if GF_dict[arg3[1]] == None:
												sys.stderr.write("Chyba: Premenna neinicializovana\n")
												sys.exit(56)
											else:
												if  GF_dict[arg2[1]].type != GF_dict[arg3[1]].type and (GF_dict[arg2[1]].type == "int" or GF_dict[arg2[1]].type == "string" or GF_dict[arg2[1]].type == "bool"):
													sys.stderr.write("Chyba: Zly typ premennej\n")
													sys.exit(53)
												else:
													if GF_dict[arg2[1]].type == "int":
														if int(GF_dict[arg2[1]].value) > int(GF_dict[arg3[1]].value):
															temp_var = IPPvariable("bool","true")
															GF_dict[arg1[1]] = temp_var
														else:
															temp_var = IPPvariable("bool","false")
															GF_dict[arg1[1]] = temp_var	
														#print(GF_dict[arg1[1]].type, GF_dict[arg1[1]].value)
							
													else:
														if GF_dict[arg2[1]].value > GF_dict[arg3[1]].value:
															temp_var = IPPvariable("bool","true")
															GF_dict[arg1[1]] = temp_var
														else:
															temp_var = IPPvariable("bool","false")
															GF_dict[arg1[1]] = temp_var	
														#print(GF_dict[arg1[1]].type, GF_dict[arg1[1]].value)	
					else:
						sys.stderr.write("Chyba: Zly typ premennej\n")
						sys.exit(53)														
														
######################################################	
		elif current_instruction.opcode.upper() == "EQ":
			arg1 = parse_variable(current_instruction.arg1_value)
			if arg1[0] == "GF":
				if arg1[1] not in GF_dict:
					sys.stderr.write("Chyba: Premenna neexistuje.\n")
					sys.exit(54)
				else:
					if current_instruction.arg2_type == current_instruction.arg3_type and (current_instruction.arg2_type == "int" or current_instruction.arg2_type == "string" or current_instruction.arg2_type == "bool"):
						if current_instruction.arg2_type == "int":
							if int(current_instruction.arg2_value) == int(current_instruction.arg3_value):
								temp_var = IPPvariable("bool","true")
								GF_dict[arg1[1]] = temp_var
							else:
								temp_var = IPPvariable("bool","false")
								GF_dict[arg1[1]] = temp_var	
							#print(GF_dict[arg1[1]].type, GF_dict[arg1[1]].value)
							
						else:
							if current_instruction.arg2_value == current_instruction.arg3_value:
								temp_var = IPPvariable("bool","true")
								GF_dict[arg1[1]] = temp_var
							else:
								temp_var = IPPvariable("bool","false")
								GF_dict[arg1[1]] = temp_var	
							#print(GF_dict[arg1[1]].type, GF_dict[arg1[1]].value)
		
					elif current_instruction.arg2_type == "var" and (current_instruction.arg3_type == "int" or current_instruction.arg3_type == "string" or current_instruction.arg3_type == "bool"):
						arg2 = parse_variable(current_instruction.arg2_value)
						if arg2[0] == "GF":
							if arg2[1] not in GF_dict:
								sys.stderr.write("Chyba: Premenna neexistuje. \n")
								sys.exit(54)
							else:
								if GF_dict[arg2[1]] == None:
									sys.stderr.write("Chyba: Premenna neinicializovana\n")
									sys.exit(56)
								else:
									if GF_dict[arg2[1]].type != current_instruction.arg3_type:
										sys.stderr.write("Chyba: Zly typ premennej\n")
										sys.exit(53)
									else:
										if current_instruction.arg3_type == "int":
											if int(GF_dict[arg2[1]].value) == int(current_instruction.arg3_value):
												temp_var = IPPvariable("bool","true")
												GF_dict[arg1[1]] = temp_var
											else:
												temp_var = IPPvariable("bool","false")
												GF_dict[arg1[1]] = temp_var	
											#print(GF_dict[arg1[1]].type, GF_dict[arg1[1]].value)
							
										else:
											if GF_dict[arg2[1]].value == current_instruction.arg3_value:
												temp_var = IPPvariable("bool","true")
												GF_dict[arg1[1]] = temp_var
											else:
												temp_var = IPPvariable("bool","false")
												GF_dict[arg1[1]] = temp_var	
											#print(GF_dict[arg1[1]].type, GF_dict[arg1[1]].value)
											
					elif (current_instruction.arg2_type == "int" or current_instruction.arg2_type == "string" or current_instruction.arg2_type == "bool") and current_instruction.arg3_type == "var":
						arg2 = parse_variable(current_instruction.arg3_value)
						if arg2[0] == "GF":
							if arg2[1] not in GF_dict:
								sys.stderr.write("Chyba: Premenna neexistuje. \n")
								sys.exit(54)
							else:
								if GF_dict[arg2[1]] == None:
									sys.stderr.write("Chyba: Premenna neinicializovana\n")
									sys.exit(56)
								else:
									if GF_dict[arg2[1]].type != current_instruction.arg2_type:
										sys.stderr.write("Chyba: Zly typ premennej\n")
										sys.exit(53)
									else:
										if current_instruction.arg2_type == "int":
											if int(current_instruction.arg2_value) == int(GF_dict[arg2[1]].value):
												temp_var = IPPvariable("bool","true")
												GF_dict[arg1[1]] = temp_var
											else:
												temp_var = IPPvariable("bool","false")
												GF_dict[arg1[1]] = temp_var	
											#print(GF_dict[arg1[1]].type, GF_dict[arg1[1]].value)
							
										else:
											if current_instruction.arg2_value == GF_dict[arg2[1]].value:
												temp_var = IPPvariable("bool","true")
												GF_dict[arg1[1]] = temp_var
											else:
												temp_var = IPPvariable("bool","false")
												GF_dict[arg1[1]] = temp_var	
											#print(GF_dict[arg1[1]].type, GF_dict[arg1[1]].value)

					elif current_instruction.arg2_type == "var" and current_instruction.arg3_type == "var":
						arg2 = parse_variable(current_instruction.arg2_value)
						arg3 = parse_variable(current_instruction.arg3_value)
						if arg2[0] == "GF":
							if arg2[1] not in GF_dict:
								sys.stderr.write("Chyba: Premenna neexistuje. \n")
								sys.exit(54)
							else:
								if GF_dict[arg2[1]] == None:
									sys.stderr.write("Chyba: Premenna neinicializovana\n")
									sys.exit(56)
								else:
									###
									if arg3[0] == "GF":
										if arg3[1] not in GF_dict:
											sys.stderr.write("Chyba: Premenna neexistuje. \n")
											sys.exit(54)
										else:
											if GF_dict[arg3[1]] == None:
												sys.stderr.write("Chyba: Premenna neinicializovana\n")
												sys.exit(56)
											else:
												if  GF_dict[arg2[1]].type != GF_dict[arg3[1]].type and (GF_dict[arg2[1]].type == "int" or GF_dict[arg2[1]].type == "string" or GF_dict[arg2[1]].type == "bool"):
													sys.stderr.write("Chyba: Zly typ premennej\n")
													sys.exit(53)
												else:
													if GF_dict[arg2[1]].type == "int":
														if int(GF_dict[arg2[1]].value) == int(GF_dict[arg3[1]].value):
															temp_var = IPPvariable("bool","true")
															GF_dict[arg1[1]] = temp_var
														else:
															temp_var = IPPvariable("bool","false")
															GF_dict[arg1[1]] = temp_var	
														#print(GF_dict[arg1[1]].type, GF_dict[arg1[1]].value)
							
													else:
														if GF_dict[arg2[1]].value == GF_dict[arg3[1]].value:
															temp_var = IPPvariable("bool","true")
															GF_dict[arg1[1]] = temp_var
														else:
															temp_var = IPPvariable("bool","false")
															GF_dict[arg1[1]] = temp_var	
														#print(GF_dict[arg1[1]].type, GF_dict[arg1[1]].value)
					else:
						sys.stderr.write("Chyba: Zly typ premennej\n")
						sys.exit(53)
#########################################################
		elif current_instruction.opcode.upper() == "AND":
			arg1 = parse_variable(current_instruction.arg1_value)
			if arg1[0] == "GF":
				if arg1[1] not in GF_dict:
					sys.stderr.write("Chyba: Premenna neexistuje.\n")
					sys.exit(54)
				else:
					if current_instruction.arg2_type == current_instruction.arg3_type and current_instruction.arg2_type == "bool":
						if current_instruction.arg2_value == current_instruction.arg3_value and current_instruction.arg2_value == "true":
							temp_var = IPPvariable("bool","true")
							GF_dict[arg1[1]] = temp_var
						else:
							temp_var = IPPvariable("bool","false")
							GF_dict[arg1[1]] = temp_var
						#print(GF_dict[arg1[1]].type, GF_dict[arg1[1]].value)
						
					elif current_instruction.arg2_type == "var" and current_instruction.arg3_type == "bool":
						arg2 = parse_variable(current_instruction.arg2_value)
						if arg2[0] == "GF":
							if arg2[1] not in GF_dict:
								sys.stderr.write("Chyba: Premenna neexistuje. \n")
								sys.exit(54)
							else:
								if GF_dict[arg2[1]] == None:
									sys.stderr.write("Chyba: Premenna neinicializovana\n")
									sys.exit(56)
								else:
									if GF_dict[arg2[1]].type != "bool":
										sys.stderr.write("Chyba: Zly typ premennej\n")
										sys.exit(53)						
									else:
										if GF_dict[arg2[1]].value == current_instruction.arg3_value and GF_dict[arg2[1]].value == "true":
											temp_var = IPPvariable("bool","true")
											GF_dict[arg1[1]] = temp_var
										else:
											temp_var = IPPvariable("bool","false")
											GF_dict[arg1[1]] = temp_var
										#print(GF_dict[arg1[1]].type, GF_dict[arg1[1]].value)
										
					elif current_instruction.arg2_type == "bool" and current_instruction.arg3_type == "var":
						arg2 = parse_variable(current_instruction.arg3_value)
						if arg2[0] == "GF":
							if arg2[1] not in GF_dict:
								sys.stderr.write("Chyba: Premenna neexistuje. \n")
								sys.exit(54)
							else:
								if GF_dict[arg2[1]] == None:
									sys.stderr.write("Chyba: Premenna neinicializovana\n")
									sys.exit(56)
								else:
									if GF_dict[arg2[1]].type != "bool":
										sys.stderr.write("Chyba: Zly typ premennej\n")
										sys.exit(53)						
									else:
										if GF_dict[arg2[1]].value == current_instruction.arg2_value and GF_dict[arg2[1]].value == "true":
											temp_var = IPPvariable("bool","true")
											GF_dict[arg1[1]] = temp_var
										else:
											temp_var = IPPvariable("bool","false")
											GF_dict[arg1[1]] = temp_var
										#print(GF_dict[arg1[1]].type, GF_dict[arg1[1]].value)
										
					elif current_instruction.arg2_type == "var" and current_instruction.arg3_type == "var":
						arg2 = parse_variable(current_instruction.arg2_value)
						arg3 = parse_variable(current_instruction.arg3_value)
						if arg2[0] == "GF":
							if arg2[1] not in GF_dict:
								sys.stderr.write("Chyba: Premenna neexistuje. \n")
								sys.exit(54)
							else:
								if GF_dict[arg2[1]] == None:
									sys.stderr.write("Chyba: Premenna neinicializovana\n")
									sys.exit(56)
								else:									
										####
									if arg3[0] == "GF":
										if arg3[1] not in GF_dict:
											sys.stderr.write("Chyba: Premenna neexistuje. \n")
											sys.exit(54)
										else:
											if GF_dict[arg3[1]] == None:
												sys.stderr.write("Chyba: Premenna neinicializovana\n")
												sys.exit(56)
											else:	
												if GF_dict[arg2[1]].type != "bool" or GF_dict[arg2[1]].type != GF_dict[arg3[1]].type:
													sys.stderr.write("Chyba: Zly typ premennej\n")
													sys.exit(53)						
												else:
													if GF_dict[arg2[1]].value == GF_dict[arg3[1]].value and GF_dict[arg2[1]].value == "true":
														temp_var = IPPvariable("bool","true")
														GF_dict[arg1[1]] = temp_var
													else:
														temp_var = IPPvariable("bool","false")
														GF_dict[arg1[1]] = temp_var
													#print(GF_dict[arg1[1]].type, GF_dict[arg1[1]].value)
					else:
						sys.stderr.write("Chyba: Zly typ premennej\n")
						sys.exit(53)	
						
################################################	
		elif current_instruction.opcode.upper() == "OR":
			arg1 = parse_variable(current_instruction.arg1_value)
			if arg1[0] == "GF":
				if arg1[1] not in GF_dict:
					sys.stderr.write("Chyba: Premenna neexistuje.\n")
					sys.exit(54)
				else:
					if current_instruction.arg2_type == current_instruction.arg3_type and current_instruction.arg2_type == "bool":
						if current_instruction.arg2_value == current_instruction.arg3_value and current_instruction.arg2_value == "false":
							temp_var = IPPvariable("bool","false")
							GF_dict[arg1[1]] = temp_var
						else:
							temp_var = IPPvariable("bool","true")
							GF_dict[arg1[1]] = temp_var
						#print(GF_dict[arg1[1]].type, GF_dict[arg1[1]].value)
						
					elif current_instruction.arg2_type == "var" and current_instruction.arg3_type == "bool":
						arg2 = parse_variable(current_instruction.arg2_value)
						if arg2[0] == "GF":
							if arg2[1] not in GF_dict:
								sys.stderr.write("Chyba: Premenna neexistuje. \n")
								sys.exit(54)
							else:
								if GF_dict[arg2[1]] == None:
									sys.stderr.write("Chyba: Premenna neinicializovana\n")
									sys.exit(56)
								else:
									if GF_dict[arg2[1]].type != "bool":
										sys.stderr.write("Chyba: Zly typ premennej\n")
										sys.exit(53)						
									else:
										if GF_dict[arg2[1]].value == current_instruction.arg3_value and GF_dict[arg2[1]].value == "false":
											temp_var = IPPvariable("bool","false")
											GF_dict[arg1[1]] = temp_var
										else:
											temp_var = IPPvariable("bool","true")
											GF_dict[arg1[1]] = temp_var
										#print(GF_dict[arg1[1]].type, GF_dict[arg1[1]].value)
										
					elif current_instruction.arg2_type == "bool" and current_instruction.arg3_type == "var":
						arg2 = parse_variable(current_instruction.arg3_value)
						if arg2[0] == "GF":
							if arg2[1] not in GF_dict:
								sys.stderr.write("Chyba: Premenna neexistuje. \n")
								sys.exit(54)
							else:
								if GF_dict[arg2[1]] == None:
									sys.stderr.write("Chyba: Premenna neinicializovana\n")
									sys.exit(56)
								else:
									if GF_dict[arg2[1]].type != "bool":
										sys.stderr.write("Chyba: Zly typ premennej\n")
										sys.exit(53)						
									else:
										if GF_dict[arg2[1]].value == current_instruction.arg2_value and GF_dict[arg2[1]].value == "false":
											temp_var = IPPvariable("bool","false")
											GF_dict[arg1[1]] = temp_var
										else:
											temp_var = IPPvariable("bool","true")
											GF_dict[arg1[1]] = temp_var
										#print(GF_dict[arg1[1]].type, GF_dict[arg1[1]].value)
										
					elif current_instruction.arg2_type == "var" and current_instruction.arg3_type == "var":
						arg2 = parse_variable(current_instruction.arg2_value)
						arg3 = parse_variable(current_instruction.arg3_value)
						if arg2[0] == "GF":
							if arg2[1] not in GF_dict:
								sys.stderr.write("Chyba: Premenna neexistuje. \n")
								sys.exit(54)
							else:
								if GF_dict[arg2[1]] == None:
									sys.stderr.write("Chyba: Premenna neinicializovana\n")
									sys.exit(56)
								else:									
										####
									if arg3[0] == "GF":
										if arg3[1] not in GF_dict:
											sys.stderr.write("Chyba: Premenna neexistuje. \n")
											sys.exit(54)
										else:
											if GF_dict[arg3[1]] == None:
												sys.stderr.write("Chyba: Premenna neinicializovana\n")
												sys.exit(56)
											else:	
												if GF_dict[arg2[1]].type != "bool" or GF_dict[arg2[1]].type != GF_dict[arg3[1]].type:
													sys.stderr.write("Chyba: Zly typ premennej\n")
													sys.exit(53)						
												else:
													if GF_dict[arg2[1]].value == GF_dict[arg3[1]].value and GF_dict[arg2[1]].value == "false":
														temp_var = IPPvariable("bool","false")
														GF_dict[arg1[1]] = temp_var
													else:
														temp_var = IPPvariable("bool","true")
														GF_dict[arg1[1]] = temp_var
													#print(GF_dict[arg1[1]].type, GF_dict[arg1[1]].value)
					else:
						sys.stderr.write("Chyba: Zly typ premennej\n")
						sys.exit(53)
############################################	
		elif current_instruction.opcode.upper() == "NOT":
			arg1 = parse_variable(current_instruction.arg1_value)
			if arg1[0] == "GF":
				if arg1[1] not in GF_dict:
					sys.stderr.write("Chyba: Premenna neexistuje.\n")
					sys.exit(54)
				else:
					if current_instruction.arg2_type == "bool":
						if current_instruction.arg2_value == "true":
							temp_var = IPPvariable("bool", "false")
							GF_dict[arg1[1]] = temp_var
						else:
							temp_var = IPPvariable("bool", "true")
							GF_dict[arg1[1]] = temp_var
							
					elif current_instruction.arg2_type == "var":
						arg2 = parse_variable(current_instruction.arg2_value)
						if arg2[0] == "GF":
							if arg2[1] not in GF_dict:
								sys.stderr.write("Chyba: Premenna neexistuje. \n")
								sys.exit(54)
							else:
								if GF_dict[arg2[1]] == None:
									sys.stderr.write("Chyba: Premenna neinicializovana\n")
									sys.exit(56)
								else:
									if GF_dict[arg2[1]].type != "bool":
										sys.stderr.write("Chyba: Zly typ premennej\n")
										sys.exit(53)						
									else:
										if GF_dict[arg2[1]].value == "true":
											temp_var = IPPvariable("bool", "false")
											GF_dict[arg1[1]] = temp_var
										else:
											temp_var = IPPvariable("bool", "true")
											GF_dict[arg1[1]] = temp_var
					else:
						sys.stderr.write("Chyba: Zly typ premennej\n")
						sys.exit(53)
################################################
		elif current_instruction.opcode.upper() == "WRITE":
			if current_instruction.arg1_type == "var":
				arg1 = parse_variable(current_instruction.arg1_value)
				if arg1[0] == "GF":
					if arg1[1] not in GF_dict:
						sys.stderr.write("Chyba: Premenna neexistuje. \n")
						sys.exit(54)
					else:
						if GF_dict[arg1[1]] == None:
							sys.stderr.write("Chyba: Premenna neinicializovana\n")
							sys.exit(56)
						else:
							if GF_dict[arg1[1]].type == "bool":
								if GF_dict[arg1[1]].value == "true":
									print("true")
								elif GF_dict[arg1[1]].value == "false":
									print("false")
							elif GF_dict[arg1[1]].type == "string":
								print(parse_string(GF_dict[arg1[1]].value))
							else:
								print(GF_dict[arg1[1]].value)
				elif arg1[0] == "LF":
					if LF_created == 1:
						if len(LF_list) == 0:
							sys.stderr.write("Chyba: Ramec neexistuje.\n")
							sys.exit(55)
						if arg1[1] not in LF_list[len(LF_list)-1]:
							sys.stderr.write("Chyba: Premenna neexistuje. \n")
							sys.exit(54)
						else:
							if LF_list[len(LF_list)-1][arg1[1]] == None:
								sys.stderr.write("Chyba: Premenna neinicializovana\n")
								sys.exit(56)
							else:
								if LF_list[len(LF_list)-1][arg1[1]].type == "bool":
									if LF_list[len(LF_list)-1][arg1[1]].value == "true":
										print("true")
									elif LF_list[len(LF_list)-1][arg1[1]].value == "false":
										print("false")
								elif LF_list[len(LF_list)-1][arg1[1]].type == "string":
									print(parse_string(LF_list[len(LF_list)-1][arg1[1]].value))
								else:
									print(LF_list[len(LF_list)-1][arg1[1]].value)
					else:
						sys.stderr.write("Chyba: Ramec neexistuje.\n")
						sys.exit(55)
				if arg1[0] == "TF":
					if TF_created == 1:
						if arg1[1] not in TF_dict:
							sys.stderr.write("Chyba: Premenna neexistuje. \n")
							sys.exit(54)
						else:
							if TF_dict[arg1[1]] == None:
								sys.stderr.write("Chyba: Premenna neinicializovana\n")
								sys.exit(56)
							else:
								if TF_dict[arg1[1]].type == "bool":
									if TF_dict[arg1[1]].value == "true":
										print("true")
									elif TF_dict[arg1[1]].value == "false":
										print("false")
								elif TF_dict[arg1[1]].type == "string":
									print(parse_string(TF_dict[arg1[1]].value))
								else:
									print(TF_dict[arg1[1]].value)
					else:
						sys.stderr.write("Chyba: Ramec neexistuje.\n")
						sys.exit(55)						
			elif current_instruction.arg1_type == "bool":
				if current_instruction.arg1_value == "true":
					print("true")
				elif current_instruction.arg1_value == "false":
					print("false")
			elif current_instruction.arg1_type == "int":
				print(current_instruction.arg1_value)
			elif current_instruction.arg1_type == "string":
				print(parse_string(current_instruction.arg1_value))
			else:
				sys.stderr.write("Chyba: Zly typ premennej\n")
				sys.exit(53)
#############################################
		elif current_instruction.opcode.upper() == "PUSHS":
			if current_instruction.arg1_type == "int" or current_instruction.arg1_type == "bool" or current_instruction.arg1_type == "string":
				data_stack.append(current_instruction.arg1_value)
				#print(data_stack)
			elif current_instruction.arg1_type == "var":
				arg1 = parse_variable(current_instruction.arg1_value)
				if arg1[0] == "GF":
					if arg1[1] not in GF_dict:
						sys.stderr.write("Chyba: Premenna neexistuje. \n")
						sys.exit(54)
					else:
						if GF_dict[arg1[1]] == None:
							sys.stderr.write("Chyba: Premenna neinicializovana\n")
							sys.exit(56)
						else:
							data_stack.append(GF_dict[arg1[1]].value)
						#print(data_stack)
				elif arg1[0] == "LF":
					if LF_created == 1:
						if len(LF_list) == 0:
							sys.stderr.write("Chyba: Ramec neexistuje.\n")
							sys.exit(55)
						if arg1[1] not in LF_list[len(LF_list)-1]:
							sys.stderr.write("Chyba: Premenna neexistuje. \n")
							sys.exit(54)
						else:
							if LF_list[len(LF_list)-1][arg1[1]] == None:
								sys.stderr.write("Chyba: Premenna neinicializovana\n")
								sys.exit(56)
							else:
								data_stack.append(LF_list[len(LF_list)-1][arg1[1]].value)
							#print(data_stack)
					else:
						sys.stderr.write("Chyba: Ramec neexistuje.\n")
						sys.exit(55)
				elif arg1[0] == "TF":
					if TF_created == 1:
						if arg1[1] not in TF_dict:
							sys.stderr.write("Chyba: Premenna neexistuje. \n")
							sys.exit(54)
						else:
							if TF_dict[arg1[1]] == None:
								sys.stderr.write("Chyba: Premenna neinicializovana\n")
								sys.exit(56)
							else:
								data_stack.append(TF_dict[arg1[1]].value)
							#print(data_stack)
					else:
						sys.stderr.write("Chyba: Ramec neexistuje.\n")
						sys.exit(55)
			else:
				sys.stderr.write("Chyba: Zly typ premennej\n")
				sys.exit(53)
#############################################################
		elif current_instruction.opcode.upper() == "POPS":
			if current_instruction.arg1_type == "var":
				arg1 = parse_variable(current_instruction.arg1_value)
				if arg1[0] == "GF":
					if arg1[1] not in GF_dict:
						sys.stderr.write("Chyba: Premenna neexistuje. \n")
						sys.exit(54)
					else:
						if len(data_stack) != 0:
							temp_var = IPPvariable("string", data_stack.pop())
							GF_dict[arg1[1]] = temp_var
							#print(GF_dict[arg1[1]].value)
						else:
							sys.stderr.write("Chyba: Zasobnik je prazdny. \n")
							sys.exit(56)	
					#print(data_stack)
				elif arg1[0] == "LF":
					if LF_created == 1:
						if len(LF_list) == 0:
							sys.stderr.write("Chyba: Ramec neexistuje.\n")
							sys.exit(55)
						if arg1[1] not in LF_list[len(LF_list)-1]:
							sys.stderr.write("Chyba: Premenna neexistuje. \n")
							sys.exit(54)
						else:
							if len(data_stack) != 0:
								temp_var = IPPvariable("string", data_stack.pop())
								LF_list[len(LF_list)-1][arg1[1]] = temp_var
								#print(LF_list[len(LF_list)-1][arg1[1]].value)
							else:
								sys.stderr.write("Chyba: Zasobnik je prazdny. \n")
								sys.exit(56)	
						#print(data_stack)
					else:
						sys.stderr.write("Chyba: Ramec neexistuje.\n")
						sys.exit(55)
				elif arg1[0] == "TF":
					if TF_created == 1:
						if arg1[1] not in TF_dict:
							sys.stderr.write("Chyba: Premenna neexistuje. \n")
							sys.exit(54)
						else:
							if len(data_stack) != 0:
								temp_var = IPPvariable("string", data_stack.pop())
								TF_dict[arg1[1]] = temp_var
								#print(TF_dict[arg1[1]].value)
							else:
								sys.stderr.write("Chyba: Zasobnik je prazdny. \n")
								sys.exit(56)	
						#print(data_stack)
					else:
						sys.stderr.write("Chyba: Ramec neexistuje.\n")
						sys.exit(55)
			else:
				sys.stderr.write("Chyba: Zly typ premennej\n")
				sys.exit(53)				
#################################################################
		elif current_instruction.opcode.upper() == "INT2CHAR":
			arg1 = parse_variable(current_instruction.arg1_value)
			if arg1[0] == "GF":
				if arg1[1] not in GF_dict:
					sys.stderr.write("Chyba: Premenna neexistuje.\n")
					sys.exit(54)
				else:
					if current_instruction.arg2_type == "int":
						try:
							znak = chr(int(current_instruction.arg2_value))
							temp_var = IPPvariable("string", znak)
							GF_dict[arg1[1]] = temp_var
							#print(GF_dict[arg1[1]].value)
						except:
							sys.stderr.write("Chyba: Invalid hodnota\n")
							sys.exit(58)
							
					elif current_instruction.arg2_type == "var":
						arg2 = parse_variable(current_instruction.arg2_value)
						if arg2[0] == "GF":
							if arg2[1] not in GF_dict:
								sys.stderr.write("Chyba: Premenna neexistuje. \n")
								sys.exit(54)
							else:
								if GF_dict[arg2[1]] == None:
									sys.stderr.write("Chyba: Premenna neinicializovana\n")
									sys.exit(56)
								else:
									if GF_dict[arg2[1]].type != "int":
										sys.stderr.write("Chyba: Zly typ premennej\n")
										sys.exit(53)						
									else:
										try:
											znak = chr(int(GF_dict[arg2[1]].value))
											temp_var = IPPvariable("string", znak)
											GF_dict[arg1[1]] = temp_var
											#print(GF_dict[arg1[1]].value)
										except:
											sys.stderr.write("Chyba: Invalid hodnota\n")
											sys.exit(58)
					else:
						sys.stderr.write("Chyba: Zly typ premennej\n")
						sys.exit(53)
#######################################################################
		elif current_instruction.opcode.upper() == "STRI2INT":
			arg1 = parse_variable(current_instruction.arg1_value)
			if arg1[0] == "GF":
				if arg1[1] not in GF_dict:
					sys.stderr.write("Chyba: Premenna neexistuje.\n")
					sys.exit(54)
				else:
					if current_instruction.arg2_type == "string" and current_instruction.arg3_type == "int":
						try:
							temp_var = IPPvariable("int", ord(current_instruction.arg2_value[int(current_instruction.arg3_value)]))
							GF_dict[arg1[1]] = temp_var
							#print(GF_dict[arg1[1]].value)
						except:
							sys.stderr.write("Chyba: Invalid hodnota\n")
							sys.exit(58)
					elif current_instruction.arg2_type == "var" and current_instruction.arg3_type =="int":
						arg2 = parse_variable(current_instruction.arg2_value)
						if arg2[0] == "GF":
							if arg2[1] not in GF_dict:
								sys.stderr.write("Chyba: Premenna neexistuje. \n")
								sys.exit(54)
							else:
								if GF_dict[arg2[1]] == None:
									sys.stderr.write("Chyba: Premenna neinicializovana\n")
									sys.exit(56)
								else:
									if GF_dict[arg2[1]].type != "string":
										sys.stderr.write("Chyba: Zly typ premennej\n")
										sys.exit(53)
									else:
										try:
											temp_var = IPPvariable("int", ord(GF_dict[arg2[1]].value[int(current_instruction.arg3_value)]))
											GF_dict[arg1[1]] = temp_var
											#print(GF_dict[arg1[1]].value)
										except:
											sys.stderr.write("Chyba: Invalid hodnota\n")
											sys.exit(58)	
					elif current_instruction.arg2_type == "string" and current_instruction.arg3_type =="var":
						arg2 = parse_variable(current_instruction.arg3_value)
						if arg2[0] == "GF":
							if arg2[1] not in GF_dict:
								sys.stderr.write("Chyba: Premenna neexistuje. \n")
								sys.exit(54)
							else:
								if GF_dict[arg2[1]] == None:
									sys.stderr.write("Chyba: Premenna neinicializovana\n")
									sys.exit(56)
								else:
									if GF_dict[arg2[1]].type != "int":
										sys.stderr.write("Chyba: Zly typ premennej\n")
										sys.exit(53)
									else:
										try:
											temp_var = IPPvariable("int", ord(current_instruction.arg2_value[int(GF_dict[arg2[1]].value)]))
											GF_dict[arg1[1]] = temp_var
											#print(GF_dict[arg1[1]].value)
										except:
											sys.stderr.write("Chyba: Invalid hodnota\n")
											sys.exit(58)	
					elif current_instruction.arg2_type == "var" and current_instruction.arg3_type =="var":
						arg2 = parse_variable(current_instruction.arg2_value)
						arg3 = parse_variable(current_instruction.arg3_value)
						if arg2[0] == "GF":
							if arg2[1] not in GF_dict:
								sys.stderr.write("Chyba: Premenna neexistuje. \n")
								sys.exit(54)
							else:
								if GF_dict[arg2[1]] == None:
									sys.stderr.write("Chyba: Premenna neinicializovana\n")
									sys.exit(56)
								else:
									if arg3[0] == "GF":
										if arg3[1] not in GF_dict:
											sys.stderr.write("Chyba: Premenna neexistuje. \n")
											sys.exit(54)
										else:
											if GF_dict[arg3[1]] == None:
												sys.stderr.write("Chyba: Premenna neinicializovana\n")
												sys.exit(56)
											else:
												if GF_dict[arg2[1]].type != "string" and  GF_dict[arg3[1]].type != "int":
													sys.stderr.write("Chyba: Zly typ premennej\n")
													sys.exit(53)
												else:
													try:
														temp_var = IPPvariable("int", ord(GF_dict[arg2[1]].value[int(GF_dict[arg3[1]].value)]))
														GF_dict[arg1[1]] = temp_var
														#print(GF_dict[arg1[1]].value)
													except:
														sys.stderr.write("Chyba: Invalid hodnota\n")
														sys.exit(58)	
					else:
						sys.stderr.write("Chyba: Zly typ premennej\n")
						sys.exit(53)
#######################################################################
		elif current_instruction.opcode.upper() == "CONCAT":
			arg1 = parse_variable(current_instruction.arg1_value)
			if arg1[0] == "GF":
				if arg1[1] not in GF_dict:
					sys.stderr.write("Chyba: Premenna neexistuje.\n")
					sys.exit(54)
				else:
					if current_instruction.arg2_type == "string" and current_instruction.arg3_type == "string":
						if (current_instruction.arg2_value == None):
							current_instruction.arg2_value = ""
						if (current_instruction.arg3_value == None):
							current_instruction.arg3_value = ""
						temp_concat = current_instruction.arg2_value + current_instruction.arg3_value
						temp_var = IPPvariable("string", temp_concat)
						GF_dict[arg1[1]] = temp_var
						#print(GF_dict[arg1[1]].value)
					elif current_instruction.arg2_type == "var" and current_instruction.arg3_type =="string":
						if (current_instruction.arg3_value == None):
							current_instruction.arg3_value = ""
						arg2 = parse_variable(current_instruction.arg2_value)
						if arg2[0] == "GF":
							if arg2[1] not in GF_dict:
								sys.stderr.write("Chyba: Premenna neexistuje. \n")
								sys.exit(54)
							else:
								if GF_dict[arg2[1]] == None:
									sys.stderr.write("Chyba: Premenna neinicializovana\n")
									sys.exit(56)
								else:
									if GF_dict[arg2[1]].type != "string":
										sys.stderr.write("Chyba: Zly typ premennej\n")
										sys.exit(53)
									else:
										if (GF_dict[arg2[1]].value == None):
											GF_dict[arg2[1]].value = ""
										temp_concat = GF_dict[arg2[1]].value + current_instruction.arg3_value
										temp_var = IPPvariable("string", temp_concat)
										GF_dict[arg1[1]] = temp_var
										#print(GF_dict[arg1[1]].value)	
					elif current_instruction.arg2_type == "string" and current_instruction.arg3_type =="var":
						if (current_instruction.arg2_value == None):
							current_instruction.arg2_value = ""
						arg2 = parse_variable(current_instruction.arg3_value)
						if arg2[0] == "GF":
							if arg2[1] not in GF_dict:
								sys.stderr.write("Chyba: Premenna neexistuje. \n")
								sys.exit(54)
							else:
								if GF_dict[arg2[1]] == None:
									sys.stderr.write("Chyba: Premenna neinicializovana\n")
									sys.exit(56)
								else:
									if GF_dict[arg2[1]].type != "string":
										sys.stderr.write("Chyba: Zly typ premennej\n")
										sys.exit(53)
									else:
										if (GF_dict[arg2[1]].value == None):
											GF_dict[arg2[1]].value = ""
										temp_concat = current_instruction.arg2_value + GF_dict[arg2[1]].value
										temp_var = IPPvariable("string", temp_concat)
										GF_dict[arg1[1]] = temp_var
										#print(GF_dict[arg1[1]].value)	
					elif current_instruction.arg2_type == "var" and current_instruction.arg3_type =="var":
						arg2 = parse_variable(current_instruction.arg2_value)
						arg3 = parse_variable(current_instruction.arg3_value)
						if arg2[0] == "GF":
							if arg2[1] not in GF_dict:
								sys.stderr.write("Chyba: Premenna neexistuje. \n")
								sys.exit(54)
							else:
								if GF_dict[arg2[1]] == None:
									sys.stderr.write("Chyba: Premenna neinicializovana\n")
									sys.exit(56)
								else:
									if arg3[0] == "GF":
										if arg3[1] not in GF_dict:
											sys.stderr.write("Chyba: Premenna neexistuje. \n")
											sys.exit(54)
										else:
											if GF_dict[arg3[1]] == None:
												sys.stderr.write("Chyba: Premenna neinicializovana\n")
												sys.exit(56)
											else:
												if GF_dict[arg2[1]].type != "string" and  GF_dict[arg3[1]].type != "string":
													sys.stderr.write("Chyba: Zly typ premennej\n")
													sys.exit(53)
												else:
													if (GF_dict[arg2[1]].value == None):
														GF_dict[arg2[1]].value = ""
													if (GF_dict[arg3[1]].value == None):
														GF_dict[arg3[1]].value = ""
													temp_concat = GF_dict[arg2[1]].value + GF_dict[arg3[1]].value
													temp_var = IPPvariable("string", temp_concat)
													GF_dict[arg1[1]] = temp_var
													#print(GF_dict[arg1[1]].value)		
					else:
						sys.stderr.write("Chyba: Zly typ premennej\n")
						sys.exit(53)	
#######################################################################
		elif current_instruction.opcode.upper() == "STRLEN":
			arg1 = parse_variable(current_instruction.arg1_value)
			if arg1[0] == "GF":
				if arg1[1] not in GF_dict:
					sys.stderr.write("Chyba: Premenna neexistuje.\n")
					sys.exit(54)
				else:
					if current_instruction.arg2_type == "string":
						if current_instruction.arg2_value == None:
							current_instruction.arg2_value = ""
						temp_var = IPPvariable("int", len(current_instruction.arg2_value))
						GF_dict[arg1[1]] = temp_var
						#print(GF_dict[arg1[1]].value)
					elif current_instruction.arg2_type == "var":
						arg2 = parse_variable(current_instruction.arg2_value)
						if arg2[0] == "GF":
							if arg2[1] not in GF_dict:
								sys.stderr.write("Chyba: Premenna neexistuje. \n")
								sys.exit(54)
							else:
								if GF_dict[arg2[1]] == None:
									sys.stderr.write("Chyba: Premenna neinicializovana\n")
									sys.exit(56)
								else:
									if GF_dict[arg2[1]].type != "string":
										sys.stderr.write("Chyba: Zly typ premennej\n")
										sys.exit(53)
									else:
										if GF_dict[arg2[1]].value == None:
											GF_dict[arg2[1]].value = ""
										temp_var = IPPvariable("int", len(GF_dict[arg2[1]].value))
										GF_dict[arg1[1]] = temp_var
										#print(GF_dict[arg1[1]].value)
					else:
						sys.stderr.write("Chyba: Zly typ premennej\n")
						sys.exit(53)	

#######################################################################
		elif current_instruction.opcode.upper() == "GETCHAR":
			arg1 = parse_variable(current_instruction.arg1_value)
			if arg1[0] == "GF":
				if arg1[1] not in GF_dict:
					sys.stderr.write("Chyba: Premenna neexistuje.\n")
					sys.exit(54)
				else:
					if current_instruction.arg2_type == "string" and current_instruction.arg3_type == "int":
						try:
							temp_var = IPPvariable("string", current_instruction.arg2_value[int(current_instruction.arg3_value)])
							GF_dict[arg1[1]] = temp_var
							#print(GF_dict[arg1[1]].value)
						except:
							sys.stderr.write("Chyba: Invalid hodnota\n")
							sys.exit(58)
					elif current_instruction.arg2_type == "var" and current_instruction.arg3_type =="int":
						arg2 = parse_variable(current_instruction.arg2_value)
						if arg2[0] == "GF":
							if arg2[1] not in GF_dict:
								sys.stderr.write("Chyba: Premenna neexistuje. \n")
								sys.exit(54)
							else:
								if GF_dict[arg2[1]] == None:
									sys.stderr.write("Chyba: Premenna neinicializovana\n")
									sys.exit(56)
								else:
									if GF_dict[arg2[1]].type != "string":
										sys.stderr.write("Chyba: Zly typ premennej\n")
										sys.exit(53)
									else:
										try:
											temp_var = IPPvariable("string", GF_dict[arg2[1]].value[int(current_instruction.arg3_value)])
											GF_dict[arg1[1]] = temp_var
											#print(GF_dict[arg1[1]].value)
										except:
											sys.stderr.write("Chyba: Invalid hodnota\n")
											sys.exit(58)	
					elif current_instruction.arg2_type == "string" and current_instruction.arg3_type =="var":
						arg2 = parse_variable(current_instruction.arg3_value)
						if arg2[0] == "GF":
							if arg2[1] not in GF_dict:
								sys.stderr.write("Chyba: Premenna neexistuje. \n")
								sys.exit(54)
							else:
								if GF_dict[arg2[1]] == None:
									sys.stderr.write("Chyba: Premenna neinicializovana\n")
									sys.exit(56)
								else:
									if GF_dict[arg2[1]].type != "int":
										sys.stderr.write("Chyba: Zly typ premennej\n")
										sys.exit(53)
									else:
										try:
											temp_var = IPPvariable("string", current_instruction.arg2_value[int(GF_dict[arg2[1]].value)])
											GF_dict[arg1[1]] = temp_var
											#print(GF_dict[arg1[1]].value)
										except:
											sys.stderr.write("Chyba: Invalid hodnota\n")
											sys.exit(58)	
					elif current_instruction.arg2_type == "var" and current_instruction.arg3_type =="var":
						arg2 = parse_variable(current_instruction.arg2_value)
						arg3 = parse_variable(current_instruction.arg3_value)
						if arg2[0] == "GF":
							if arg2[1] not in GF_dict:
								sys.stderr.write("Chyba: Premenna neexistuje. \n")
								sys.exit(54)
							else:
								if GF_dict[arg2[1]] == None:
									sys.stderr.write("Chyba: Premenna neinicializovana\n")
									sys.exit(56)
								else:
									if arg3[0] == "GF":
										if arg3[1] not in GF_dict:
											sys.stderr.write("Chyba: Premenna neexistuje. \n")
											sys.exit(54)
										else:
											if GF_dict[arg3[1]] == None:
												sys.stderr.write("Chyba: Premenna neinicializovana\n")
												sys.exit(56)
											else:
												if GF_dict[arg2[1]].type != "string" and  GF_dict[arg3[1]].type != "int":
													sys.stderr.write("Chyba: Zly typ premennej\n")
													sys.exit(53)
												else:
													try:
														temp_var = IPPvariable("string", GF_dict[arg2[1]].value[int(GF_dict[arg3[1]].value)])
														GF_dict[arg1[1]] = temp_var
														#print(GF_dict[arg1[1]].value)
													except:
														sys.stderr.write("Chyba: Invalid hodnota\n")
														sys.exit(58)	
					else:
						sys.stderr.write("Chyba: Zly typ premennej\n")
						sys.exit(53)
#######################################################################
		elif current_instruction.opcode.upper() == "SETCHAR":
			arg1 = parse_variable(current_instruction.arg1_value)
			if arg1[0] == "GF":
				if arg1[1] not in GF_dict:
					sys.stderr.write("Chyba: Premenna neexistuje.\n")
					sys.exit(54)
				else:
					if GF_dict[arg1[1]] == None:
						sys.stderr.write("Chyba: Premenna neinicializovana\n")
						sys.exit(56)
					elif GF_dict[arg1[1]].type != "string":
						sys.stderr.write("Chyba: Zly typ premennej \n")
						sys.exit(53)
					else:
						if current_instruction.arg2_type == "int" and current_instruction.arg3_type == "string":
							try:
								temp_string = list(GF_dict[arg1[1]].value)
								temp_string[int(current_instruction.arg2_value)] = current_instruction.arg3_value[0]
								temp_var = IPPvariable("string", ''.join(temp_string))
								GF_dict[arg1[1]] = temp_var
								#print(GF_dict[arg1[1]].value)
							except:
								sys.stderr.write("Chyba: Invalid hodnota\n")
								sys.exit(58)
						elif current_instruction.arg2_type == "var" and current_instruction.arg3_type =="string":
							arg2 = parse_variable(current_instruction.arg2_value)
							if arg2[0] == "GF":
								if arg2[1] not in GF_dict:
									sys.stderr.write("Chyba: Premenna neexistuje. \n")
									sys.exit(54)
								else:
									if GF_dict[arg2[1]] == None:
										sys.stderr.write("Chyba: Premenna neinicializovana\n")
										sys.exit(56)
									else:
										if GF_dict[arg2[1]].type != "int":
											sys.stderr.write("Chyba: Zly typ premennej\n")
											sys.exit(53)
										else:
											try:
												temp_string = list(GF_dict[arg1[1]].value)
												temp_string[int(GF_dict[arg2[1]].value)] = current_instruction.arg3_value[0]
												temp_var = IPPvariable("string", ''.join(temp_string))
												GF_dict[arg1[1]] = temp_var
												#print(GF_dict[arg1[1]].value)
											except:
												sys.stderr.write("Chyba: Invalid hodnota\n")
												sys.exit(58)	
						elif current_instruction.arg2_type == "int" and current_instruction.arg3_type =="var":
							arg2 = parse_variable(current_instruction.arg3_value)
							if arg2[0] == "GF":
								if arg2[1] not in GF_dict:
									sys.stderr.write("Chyba: Premenna neexistuje. \n")
									sys.exit(54)
								else:
									if GF_dict[arg2[1]] == None:
										sys.stderr.write("Chyba: Premenna neinicializovana\n")
										sys.exit(56)
									else:
										if GF_dict[arg2[1]].type != "string":
											sys.stderr.write("Chyba: Zly typ premennej\n")
											sys.exit(53)
										else:
											try:
												temp_string = list(GF_dict[arg1[1]].value)
												temp_string[int(current_instruction.arg2_value)] = GF_dict[arg2[1]].value[0]
												temp_var = IPPvariable("string", ''.join(temp_string))
												GF_dict[arg1[1]] = temp_var
												#print(GF_dict[arg1[1]].value)
											except:
												sys.stderr.write("Chyba: Invalid hodnota\n")
												sys.exit(58)	
						elif current_instruction.arg2_type == "var" and current_instruction.arg3_type =="var":
							arg2 = parse_variable(current_instruction.arg2_value)
							arg3 = parse_variable(current_instruction.arg3_value)
							if arg2[0] == "GF":
								if arg2[1] not in GF_dict:
									sys.stderr.write("Chyba: Premenna neexistuje. \n")
									sys.exit(54)
								else:
									if GF_dict[arg2[1]] == None:
										sys.stderr.write("Chyba: Premenna neinicializovana\n")
										sys.exit(56)
									else:
										if arg3[0] == "GF":
											if arg3[1] not in GF_dict:
												sys.stderr.write("Chyba: Premenna neexistuje. \n")
												sys.exit(54)
											else:
												if GF_dict[arg3[1]] == None:
													sys.stderr.write("Chyba: Premenna neinicializovana\n")
													sys.exit(56)
												else:
													if GF_dict[arg2[1]].type != "int" and  GF_dict[arg3[1]].type != "string":
														sys.stderr.write("Chyba: Zly typ premennej\n")
														sys.exit(53)
													else:
														try:
															temp_string = list(GF_dict[arg1[1]].value)
															temp_string[int(GF_dict[arg2[1]].value)] = GF_dict[arg3[1]].value[0]
															temp_var = IPPvariable("string", ''.join(temp_string))
															GF_dict[arg1[1]] = temp_var
															#print(GF_dict[arg1[1]].value)
														except:
															sys.stderr.write("Chyba: Invalid hodnota\n")
															sys.exit(58)													
						else:
							sys.stderr.write("Chyba: Zly typ premennej\n")
							sys.exit(53)	
#######################################################################
		elif current_instruction.opcode.upper() == "DPRINT":
			if current_instruction.arg1_type == "int":
				sys.stderr.write(current_instruction.arg1_value+'\n')
			elif current_instruction.arg1_type == "bool":
				if current_instruction.arg1_value == "true":
					sys.stderr.write("true\n")
				else:
					sys.stderr.write("false\n")
			elif current_instruction.arg1_type =="string":
				sys.stderr.write(parse_string(current_instruction.arg1_value)+'\n')
			elif current_instruction.arg1_type == "var":
				arg1 = parse_variable(current_instruction.arg1_value)
				if arg1[0] == "GF":
					if arg1[1] not in GF_dict:
						sys.stderr.write("Chyba: Premenna neexistuje.\n")
						sys.exit(54)
					else:
						if GF_dict[arg1[1]] == None:
							sys.stderr.write("Chyba: Premenna neinicializovana\n")
							sys.exit(56)
						else:
							if GF_dict[arg1[1]].type == "int":
								sys.stderr.write(GF_dict[arg1[1]].value+'\n')
							elif GF_dict[arg1[1]].type == "bool":
								if GF_dict[arg1[1]].value == "true":
									sys.stderr.write("true\n")
								else:
									sys.stderr.write("false\n")
							elif GF_dict[arg1[1]].type =="string":
								sys.stderr.write(parse_string(GF_dict[arg1[1]].value)+'\n')
			else:
				sys.stderr.write("Chyba: Zly typ premennej\n")
				sys.exit(53)	
#######################################################################
		# elif current_instruction.opcode.upper() == "LABEL":
			# if current_instruction.arg1_value not in LABEL_dict:
				# new_var = {current_instruction.arg1_value: current_instruction.order }
				# LABEL_dict.update(new_var)
				# #print(LABEL_dict)
			# else:
				# sys.stderr.write("Chyba: Navesti uz existuje.\n")
				# sys.exit(52)
			# #print("LABEL OK")	
#######################################################################
		elif current_instruction.opcode.upper() == "TYPE":
			arg1 = parse_variable(current_instruction.arg1_value)
			if arg1[0] == "GF":
				if arg1[1] not in GF_dict:
					sys.stderr.write("Chyba: Premenna neexistuje.\n")
					sys.exit(54)
				else:
					if current_instruction.arg2_type == "string" or current_instruction.arg2_type == "int" or current_instruction.arg2_type == "bool":
						temp_var = IPPvariable("string", current_instruction.arg2_type)
						GF_dict[arg1[1]] = temp_var
						#print(GF_dict[arg1[1]].value)
					elif current_instruction.arg2_type == "var":
						arg2 = parse_variable(current_instruction.arg2_value)
						if arg2[0] == "GF":
							if arg2[1] not in GF_dict:
								sys.stderr.write("Chyba: Premenna neexistuje. \n")
								sys.exit(54)
							else:
								if GF_dict[arg2[1]] == None:
									temp_var = IPPvariable("string", "")
									GF_dict[arg1[1]] = temp_var
									#print(GF_dict[arg1[1]].value)
								else:
									temp_var = IPPvariable("string", GF_dict[arg2[1]].type)
									GF_dict[arg1[1]] = temp_var
									#print(GF_dict[arg1[1]].value)
					else:
						sys.stderr.write("Chyba: Zly typ premennej\n")
						sys.exit(53)
#######################################################################
		elif current_instruction.opcode.upper() == "JUMP":
			if current_instruction.arg1_value not in LABEL_dict:
				sys.stderr.write("Chyba: Navesti neexistuje.\n")
				sys.exit(52)
			else:
				#print(LABEL_dict[current_instruction.arg1_value])
				position_counter = int(LABEL_dict[current_instruction.arg1_value])-1
			#print("JUMP OK")
#######################################################################
		elif current_instruction.opcode.upper() == "JUMPIFEQ":
			if current_instruction.arg1_value not in LABEL_dict:
				sys.stderr.write("Chyba: Navesti neexistuje.\n")
				sys.exit(52)
			else:
				if current_instruction.arg2_type == current_instruction.arg3_type and (current_instruction.arg2_type == "int" or current_instruction.arg2_type == "string" or current_instruction.arg2_type == "bool"):
					if current_instruction.arg2_value == current_instruction.arg3_value:
						position_counter = int(LABEL_dict[current_instruction.arg1_value])-1
				elif current_instruction.arg2_type == "var" and (current_instruction.arg3_type == "int" or current_instruction.arg3_type == "string" or current_instruction.arg3_type == "bool"):
					arg2 = parse_variable(current_instruction.arg2_value)
					if arg2[0] == "GF":
						if arg2[1] not in GF_dict:
							sys.stderr.write("Chyba: Premenna neexistuje. \n")
							sys.exit(54)
						else:
							if GF_dict[arg2[1]] == None:
								sys.stderr.write("Chyba: Premenna neinicializovana\n")
								sys.exit(56)
							else:
								if GF_dict[arg2[1]].type != current_instruction.arg3_type:
									sys.stderr.write("Chyba: Zly typ premennej\n")
									sys.exit(53)
								else:
									if GF_dict[arg2[1]].value == current_instruction.arg3_value:
										position_counter = int(LABEL_dict[current_instruction.arg1_value])-1
				
				elif (current_instruction.arg2_type == "int" or current_instruction.arg2_type == "string" or current_instruction.arg2_type == "bool") and current_instruction.arg3_type == "var":
					arg2 = parse_variable(current_instruction.arg3_value)
					if arg2[0] == "GF":
						if arg2[1] not in GF_dict:
							sys.stderr.write("Chyba: Premenna neexistuje. \n")
							sys.exit(54)
						else:
							if GF_dict[arg2[1]] == None:
								sys.stderr.write("Chyba: Premenna neinicializovana\n")
								sys.exit(56)
							else:
								if GF_dict[arg2[1]].type != current_instruction.arg2_type:
									sys.stderr.write("Chyba: Zly typ premennej\n")
									sys.exit(53)
								else:
									if GF_dict[arg2[1]].value == current_instruction.arg2_value:
										position_counter = int(LABEL_dict[current_instruction.arg1_value])-1
				elif current_instruction.arg2_type == "var" and current_instruction.arg3_type == "var":
					arg2 = parse_variable(current_instruction.arg2_value)
					arg3 = parse_variable(current_instruction.arg3_value)
					if arg2[0] == "GF":
						if arg2[1] not in GF_dict:
							sys.stderr.write("Chyba: Premenna neexistuje. \n")
							sys.exit(54)
						else:
							if GF_dict[arg2[1]] == None:
								sys.stderr.write("Chyba: Premenna neinicializovana\n")
								sys.exit(56)
							else:
								if arg3[0] == "GF":
									if arg3[1] not in GF_dict:
										sys.stderr.write("Chyba: Premenna neexistuje. \n")
										sys.exit(54)
									else:
										if GF_dict[arg3[1]] == None:
											sys.stderr.write("Chyba: Premenna neinicializovana\n")
											sys.exit(56)
										else:
											if GF_dict[arg3[1]].type != GF_dict[arg2[1]].type and (GF_dict[arg2[1]].type == "int" or GF_dict[arg2[1]].type == "string" or GF_dict[arg2[1]].type == "bool"):
												sys.stderr.write("Chyba: Zly typ premennej\n")
												sys.exit(53)
											else:
												if GF_dict[arg2[1]].value == GF_dict[arg3[1]].value:
													position_counter = int(LABEL_dict[current_instruction.arg1_value])-1												
				else:
					sys.stderr.write("Chyba: Zly typ premennej\n")
					sys.exit(53)				
			#print("JUMPIFEQ OK")
#######################################################################
		elif current_instruction.opcode.upper() == "JUMPIFNEQ":
			if current_instruction.arg1_value not in LABEL_dict:
				sys.stderr.write("Chyba: Navesti neexistuje.\n")
				sys.exit(52)
			else:
				if current_instruction.arg2_type == current_instruction.arg3_type and (current_instruction.arg2_type == "int" or current_instruction.arg2_type == "string" or current_instruction.arg2_type == "bool"):
					if current_instruction.arg2_value != current_instruction.arg3_value:
						position_counter = int(LABEL_dict[current_instruction.arg1_value])-1
				elif current_instruction.arg2_type == "var" and (current_instruction.arg3_type == "int" or current_instruction.arg3_type == "string" or current_instruction.arg3_type == "bool"):
					arg2 = parse_variable(current_instruction.arg2_value)
					if arg2[0] == "GF":
						if arg2[1] not in GF_dict:
							sys.stderr.write("Chyba: Premenna neexistuje. \n")
							sys.exit(54)
						else:
							if GF_dict[arg2[1]] == None:
								sys.stderr.write("Chyba: Premenna neinicializovana\n")
								sys.exit(56)
							else:
								if GF_dict[arg2[1]].type != current_instruction.arg3_type:
									sys.stderr.write("Chyba: Zly typ premennej\n")
									sys.exit(53)
								else:
									if GF_dict[arg2[1]].value != current_instruction.arg3_value:
										position_counter = int(LABEL_dict[current_instruction.arg1_value])-1
				
				elif (current_instruction.arg2_type == "int" or current_instruction.arg2_type == "string" or current_instruction.arg2_type == "bool") and current_instruction.arg3_type == "var":
					arg2 = parse_variable(current_instruction.arg3_value)
					if arg2[0] == "GF":
						if arg2[1] not in GF_dict:
							sys.stderr.write("Chyba: Premenna neexistuje. \n")
							sys.exit(54)
						else:
							if GF_dict[arg2[1]] == None:
								sys.stderr.write("Chyba: Premenna neinicializovana\n")
								sys.exit(56)
							else:
								if GF_dict[arg2[1]].type != current_instruction.arg2_type:
									sys.stderr.write("Chyba: Zly typ premennej\n")
									sys.exit(53)
								else:
									if GF_dict[arg2[1]].value != current_instruction.arg2_value:
										position_counter = int(LABEL_dict[current_instruction.arg1_value])-1
				elif current_instruction.arg2_type == "var" and current_instruction.arg3_type == "var":
					arg2 = parse_variable(current_instruction.arg2_value)
					arg3 = parse_variable(current_instruction.arg3_value)
					if arg2[0] == "GF":
						if arg2[1] not in GF_dict:
							sys.stderr.write("Chyba: Premenna neexistuje. \n")
							sys.exit(54)
						else:
							if GF_dict[arg2[1]] == None:
								sys.stderr.write("Chyba: Premenna neinicializovana\n")
								sys.exit(56)
							else:
								if arg3[0] == "GF":
									if arg3[1] not in GF_dict:
										sys.stderr.write("Chyba: Premenna neexistuje. \n")
										sys.exit(54)
									else:
										if GF_dict[arg3[1]] == None:
											sys.stderr.write("Chyba: Premenna neinicializovana\n")
											sys.exit(56)
										else:
											if GF_dict[arg3[1]].type != GF_dict[arg2[1]].type and (GF_dict[arg2[1]].type == "int" or GF_dict[arg2[1]].type == "string" or GF_dict[arg2[1]].type == "bool"):
												sys.stderr.write("Chyba: Zly typ premennej\n")
												sys.exit(53)
											else:
												if GF_dict[arg2[1]].value != GF_dict[arg3[1]].value:
													position_counter = int(LABEL_dict[current_instruction.arg1_value])-1												
				else:
					sys.stderr.write("Chyba: Zly typ premennej\n")
					sys.exit(53)				
			#print("JUMPIFNEQ OK")
#######################################################################
		elif current_instruction.opcode.upper() == "CALL":
			if current_instruction.arg1_value not in LABEL_dict:
				sys.stderr.write("Chyba: Navesti neexistuje.\n")
				sys.exit(52)
			else:
				#print(LABEL_dict[current_instruction.arg1_value])
				position_stack.append(current_instruction.order)
				position_counter = int(LABEL_dict[current_instruction.arg1_value])-1
			#print("CALL OK")	
#######################################################################
		elif current_instruction.opcode.upper() == "RETURN":
			if len(position_stack) == 0:
				sys.stderr.write("Chyba: Zasobnik volania je prazdny.\n")
				sys.exit(56)
			else:
				position_counter = int(position_stack.pop())
			#print("RETURN OK")		
#######################################################################
		elif current_instruction.opcode.upper() == "READ":
			arg1 = parse_variable(current_instruction.arg1_value)
			if arg1[0] == "GF":
				if arg1[1] not in GF_dict:
					sys.stderr.write("Chyba: Premenna neexistuje.\n")
					sys.exit(54)
				else:
					if current_instruction.arg2_type != "type":
						sys.stderr.write("Chyba: Zly typ premennej\n")
						sys.exit(53)
					else:
						try:
							temp_input = input()
							if custom_isint(temp_input) and current_instruction.arg2_value == "int":
								temp_var = IPPvariable(current_instruction.arg2_value, temp_input)
								GF_dict[arg1[1]] = temp_var
							elif current_instruction.arg2_value == "bool":
								if custom_isbool(temp_input.lower()) and temp_input == "true":
									temp_var = IPPvariable(current_instruction.arg2_value, temp_input.lower())
									GF_dict[arg1[1]] = temp_var	
								else:
									temp_var = IPPvariable(current_instruction.arg2_value, "false")
									GF_dict[arg1[1]] = temp_var										
							elif custom_isstring(temp_input) and current_instruction.arg2_value == "string":							
								temp_var = IPPvariable(current_instruction.arg2_value, temp_input)
								GF_dict[arg1[1]] = temp_var
							elif current_instruction.arg2_value == "int":
								temp_var = IPPvariable(current_instruction.arg2_value, "0")
								GF_dict[arg1[1]] = temp_var	
							elif current_instruction.arg2_value == "bool":
								temp_var = IPPvariable(current_instruction.arg2_value, "false")
								GF_dict[arg1[1]] = temp_var	
							elif current_instruction.arg2_value == "string":
								temp_var = IPPvariable(current_instruction.arg2_value, "")
								GF_dict[arg1[1]] = temp_var										
						except:
							sys.stderr.write("Chyba: Input failed\n")
							sys.exit(52)	
			elif arg1[0] == "LF":
				if LF_created == 1:
					if len(LF_list) == 0:
						sys.stderr.write("Chyba: Ramec neexistuje.\n")
						sys.exit(55)
					if arg1[1] not in LF_list[len(LF_list)-1]:
						sys.stderr.write("Chyba: Premenna neexistuje.\n")
						sys.exit(54)
					else:
						if current_instruction.arg2_type != "type":
							sys.stderr.write("Chyba: Zly typ premennej\n")
							sys.exit(53)
						else:
							try:
								temp_input = input()
								if custom_isint(temp_input) and current_instruction.arg2_value == "int":
									temp_var = IPPvariable(current_instruction.arg2_value, temp_input)
									LF_list[len(LF_list)-1][arg1[1]] = temp_var
								elif current_instruction.arg2_value == "bool":
									if custom_isbool(temp_input.lower()) and temp_input == "true":
										temp_var = IPPvariable(current_instruction.arg2_value, temp_input.lower())
										LF_list[len(LF_list)-1][arg1[1]] = temp_var	
									else:
										temp_var = IPPvariable(current_instruction.arg2_value, "false")
										LF_list[len(LF_list)-1][arg1[1]] = temp_var										
								elif custom_isstring(temp_input) and current_instruction.arg2_value == "string":							
									temp_var = IPPvariable(current_instruction.arg2_value, temp_input)
									LF_list[len(LF_list)-1][arg1[1]] = temp_var
								elif current_instruction.arg2_value == "int":
									temp_var = IPPvariable(current_instruction.arg2_value, "0")
									LF_list[len(LF_list)-1][arg1[1]] = temp_var	
								elif current_instruction.arg2_value == "bool":
									temp_var = IPPvariable(current_instruction.arg2_value, "false")
									LF_list[len(LF_list)-1][arg1[1]] = temp_var	
								elif current_instruction.arg2_value == "string":
									temp_var = IPPvariable(current_instruction.arg2_value, "")
									LF_list[len(LF_list)-1][arg1[1]] = temp_var										
							except:
								sys.stderr.write("Chyba: Input failed\n")
								sys.exit(52)
				else:
					sys.stderr.write("Chyba: Ramec neexistuje.\n")
					sys.exit(55)
					
			elif arg1[0] == "TF":
				if TF_created == 1:
					if arg1[1] not in TF_dict:
						sys.stderr.write("Chyba: Premenna neexistuje.\n")
						sys.exit(54)
					else:
						if current_instruction.arg2_type != "type":
							sys.stderr.write("Chyba: Zly typ premennej\n")
							sys.exit(53)
						else:
							try:
								temp_input = input()
								if custom_isint(temp_input) and current_instruction.arg2_value == "int":
									temp_var = IPPvariable(current_instruction.arg2_value, temp_input)
									TF_dict[arg1[1]] = temp_var
								elif current_instruction.arg2_value == "bool":
									if custom_isbool(temp_input.lower()) and temp_input == "true":
										temp_var = IPPvariable(current_instruction.arg2_value, temp_input.lower())
										TF_dict[arg1[1]] = temp_var	
									else:
										temp_var = IPPvariable(current_instruction.arg2_value, "false")
										TF_dict[arg1[1]] = temp_var										
								elif custom_isstring(temp_input) and current_instruction.arg2_value == "string":							
									temp_var = IPPvariable(current_instruction.arg2_value, temp_input)
									TF_dict[arg1[1]] = temp_var
								elif current_instruction.arg2_value == "int":
									temp_var = IPPvariable(current_instruction.arg2_value, "0")
									TF_dict[arg1[1]] = temp_var	
								elif current_instruction.arg2_value == "bool":
									temp_var = IPPvariable(current_instruction.arg2_value, "false")
									TF_dict[arg1[1]] = temp_var	
								elif current_instruction.arg2_value == "string":
									temp_var = IPPvariable(current_instruction.arg2_value, "")
									TF_dict[arg1[1]] = temp_var										
							except:
								sys.stderr.write("Chyba: Input failed\n")
								sys.exit(52)													
			#print("READ OK")
#######################################################################
		elif current_instruction.opcode.upper() == "CREATEFRAME":
			#print("LF_list:", LF_list)
			#print("LF_created:",LF_created)
			#print("TF_list:", TF_dict)
			#print("TF_created::::",TF_created)
			if TF_created == 1:
				TF_dict = {}
				TF_created = 1
			elif TF_created == 0:
				TF_dict = {}
				TF_created = 1
			#print("LF_list:", LF_list)
			#print("LF_created:",LF_created)
			#print("TF_list:", TF_dict)
			#print("TF_created:",TF_created)
			#print("CREATEFRAME OK")
#######################################################################
		elif current_instruction.opcode.upper() == "PUSHFRAME":
			if TF_created == 1:
				if LF_created == 1:
					LF_list.append(TF_dict)
					TF_created = 0
				else:
					LF_created = 1
					LF_list.append(TF_dict)
					TF_created = 0					
			else:
				sys.stderr.write("Neexistujuci ramec. \n")
				sys.exit(55)				
			#print("LF_list:", LF_list)
			#print("LF_created:",LF_created)
			#print("PUSHFRAME OK")
#######################################################################
		elif current_instruction.opcode.upper() == "POPFRAME":
			if LF_created == 1:
				if TF_created == 1:
					TF_dict = {}
					#print("LF_LIST_HERE: ", LF_list)
					temp = LF_list.pop()
					#print("Temp: ", temp)
					TF_dict.update(temp)
				else:
					sys.stderr.write("Neexistujuci ramec. \n")
					sys.exit(55)					
			else:
				sys.stderr.write("Neexistujuci ramec. \n")
				sys.exit(55)				
			#print("LF_list:", LF_list)
			#print("LF_created:",LF_created)
			#print("TF_list:", TF_dict)
			#print("TF_created:",TF_created)
			#print("PUSHFRAME OK")
main()	