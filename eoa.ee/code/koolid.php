<?php namespace koolid {
	
	function get_schools($conn) {
		$sql = "SELECT * FROM school;";
		$result = $conn->query($sql);
		$nimed = array();
		if ($result->num_rows > 0) {
			while($row = $result->fetch_assoc()) {
				array_push($nimed, $row);
			}
		}
		return $nimed;
	}
	
	function cont_by_school($conn, $s_id) {
		$sql = "SELECT * FROM contestant WHERE school_id=".$s_id.";";
		$result = $conn->query($sql);
		$nimed = array();
		if ($result->num_rows > 0) {
			while($row = $result->fetch_assoc()) {
				array_push($nimed, $row);
			}
		}
		return $nimed;
	}
	
	function cont_place_by_school($conn, $s_id, $place) {
		$sql = "SELECT * FROM contestant WHERE school_id=".$s_id." AND placement=".$place.";";
		$result = $conn->query($sql);
		$nimed = array();
		if ($result->num_rows > 0) {
			while($row = $result->fetch_assoc()) {
				$nimed[$row["id"]] = $row["name"];
			}
		}
		return $nimed;
	}
	
	function loe_unique($sis){
		$out = array();
		foreach($sis as &$s){
			if(!in_array($s['person_id'], $out)){
				array_push($out, $s['person_id']);
			}
		}
		return count($out);
	}
	
	function sum_kool($conn){
		$koolid = get_schools($conn);
		$out="<center><table class='sortable'>";
		$out.="<tr><th>NIMI</th><th>OSAVÕTTE</th><th>ÕPILASI</th><th>1. KOHTA</th><th>2. KOHTA</th><th>3. KOHTA</th></tr>";
		foreach($koolid as &$k){
			$conts=cont_by_school($conn, $k['id']);
			$out.="<tr><td>".$k['name']."</td>";
			$out.="<td>".count($conts)."</td>";
			$out.="<td>".loe_unique($conts)."</td>";
			$out.="<td>".count(cont_place_by_school($conn, $k['id'], "1"))."</td>";
			$out.="<td>".count(cont_place_by_school($conn, $k['id'], "2"))."</td>";
			$out.="<td>".count(cont_place_by_school($conn, $k['id'], "3"))."</td></tr>";
		}
		$out.="</table></center>";
		return $out;
	}
}?>