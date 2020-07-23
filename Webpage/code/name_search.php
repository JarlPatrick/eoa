<?php namespace name_s {

function id_by_name($conn, $name) {
	$sql = "SELECT * FROM person WHERE name LIKE '%".$name."%';";
	$result = $conn->query($sql);
	$nimed = array();
	if ($result->num_rows > 0) {
		while($row = $result->fetch_assoc()) {
			$nimed[$row["id"]] = $row["name"];
		}
	}
	return $nimed;
}

function multi_name($nimed, $nimi){
	$out="<center><br><h1>Inimesed, kelle nimed vastavad otsingule '".$nimi."':</h1><br>";
	foreach ($nimed as $id=>$name){
		$out.="<h3><a href='?name=".$name."'>".$name."</a></h3>";
	}
	return $out;
}

function get_table($conn, $tbname, $scpar, $scind){
	$sql = "SELECT * FROM ".$tbname." WHERE ".$scpar."=".$scind.";";
	$result = $conn->query($sql);
	$out = array();
	if ($result->num_rows > 0) {
		while($row = $result->fetch_assoc()) {
			array_push($out, $row);
		}
	}
	return $out;
}
	

function single_name($conn, $n_id, $nimi){
	$out="<center><br><h1>".$nimi." profiil </h1><br>";
	$contestant=get_table($conn, "contestant", "person_id", $n_id);
	
	$out.="<table><tr><th>Ala</th><th>Tüüp</th><th>Aasta</th><th>Vanuseklass</th><th>Koht</th><th>Link</th></tr>";
	foreach ($contestant as $p){
		$subcont = get_table($conn, "subcontest", "id", $p["subcontest_id"])[0];
		$cont = get_table($conn, "contest", "id", $subcont["contest_id"])[0];
		$subject = get_table($conn, "subject", "id", $cont["subject_id"])[0];
		$type = get_table($conn, "type", "id", $cont["type_id"])[0];
		$year = get_table($conn, "year", "id", $cont["year_id"])[0];
		$age_group = get_table($conn, "age_group", "id", $subcont["age_group_id"])[0];
		
		$out.="<tr><th>".$subject["name"]."</th><th>".$type["name"]."</th><th>".$year["name"]."</th><th>".$age_group["name"]."</th><th>".$p["placement"]."</th><th><a href='?id=".$subcont["id"]."'>Link</a></th></tr>";
	}
	return $out;
}

function search($conn, $name){
	$nimed = id_by_name($conn, $name);
	if(count($nimed) >1){
		return multi_name($nimed,$name);
	}
	if(count($nimed) == 1){
		foreach ($nimed as $id=>$name){
			return single_name($conn, $id, $name);
		}
	}
}

}?>