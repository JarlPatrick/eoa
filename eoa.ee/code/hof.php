<?php namespace hof {	
	function get_students($conn): array {
		$sql = "SELECT person.id id, person.name name, COUNT(*) participations,
				COUNT(CASE WHEN contestant.placement = 1 THEN 1 END) place1,
				COUNT(CASE WHEN contestant.placement = 2 THEN 1 END) place2,
				COUNT(CASE WHEN contestant.placement = 3 THEN 1 END) place3
			FROM person INNER JOIN contestant ON contestant.person_id = person.id GROUP BY person.id
			HAVING place1 + place2 + place3 > 0 OR participations >= 8
			ORDER BY participations DESC, place1 + place2 + place3 DESC, place1 DESC, place2 DESC, place3 DESC;";
		$result = $conn->query($sql);
		$students = array();
		if ($result->num_rows > 0) {
			while($row = $result->fetch_assoc()) {
				array_push($students, $row);
			}
		}
		return $students;
	}
	
	function hof($conn): array {
		$students = get_students($conn);
		
		$out="<center><h1>Enim olümpiaadidest osa võtnud õpilased:</h1>";
		$out.="<table class='sortable'>";
		$out.="<tr><th>NIMI</th><th>OSAVÕTTE</th><th>1. KOHTI</th><th>2. KOHTI</th><th>3. KOHTI</th></tr>";
		foreach($students as &$s){
			$out.="<tr><td><a href='?name_id=".$s["id"]."'>".$s["name"]."</a></td><td>".$s["participations"]."</td><td>".$s["place1"]."</td><td>".$s["place2"]."</td><td>".$s["place3"]."</td></tr>";
		}
		$out.="</table></center>";
		return array("content" => $out, "status" => 200, "title" => "Autabel - EOA");
	}
}
