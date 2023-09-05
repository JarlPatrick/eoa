<?php namespace tul_by_id {

function get_title($conn, $id): string {
    $sql = "SELECT subcontest.id AS id, subcontest.name AS subcontest_name,
    contest.id AS contest_id, contest.name AS contest_name, tasks_link FROM subcontest
    LEFT JOIN contest ON subcontest.contest_id = contest.id
    WHERE subcontest.id=".$id.";";
	$result = $conn->query($sql);
	if ($result->num_rows == 1) {
        $row = $result->fetch_assoc();
        $out = "<center><h1>".$row["contest_name"]."<br>".$row["subcontest_name"]."</h1>";
        if(!empty($row["tasks_link"])){
            $out .= "<h2><a href='".$row["tasks_link"]."'>Ülesanded</a></h2>";
        }
	} else {
        $out = "<center><h1>DATA ERROR</h1>";
    }

	$out .= '<div style="overflow-x:auto;"><table class="sortable">';
	return $out;
}

function name_by_id($conn, $table_name): array {
	$sql = "SELECT id, name FROM ".$table_name.";";
	$result = $conn->query($sql);
	$nimed = array();
	if ($result->num_rows > 0) {
		while($row = $result->fetch_assoc()) {
			$nimed[$row["id"]] = $row["name"];
		}
	}
	return $nimed;
}

function get_results($conn,$ids): array {
	$entrys = array();
	foreach ($ids as &$id){
		$entry = array();
		$sql = "SELECT * FROM contestant_field where task_id=".$id.";";
		$result = $conn->query($sql);
		if ($result->num_rows > 0) {
			while($row = $result->fetch_assoc()) {
				$entry[$row["contestant_id"]] = $row["entry"];
			}
		}
		$entrys[$id] = $entry;
	}
	return $entrys;
}

function get_mentor($conn, $id): array {
	$mentors = array();
	$sql = "SELECT mentor_id FROM mentor where contestant_id=".$id.";";
	$result = $conn->query($sql);
	if ($result->num_rows > 0) {
		while($row = $result->fetch_assoc()) {
			array_push($mentors, $row["mentor_id"]);
		}
	}
	return $mentors;
	
}

function tulemus($conn, $id): string {
	
	$nimed = name_by_id($conn,"person");
	$vanus = name_by_id($conn,"age_group");
	$kool = name_by_id($conn,"school");
	
	$out = get_title($conn, $id);
	
	
	$out.="<tr><th>Koht</th>";
	$out.="<th>Nimi</th><th>Klass</th><th>Kool</th><th>Juhendaja</th>";
	$tasksql = "SELECT * FROM subcontest_column where subcontest_id=".$id.";";
	$taskresult = $conn->query($tasksql);
	$nrTask = array();
	if ($taskresult->num_rows > 0) {
			while($row = $taskresult->fetch_assoc()) {
					$out .= "<th>".$row["name"]."</th>";
					array_push($nrTask, $row["id"]);
			}
	}
	
	$results = get_results($conn, $nrTask);
	
	$out.="</tr>";
	
	
	$CIsql = "SELECT * FROM contestant where subcontest_id=".$id." order by isnull(placement), placement;";
	$CIresult = $conn->query($CIsql);
	if ($CIresult->num_rows > 0) {
			// output data of each row
			while($row = $CIresult->fetch_assoc()) {
					$out .= "<tr class='item'><td>".$row["placement"]."</td><td><a href='?name_id=".$row["person_id"]."'>".$nimed[$row["person_id"]]."</a></td>";
					$out .= "<td>".$vanus[$row["age_group_id"]]."</td><td><a href='?school_id=".$row["school_id"]."'>".$kool[$row["school_id"]]."</a></td>";
					$mentor = get_mentor($conn, $row["id"]);
					$out .="<td>";
					foreach ($mentor as &$men){
						if(array_search($men, $mentor) > 0){$out .=" / ";}
						$out .="<a href='?name_id=".$men."'>";
						$out .=$nimed[$men]."</a>";
					}$out .="</td>";
					foreach ($nrTask as &$ent){
						$out .="<td>".$results[$ent][$row["id"]]."</td>";
					}
					$out .= "</tr>";
			}
	}
	$out .= "</table></div></center>";
	
	return $out;

}

}
