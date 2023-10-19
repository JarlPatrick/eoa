<?php namespace name_s {

function name_by_id($conn, $n_id) {
	$sql = "SELECT * FROM person WHERE id=".$n_id.";";
	$result = $conn->query($sql);
	$name = "";
	if ($result->num_rows > 0) {
		while($row = $result->fetch_assoc()) {
			$name = $row["name"];
		}
	}
	return $name;
}

function find_by_name($conn, $name): array {
	$sql = "SELECT id, name FROM person WHERE name LIKE '%".$conn->real_escape_string($name)."%';";
	$result = $conn->query($sql);
	$names = array();
	if ($result->num_rows > 0) {
		while($row = $result->fetch_assoc()) {
			$names[$row["id"]] = $row["name"];
		}
	}
	return $names;
}

function multi_name($nimed, $nimi): string {
	$out="<center><br><h1>Inimesed, kelle nimed vastavad otsingule '".$nimi."':</h1><br>";
	foreach ($nimed as $id=>$name){
		$out.="<h3><a href='?name_id=".$id."'>".$name."</a></h3>";
	}
	return $out;
}

function get_participations($conn, $id): array {
	$sql = "SELECT placement, s_name, t_name, y_name, a_name, sc_id
		FROM contestant co
		LEFT JOIN full_subcontest sub ON sub.sc_id = co.subcontest_id
		WHERE co.person_id = $id
		ORDER BY y_name DESC, sc_id DESC;";

	$result = $conn->query($sql);
	$participations = array();
	if ($result->num_rows > 0) {
		while($row = $result->fetch_assoc()) {
			$participations[] = $row;
		}
	}
	return $participations;
}

function get_mentees($conn, $id): array {
	$sql = "SELECT p.id m_id, p.name m_name, s_name, t_name, y_name, a_name, placement, sc_id
		FROM mentor m
		LEFT JOIN contestant co ON co.id = m.contestant_id
		LEFT JOIN person p ON p.id = co.person_id
		LEFT JOIN full_subcontest sub ON sub.sc_id = co.subcontest_id
		WHERE m.mentor_id = $id
		ORDER BY y_name DESC, sc_id DESC;";
	$result = $conn->query($sql);
	$mentees = array();
	if($result->num_rows > 0) {
		while($row = $result->fetch_assoc()) {
			$mentees[] = $row;
		}
	}
	return $mentees;
}

function person_profile($conn, $id){
	$name = name_by_id($conn, $id);
	if($name == "") {
		return array("content" => "<h1>404</h1><div>Lehte ei leitud</div>",
			"status" => 404,
			"title" => "404 - EOA");
	}
	
	$out="<center><br><h1>".$name." profiil </h1><br>";
	$mentees=get_mentees($conn, $id);
	$participations = get_participations($conn, $id);
	if(count($participations)>0){
		$out.= "<h2>Osalemised (".count($participations).")</h2>";
		
		$out.="<table class='sortable'><tr>";
		$out .= "<th>Ala</th>";
		$out .= "<th>Tüüp</th>";
		$out .= "<th>Aasta</th>";
		$out .= "<th>Vanuseklass</th>";
		$out .= "<th>Koht</th>";
		$out .= "<th>Link</th></tr>";
		foreach ($participations as $p){
			$out .= "<tr><td>".$p["s_name"]."</td>";
			$out .= "<td>".$p["t_name"]."</td>";
			$out .= "<td>".$p["y_name"]."</td>";
			$out .= "<td>".$p["a_name"]."</td>";
			$out .= "<td>".$p["placement"]."</td>";
			$out .= "<td><a href='?id=".$p["sc_id"]."'>Link</a></td></tr>";
		}
		$out.= "</table>";
	}
	if(count($mentees)>0){
		$out .= "<h2>Juhendamised (".count($mentees).")</h2>";
		
		$out .= "<table class='sortable'><tr>";
		$out .= "<th>Õpilase nimi</th>";
		$out .= "<th>Ala</th>";
		$out .= "<th>Tüüp</th>";
		$out .= "<th>Aasta</th>";
		$out .= "<th>Vanuseklass</th>";
		$out .= "<th>Koht</th>";
		$out .= "<th>Link</th></tr>";
		foreach ($mentees as $m){
			$out .="<tr><td><a href='/?name_id=".$m["m_id"]."'>".$m["m_name"]."</a></td>";
			$out .= "<td>".$m["s_name"]."</td>";
			$out .= "<td>".$m["t_name"]."</td>";
			$out .= "<td>".$m["y_name"]."</td>";
			$out .= "<td>".$m["a_name"]."</td>";
			$out .= "<td>".$m["placement"]."</td>";
			$out .= "<td><a href='?id=".$m["sc_id"]."'>Link</a></td></tr>";
		}
		$out.= "</table>";
	}
	return array("content" => $out, "status" => 200, "title" => $name . " - EOA");
}

function search($conn, $name){
	$names = find_by_name($conn, $name);
	if(count($names) > 1){
		$out = multi_name($names,$name);
		return array("content" => $out, "status" => 200, "title" => $name . " - otsing - EOA");
	} elseif(count($names) == 1){
		foreach ($names as $id=>$name){
			return person_profile($conn, $id);
		}
	} else {
		return array("content" => "<div>Otsingule vastavaid nimesid ei leitud.</div>",
			"status" => 200, "title" => $name . " - otsing - EOA");
	}
}

}
