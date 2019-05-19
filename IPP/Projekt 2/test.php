<?php

function printHelp(){
    echo "Skript slouži pro automatické testování postupné aplikace parse.php a interpret.py.  Skript projde zadaný adresář s testy a využije je pro automatické otestování správné funkčnosti obou předchozích programů včetně vygenerování přehledného souhrnu v HTML 5 do standardního výstupu.\n";
	echo "Parametry:\n";
	echo "--help vypíše na standardní výstup nápovědu skriptu (nenačítá žádný vstup), tento parametr nelze kombinovat s žádným dalším parametrem \n";
	echo "--directory=path testy bude hledat v zadaném adresáři (chybí-li tento parametr, tak skript prochází aktuální adresář)\n";
	echo "--recursive testy bude hledat nejen v zadaném adresáři, ale i rekurzivně ve všech jeho podadresářích\n";
	echo "--parse-script=file soubor se skriptem v PHP 5.6 pro analýzu zdrojového kódu v IPPcode18(chybí-li tento parametr, tak implicitní hodnotou je parse.php uložený v aktuálním adresáři) \n";
	echo "--int-script=file soubor se skriptem v Python 3.6 pro interpret XML reprezentace kódu v IPPcode18 (chybí-li tento parametr, tak implicitní hodnotou je interpret.py uložený v aktuálním adresáři)\n";
	echo "Spustenie skriptu:\n";
	echo "php5.6 test.php [--directory=path][--recursive][--parse-script=file][--int-script=file][--help]\n";
	exit(0);
}

function loadArgs($argv){
    
    $shortopts = "";
    $longopts = array(
        "help",
		"directory:",
		"recursive",
		"parse-script:",
		"int-script:",
    );
    $opts = getopt($shortopts, $longopts);
    
	
    if (isset($opts['help']) && count($argv) == 2 && count($opts) == 1){
        printHelp();
    }
	else if(count($argv) == count($opts)+1 && !(isset($opts['help']))){
		return $opts;
	}
    else {
		fwrite(STDERR,"Chyba 10: Wrong arguments, try --help \n");
        exit(10);    
    }

}
$TEST_DIR_PATH = "./";
$PARSE_SCRIPT_PATH = "parse.php";
$INT_SCRIPT_PATH = "interpret.py";

$MAX_DEPTH = 1;

$args = loadArgs($argv);

$directory_set = 0;

$all_passed = 1;

$number_tests = 0;
$passed = 0;

if(isset($args['directory'])){
	$TEST_DIR_PATH = $args['directory'];
	$directory_set =1;
}
if(isset($args['parse-script'])){
	$PARSE_SCRIPT_PATH = "parse.php"	;
}
if(isset($args['int-script'])){
	$INT_SCRIPT_PATH = "interpret.py";
}
if(isset($args['recursive'])){
	$MAX_DEPTH = 0;
}

//RECURSIVE OFF
// Zakladne echo html suboru s css syle
echo "
<html>
<head>
<style>
table{
	margin:auto;
	width:auto;
	padding:10px;
    border: 1px solid black;	
}
tr {
    border: 1px solid black;
}
#ok{
	padding:5px;
	text-align: center;
	font-weight: bold;
	background-color: lightgreen;
}
#fail{
	padding:5px;
	text-align:center;
	font-weight: bold;
	background-color: #ff6666;
}
</style>
</head>
<body>
<h2 style=\"margin:auto; text-align: center;\">Test results</h2>
<table>
  <tr>
    <th>Test</th>
    <th>Result</th> 
    <th>Expected Return</th> 
	<th>Received Return</th> 
  </tr>	
";

