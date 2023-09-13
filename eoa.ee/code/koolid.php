<?php namespace koolid {
	
	function get_schools($conn): array {
		$sql = "SELECT school.name name, school.id id, count(*) participations, count(distinct contestant.person_id) students,
				count(case when contestant.placement = 1 then 1 end) place1,
				count(case when contestant.placement = 2 then 1 end) place2,
				count(case when contestant.placement = 3 then 1 end) place3
			FROM school INNER JOIN contestant ON contestant.school_id = school.id GROUP BY school.id
			ORDER BY participations DESC, place1 + place2 + place3 DESC, place1 DESC, place2 DESC, place3 DESC;";
		$result = $conn->query($sql);
		$nimed = array();
		if ($result->num_rows > 0) {
			while($row = $result->fetch_assoc()) {
				array_push($nimed, $row);
			}
		}
		return $nimed;
	}
	
	function sum_kool($conn): array {
		$koolid = get_schools($conn);
		$out="<center><table class='sortable'>";
		$out.="<tr><th>NIMI</th><th>OSAVÕTTE</th><th>ÕPILASI</th><th>1. KOHTA</th><th>2. KOHTA</th><th>3. KOHTA</th></tr>";
		foreach($koolid as &$k){
			$out.="<tr><td><a href='?school_id=".$k['id']."'>".$k['name']."</a></td>";
			$out.="<td>".$k['participations']."</td>";
			$out.="<td>".$k['students']."</td>";
			$out.="<td>".$k['place1']."</td>";
			$out.="<td>".$k['place2']."</td>";
			$out.="<td>".$k['place3']."</td></tr>";
		}
		$out.="</table></center>";
		return array("content" => $out, "status" => 200, "title" => "Koolid - EOA");
	}
}
