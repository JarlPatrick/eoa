<?php namespace tul_by_id {

function get_title($conn, $id){
	$sql = "SELECT * FROM subcontest WHERE id=".$id.";";
	$result = $conn->query($sql);
	if ($result->num_rows > 0) {
		while($row = $result->fetch_assoc()) {
			$Cid = $row["contest_id"];
			$SCname = $row["name"];
		}
	}
	
	$sql = "SELECT * FROM contest WHERE id=".$Cid.";";
	$result = $conn->query($sql);
	if ($result->num_rows > 0) {
		while($row = $result->fetch_assoc()) {
			$Cname = $row["name"];
		}
	}
	
	$out =  "<center><h1>".$Cname."<br>".$SCname."</h1><table class='sortable'>";
	return $out;
}

function name_by_id($conn, $table_name) {
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

function get_results($conn,$ids){
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

function get_mentor($conn, $id){
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

function tulemus($conn, $id){
	
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
	
	
	$CIsql = "SELECT * FROM contestant where subcontest_id=".$id.";";
	$CIresult = $conn->query($CIsql);
	if ($CIresult->num_rows > 0) {
			// output data of each row
			while($row = $CIresult->fetch_assoc()) {
					$out .= "<tr class='item'><th>".$row["placement"]."</th><th><a href='?name_id=".$row["person_id"]."'>".$nimed[$row["person_id"]]."</a></th>";
					$out .= "<th>".$vanus[$row["age_group_id"]]."</th><th>".$kool[$row["school_id"]]."</th>";
					$mentor = get_mentor($conn, $row["id"]);
					$out .="<th>";
					foreach ($mentor as &$men){
						if(array_search($men, $mentor) > 0){$out .=" / ";}
						$out .="<a href='?name_id=".$men."'>";
						$out .=$nimed[$men]."</a>";
					}$out .="</th>";
					foreach ($nrTask as &$ent){
						$out .="<th>".$results[$ent][$row["id"]]."</th>";
					}
					$out .= "</tr>";
			}
	}
	$out .= "</table></center>";
	
	return $out;

}

}?>