// Ak bez rekurzie 
if ($MAX_DEPTH == 1){
	#vyhlada vsetky subory s priponou .src v aktualnom adresari 
	$command_find = "find ".$TEST_DIR_PATH." -maxdepth 1 -type f -name \"*.src\" | cut -d '.' -f2";
	exec($command_find, $tests, $return);
	foreach ($tests as $test){
		$number_tests = $number_tests +1;
		//echo $test."\n";
		$src = $test.".src";
		$in = $test.".in";
		$out = $test.".out";
		$rc = $test.".rc";
		$temp = $test.".temp";
		
		# Vytvorenie pripadne neexistujucich suborov potrebnych pre test a ich naplnenie default hodnotami.
		if($directory_set == 1){
			
			if(!@fopen(".".$out,"r")){
				$temp2 = fopen(".".$out,"w");
				fclose($temp2);			
			}
			if(!@fopen(".".$in,"r")){
				$temp2 = fopen(".".$in,"w");
				fclose($temp2);			
			}
			if(!@fopen(".".$rc,"r")){
				$temp2 = fopen(".".$rc,"w");
				fwrite($temp2,"0");
				fclose($temp2);			
			}
		}
		else if ($directory_set == 0){
			
			if(!@fopen($TEST_DIR_PATH.$out,"r")){
				$temp2 = fopen($TEST_DIR_PATH.$out,"w");
				fclose($temp2);			
			}
			if(!@fopen($TEST_DIR_PATH.$in,"r")){
				$temp2 = fopen($TEST_DIR_PATH.$in,"w");
				fclose($temp2);			
			}
			if(!@fopen($TEST_DIR_PATH.$rc,"r")){
				$temp2 = fopen($TEST_DIR_PATH.$rc,"w");
				fwrite($temp2,"0");
				fclose($temp2);			
			}			
		}
		
		
		
		if($directory_set == 1){
			$command = "php5.6 ".$PARSE_SCRIPT_PATH." <.".$src." >.".$temp;
			//echo $command."\n";
			exec($command,$output,$return);
			$handle = @fopen(".".$rc,"r");
		}
		else if ($directory_set ==0){
			$command = "php5.6 ".$PARSE_SCRIPT_PATH." <".$TEST_DIR_PATH.$src." >".$TEST_DIR_PATH.$temp;
			//echo $command."\n";
			exec($command,$output,$return);
			$handle = @fopen($TEST_DIR_PATH.$rc,"r");
		}
		// TODO: KONTROLA CI NAHODOU NEMAM SKOR ERROR NEZ MA BYT

		//$handle = @fopen($TEST_DIR_PATH.$rc,"r");
		if ($handle){
			$buffer = trim(fgets($handle));
			//echo "Buffer: ".$buffer."\n";
			fclose($handle);
			if ($buffer == $return && $return == 21){
				// TEST PASS
				$passed = $passed +1;
				echo "
				  <tr>
					<td id=\"ok\">".$test."</td>
					<td id=\"ok\">Passed</td>
					<td id=\"ok\">".$buffer."</td>
					<td id=\"ok\">".$return."</td>
				  </tr>
				";
			}
			else if ($buffer == 21 && $return !=21){
				// TEST FAILED
				echo "
				  <tr>
					<td id=\"fail\">".$test."</td>
					<td id=\"fail\">Failed</td>
					<td id=\"fail\">".$buffer."</td>
					<td id=\"fail\">".$return."</td>
				  </tr>
				";
				$all_passed = 0;
			}
			else if ($buffer != 21 && $return == 21){
				echo "
				  <tr>
					<td id=\"fail\">".$test."</td>
					<td id=\"fail\">Failed</td>
					<td id=\"fail\">".$buffer."</td>
					<td id=\"fail\">".$return."</td>
				  </tr>
				";
				$all_passed = 0;
			}
			else if ($buffer != 21 && $return == 0){
				// CONTINUE PHASE2
				if($directory_set == 1){
					$command = "python3 ".$INT_SCRIPT_PATH." --source=.".$temp." >.".$test.".myout <.".$in;
					exec($command, $output,$return);
				}
				else if ($directory_set ==0){
					$command = "python3 ".$INT_SCRIPT_PATH." --source=".$TEST_DIR_PATH.$temp." >".$TEST_DIR_PATH.$test.".myout <.".$in;
					exec($command, $output,$return);					
				}
				if($buffer == $return && $return ==0){
					if($directory_set == 1){
						$command = "diff -s .".$test.".myout .".$out." -Z -B";
						exec($command, $output, $return);						
					}
					else if ($directory_set == 0){
						$command = "diff -s ".$TEST_DIR_PATH.$test.".myout ".$TEST_DIR_PATH.$out." -Z -B";
						exec($command, $output, $return);
					}
					if ($return == 0){
						$passed = $passed +1;
						echo "
							<tr>
								<td id=\"ok\">".$test."</td>
								<td id=\"ok\">Passed</td>
								<td id=\"ok\">".$buffer."</td>
								<td id=\"ok\">".$return."</td>
							</tr>
							";
					}
					else{	
							echo "
								<tr>
									<td id=\"fail\">".$test."</td>
									<td id=\"fail\">Failed</td>
									<td id=\"fail\">".$buffer."</td>
									<td id=\"fail\">".$return."</td>
								</tr>
								";
								$all_passed = 0;
					}
				}
				else if ($buffer == $return){
					$passed = $passed +1;
						echo "
							<tr>
								<td id=\"ok\">".$test."</td>
								<td id=\"ok\">Passed</td>
								<td id=\"ok\">".$buffer."</td>
								<td id=\"ok\">".$return."</td>
							</tr>
							";					
				}			
				else if ($buffer >= 52 && $buffer <= 58 && $buffer != $return){
					$passed = $passed +1;
						echo "
							<tr>
								<td id=\"ok\">".$test."</td>
								<td id=\"ok\">Passed</td>
								<td id=\"ok\">".$buffer."</td>
								<td id=\"ok\">".$return."</td>
							</tr>
							";					
				}				
				else{
							echo "
								<tr>
									<td id=\"fail\">".$test."</td>
									<td id=\"fail\">Failed</td>
									<td id=\"fail\">".$buffer."</td>
									<td id=\"fail\">".$return."</td>
								</tr>
								";
								$all_passed = 0;
				}
				
			}
		}
		
		//$command = "diff -s ".$return." ".$TEST_DIR_PATH.$rc." -Z";	
		if($directory_set == 1){
			$command = "find . -name \"*.temp\" -type f -delete";
			exec($command,$output,$return);
			$command = "find . -name \"*.myout\" -type f -delete";
			exec($command,$output,$return);
		}
		else if ($directory_set ==0){
			$command = "find . -name \"*.temp\" -type f -delete";
			exec($command,$output,$return);
			$command = "find . -name \"*.myout\" -type f -delete";
			exec($command,$output,$return);
		}		
		
	}
	

}
// RECURSIVE ON TODO: GENEROVAT HTML, ODSTRANIT TEMP FILES
else{
	$command_find = "find ".$TEST_DIR_PATH." -type f -name \"*.src\" | cut -d '.' -f2";
	exec($command_find, $tests, $return);
	foreach ($tests as $test){
		$number_tests = $number_tests +1;
		//echo $test."\n";
		$src = $test.".src";
		$in = $test.".in";
		$out = $test.".out";
		$rc = $test.".rc";
		$temp = $test.".temp";
		
		if($directory_set == 1){
			
			if(!@fopen(".".$out,"r")){
				$temp2 = fopen(".".$out,"w");
				fclose($temp2);			
			}
			if(!@fopen(".".$in,"r")){
				$temp2 = fopen(".".$in,"w");
				fclose($temp2);			
			}
			if(!@fopen(".".$rc,"r")){
				$temp2 = fopen(".".$rc,"w");
				fwrite($temp2,"0");
				fclose($temp2);			
			}
		}
		else if ($directory_set == 0){
			
			if(!@fopen($TEST_DIR_PATH.$out,"r")){
				$temp2 = fopen($TEST_DIR_PATH.$out,"w");
				fclose($temp2);			
			}
			if(!@fopen($TEST_DIR_PATH.$in,"r")){
				$temp2 = fopen($TEST_DIR_PATH.$in,"w");
				fclose($temp2);			
			}
			if(!@fopen($TEST_DIR_PATH.$rc,"r")){
				$temp2 = fopen($TEST_DIR_PATH.$rc,"w");
				fwrite($temp2,"0");
				fclose($temp2);			
			}			
		}
		
		
		
		if($directory_set == 1){
			$command = "php5.6 ".$PARSE_SCRIPT_PATH." <.".$src." >.".$temp;
			//echo $command."\n";
			exec($command,$output,$return);
			$handle = @fopen(".".$rc,"r");
		}
		else if ($directory_set ==0){
			$command = "php5.6 ".$PARSE_SCRIPT_PATH." <".$TEST_DIR_PATH.$src." >".$TEST_DIR_PATH.$temp;
			//echo $command."\n";
			exec($command,$output,$return);
			$handle = @fopen($TEST_DIR_PATH.$rc,"r");
		}
		// TODO: KONTROLA CI NAHODOU NEMAM SKOR ERROR NEZ MA BYT

		//$handle = @fopen($TEST_DIR_PATH.$rc,"r");
		if ($handle){
			$buffer = trim(fgets($handle));
			//echo "Buffer: ".$buffer."\n";
			fclose($handle);
			if ($buffer == $return && $return == 21){
				$passed = $passed +1;
				// TEST PASS
				echo "
				  <tr>
					<td id=\"ok\">".$test."</td>
					<td id=\"ok\">Passed</td>
					<td id=\"ok\">".$buffer."</td>
					<td id=\"ok\">".$return."</td>
				  </tr>
				";			
			}
			else if ($buffer == 21 && $return !=21){
				// TEST FAILED
							echo "
								<tr>
									<td id=\"fail\">".$test."</td>
									<td id=\"fail\">Failed</td>
									<td id=\"fail\">".$buffer."</td>
									<td id=\"fail\">".$return."</td>
								</tr>
								";
								$all_passed = 0;
			}
			else if ($buffer != 21 && $return == 21){
							echo "
								<tr>
									<td id=\"fail\">".$test."</td>
									<td id=\"fail\">Failed</td>
									<td id=\"fail\">".$buffer."</td>
									<td id=\"fail\">".$return."</td>
								</tr>
								";
								$all_passed = 0;
			}
			else if ($buffer != 21 && $return == 0){
				// CONTINUE PHASE2
				if($directory_set == 1){
					$command = "python3 ".$INT_SCRIPT_PATH." --source=.".$temp." >.".$test.".myout <".$TEST_DIR_PATH.$in;
					exec($command, $output,$return);
				}
				else if ($directory_set ==0){
					$command = "python3 ".$INT_SCRIPT_PATH." --source=".$TEST_DIR_PATH.$temp." >".$TEST_DIR_PATH.$test.".myout <".$TEST_DIR_PATH.$in;
					exec($command, $output,$return);					
				}
				if($buffer == $return && $return == 0){
					if($directory_set == 1){
						$command = "diff -s .".$test.".myout .".$out." -Z -B";
						exec($command, $output, $return);						
					}
					else if ($directory_set == 0){
						$command = "diff -s ".$TEST_DIR_PATH.$test.".myout ".$TEST_DIR_PATH.$out." -Z -B";
						exec($command, $output, $return);
					}
					if ($return == 0){
						$passed = $passed +1;
						echo "
							<tr>
								<td id=\"ok\">".$test."</td>
								<td id=\"ok\">Passed</td>
								<td id=\"ok\">".$buffer."</td>
								<td id=\"ok\">".$return."</td>
							</tr>
							";
							
					}
					else{	
							echo "
								<tr>
									<td id=\"fail\">".$test."</td>
									<td id=\"fail\">Failed</td>
									<td id=\"fail\">".$buffer."</td>
									<td id=\"fail\">".$return."</td>
								</tr>
								";
								$all_passed = 0;
					}
				}
				else if ($buffer == $return){
					$passed = $passed +1;
						echo "
							<tr>
								<td id=\"ok\">".$test."</td>
								<td id=\"ok\">Passed</td>
								<td id=\"ok\">".$buffer."</td>
								<td id=\"ok\">".$return."</td>
							</tr>
							";					
				}
				else if ($buffer >= 52 && $buffer <= 58 && $buffer != $return){
					$passed = $passed +1;
						echo "
							<tr>
								<td id=\"ok\">".$test."</td>
								<td id=\"ok\">Passed</td>
								<td id=\"ok\">".$buffer."</td>
								<td id=\"ok\">".$return."</td>
							</tr>
							";					
				}
				else{
							echo "
								<tr>
									<td id=\"fail\">".$test."</td>
									<td id=\"fail\">Failed</td>
									<td id=\"fail\">".$buffer."</td>
									<td id=\"fail\">".$return."</td>
								</tr>
								";
								$all_passed = 0;
				}
				
			}
		}
		
		//$command = "diff -s ".$return." ".$TEST_DIR_PATH.$rc." -Z";	
		
		if($directory_set == 1){
			$command = "find . -name \"*.temp\" -type f -delete";
			exec($command,$output,$return);
			$command = "find . -name \"*.myout\" -type f -delete";
			exec($command,$output,$return);
		}
		else if ($directory_set ==0){
			$command = "find . -name \"*.temp\" -type f -delete";
			exec($command,$output,$return);
			$command = "find . -name \"*.myout\" -type f -delete";
			exec($command,$output,$return);
		}			
	}
}
echo "
</table>
";

if ($all_passed){
	echo "<h1 id=\"ok\">All tests passed!</h2>";
}
else{
	$failed = $number_tests - $passed;
	$percent = ($passed*100)/$number_tests;
	echo "<h1 id=\"fail\">Some tests failed! Passed ".round($percent,2)."% (".$passed."/".$number_tests.")</h2>";	
}

echo "
</body>
</html>	
";

?>