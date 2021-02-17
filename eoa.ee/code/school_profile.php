<?php namespace school_profile {
	
	function school_name($conn, $s_id){
		$sql = "SELECT name FROM school WHERE id=".$s_id.";";
		$result = $conn->query($sql);
		if ($result->num_rows > 0) {
		while($row = $result->fetch_assoc()) {
			$name = $row["name"];
			}
		}
		return $name;
	}
	
	function all_names($conn) {
		$sql = "SELECT * FROM person;";
		$result = $conn->query($sql);
		$nimi = array();
		if ($result->num_rows > 0) {
			while($row = $result->fetch_assoc()) {
				$nimi[$row['id']] = $row["name"];
			}
		}
		return $nimi;
	}
	
	function all_conts($conn, $s_id) {
		$sql = "SELECT * FROM contestant WHERE school_id =".$s_id.";";
		$result = $conn->query($sql);
		$out = array();
		if ($result->num_rows > 0) {
			while($row = $result->fetch_assoc()) {
				array_push($out, $row);
			}
		}
		return $out;
	}
	
	function all_mentors($conn, $conts){
		$c_list = "(";
		foreach($conts as $c){
			$c_list.=$c["id"].",";
		}
		$c_list = substr($c_list, 0, -1).")";
		$sql = "SELECT mentor_id FROM mentor WHERE contestant_id IN ".$c_list.";";
		$result = $conn->query($sql);
		$out = array();
		if ($result->num_rows > 0) {
			while($row = $result->fetch_assoc()) {
				array_push($out, $row);
			}
		}
		return $out;
	}
	
	function get_profile($conn, $s_id){
		$school_name = school_name($conn, $s_id);
		$names = all_names($conn);
		$conts = all_conts($conn, $s_id);
		$mentors_ids = all_mentors($conn, $conts);
		
		$student = array();
		foreach ($conts as $c){
			if(empty($student[$c['person_id']])){
				$student[$c['person_id']][0] = 1;
				$student[$c['person_id']][1] = $names[$c['person_id']];
			} else {
				$student[$c['person_id']][0] += 1;
			}
		}
		
		$mentors = array();
		foreach ($mentors_ids as $m){
			if(empty($mentors[$m['mentor_id']])){
				$mentors[$m['mentor_id']][0] = 1;
				$mentors[$m['mentor_id']][1] = $names[$m['mentor_id']];
			} else {
				$mentors[$m['mentor_id']][0] += 1;
			}
		}
		
		$out="<center><br>";
		$out.= "<h1>".$school_name."</h1><br>";
		
		$out.="<div><table style='float: left'><tr>";
		$out.= "<tr><th>Juhendaja</th><th>Juhendamisi</th></tr>";
		usort($mentors, function($a, $b) {	return $b[0] <=> $a[0];	});
		foreach ($mentors as $id=>$m){
			$out.="<tr><td>".$m[1]."</td><td>".$m[0]."</td></tr>";
		}
		$out.="</table><table style='float: right'>";
		$out.= "<tr><th>Õpilane</th><th>Osalemisi</th></tr>";
		usort($student, function($a, $b) {	return $b[0] <=> $a[0];	});
		foreach ($student as $id=>$s){
			$out.="<tr><td>".$s[1]."</td><td>".$s[0]."</td></tr>";
		}
		$out.="</table></div>";
		
		$out.="</center>";
		
		return $out;
	}
	
}?>