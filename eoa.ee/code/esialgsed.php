<?php namespace esialgsed {

function Fkood(){
	//koodide saamine
	$urlfusa='https://docs.google.com/spreadsheets/u/1/d/1HxQ_u9cZKaucH2-DxHsPQdqpKZnaf4_obieFHFYm8gY/export?format=csv&id=1HxQ_u9cZKaucH2-DxHsPQdqpKZnaf4_obieFHFYm8gY&gid=1454512836';
	if(!ini_set('default_socket_timeout', 15)) echo "<!-- unable to change socket timeout -->";
	if (($handle = fopen($urlfusa, "r")) !== FALSE) {
	while (($data = fgetcsv($handle, 1000, ",")) !== FALSE) {
			$fusakood[$data[0]] = $data[2];
	}
	fclose($handle);
	}
	else{die("Problem reading csv 12");}
	
	return $fusakood;
}

function Mkood(){
	$urlmata='https://docs.google.com/spreadsheets/d/18AQhRiya1A1KBGD1CeOkty_pzYgeVCaZ5mjdp3Q-1Uk/export?format=csv&gid=1286121907';
	if(!ini_set('default_socket_timeout', 15)) echo "<!-- unable to change socket timeout -->";
	if (($handle = fopen($urlmata, "r")) !== FALSE) {
	while (($data = fgetcsv($handle, 1000, ",")) !== FALSE) {
		$matakood[$data[0]] = $data[1];
	}
	fclose($handle);
	}
	else{die("Problem reading csv 12");}
	return $matakood;
}

function esialg($url,$ul,$nimi,$alanimi){
	$log = "";
	if($alanimi == "fusa"){
		$kood = Fkood();
	}
	if($alanimi == "mata"){
		$kood = Mkood();
	}
	
	
	if(!ini_set('default_socket_timeout', 15)) $log .="<!-- unable to change socket timeout -->";

	if (($handle = fopen($url, "r")) !== FALSE) {
	while (($data = fgetcsv($handle, 1000, ",")) !== FALSE) {
		$sheet[] = $data;
	}
	fclose($handle);
	}
	else
		die("Problem reading csv");

	unset($sheet[0]);
	$num=$ul+1;
	if($ul+1==13){
	usort($sheet, function($a, $b) {
		return $b[13] <=> $a[13];
	});}
	if($ul+1==7){
	usort($sheet, function($a, $b) {
		return $b[7] <=> $a[7];
    });}
	$log .= "<center><h1>".$nimi."</h1><br><table class='sortable'>";
	$log .= "<tr><th>NIMI</th><th>KOOD</th>";
	for($x=1; $x <= $ul;$x++){
		$log .= "<th>".$x."</th>";
	}
	$log .= "<th>Kokku</th></tr>";

	foreach($sheet as $val){
	$ridaa = "<tr>";
	$ridaa.= "<th>".$kood[$val[0]]."</th>";
	$tulemus = false;
	$i=0;
	foreach($val as $a){
		$ridaa.= "<th>".$a."</th>";
		if(ord($a) >= 48 && ord($a) <= 55 && $i>0 && $i < 6){
			$tulemus = true;
		}
	$i+=1;
	}
	$ridaa.= "</tr>";
	if($tulemus){$log .= $ridaa;}
	};
	
	return $log;
}

}
