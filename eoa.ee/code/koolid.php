<?php namespace koolid {
	
	function get_schools($conn): array {
		$sql = "SELECT school.name name, school.id id, COUNT(*) participations, COUNT(DISTINCT contestant.person_id) students,
				COUNT(CASE WHEN contestant.placement = 1 THEN 1 END) place1,
				COUNT(CASE WHEN contestant.placement = 2 THEN 1 END) place2,
				COUNT(CASE WHEN contestant.placement = 3 THEN 1 END) place3,
                COUNT(CASE WHEN contestant.placement >= 1 AND contestant.placement <= 3 THEN 1 END) places_top3
			FROM school INNER JOIN contestant ON contestant.school_id = school.id GROUP BY school.id
			ORDER BY participations DESC, places_top3 DESC, place1 DESC, place2 DESC, place3 DESC;";
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
			$out.="<td sorttable_customkey=".-$k['participations'].">".$k['participations']."</td>";
			$out.="<td sorttable_customkey=".-$k['students'].">".$k['students']."</td>";
			$out.="<td sorttable_customkey=".-$k['place1'].">".$k['place1']."</td>";
			$out.="<td sorttable_customkey=".-$k['place2'].">".$k['place2']."</td>";
			$out.="<td sorttable_customkey=".-$k['place3'].">".$k['place3']."</td></tr>";
		}
		$out.="</table></center>";
		return array("content" => $out, "status" => 200, "title" => "Koolid - EOA");
	}
}
