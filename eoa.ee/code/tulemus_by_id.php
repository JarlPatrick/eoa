<?php namespace tul_by_id {

function get_title($conn, $id): string {
    $sql = "SELECT subcontest.name AS subcontest_name,
        contest.name AS contest_name, tasks_link FROM subcontest
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

function get_columns($conn, $id): array {
    $sql = "SELECT id, name FROM subcontest_column
        WHERE subcontest_id=".$id.";";
    $result = $conn->query($sql);
    $out = array();
    if ($result->num_rows > 0) {
        while($row = $result->fetch_assoc()) {
            $out[] = $row;
        }
    }
    return $out;
}

function get_contestant_info($conn, $id): array {
    $sql = "SELECT contestant.id AS contestant_id, placement, person_id,
        person.name AS person_name, age_group.name AS age_group_name,
        school_id, school.name AS school_name, mentor_id,
        mentorPerson.name AS mentor_name FROM contestant
        LEFT JOIN person ON contestant.person_id = person.id
        LEFT JOIN age_group ON contestant.age_group_id = age_group.id
        LEFT JOIN school ON contestant.school_id = school.id
        LEFT JOIN mentor ON contestant.id = mentor.contestant_id
        LEFT JOIN person mentorPerson ON mentor.mentor_id = mentorPerson.id
        WHERE subcontest_id=".$id."
        ORDER BY ISNULL(placement), placement;";
    $result = $conn->query($sql);
    $out = array();
    if ($result->num_rows > 0) {
        while($row = $result->fetch_assoc()) {
            $out[] = $row;
        }
    }
    return $out;
}

function get_results($conn, $ids): array {
	$entries = array();
    $idsString = implode(", ", $ids);
    $sql = "SELECT * FROM contestant_field
        WHERE task_id IN (".$idsString.")
        ORDER BY FIELD(task_id, ".$idsString.");";
    $result = $conn->query($sql);
    $resultObjects = array();
    if ($result->num_rows > 0) {
        while($row = $result->fetch_assoc()) {
            $resultObjects[] = $row;
        }
    }
    $oldID = "";
    $entry = array();
    foreach ($resultObjects as $resultObject) {
        $id = $resultObject["task_id"];
        if ($id != $oldID) {
            if ($oldID != "") {
                $entries[$oldID] = $entry;
            }
            $entry = array();
            $oldID = $id;
        }
        $entry[$resultObject["contestant_id"]] = $resultObject["entry"];
    }
    $entries[$oldID] = $entry;
    return $entries;
}

function tulemus($conn, $id): string {
	
	$out = get_title($conn, $id);
	
	$out.="<tr><th>Koht</th>";
	$out.="<th>Nimi</th><th>Klass</th><th>Kool</th><th>Juhendaja</th>";
	$columns = get_columns($conn, $id);
    if (count($columns) == 0) {
        die("<h1>404</h1><div>Lehte ei leitud</div>");
    }
	$taskIDs = array();
    foreach ($columns as $column) {
        $out .= "<th>".$column["name"]."</th>";
        $taskIDs[] = $column["id"];
    }
    $out.="</tr>";
	
	$results = get_results($conn, $taskIDs);

    $contestantInfoObjects = get_contestant_info($conn, $id);
    $mentors = array();
    foreach ($contestantInfoObjects as $index => $contestantInfoObject) {
        $addRow = true;
        if (isset($contestantInfoObjects[$index+1])) {
            if ($contestantInfoObjects[$index+1]["person_id"] == $contestantInfoObject["person_id"]) {
                $addRow = false;
            }
        }
        if ($addRow) {
            $out .= "<tr class='item'><td>".$contestantInfoObject["placement"]."</td><td><a href='?name_id=".$contestantInfoObject["person_id"]."'>".$contestantInfoObject["person_name"]."</a></td>";
            $out .= "<td>".$contestantInfoObject["age_group_name"]."</td><td><a href='?school_id=".$contestantInfoObject["school_id"]."'>".$contestantInfoObject["school_name"]."</a></td>";
            $mentors[] = array("id" => $contestantInfoObject["mentor_id"], "name" => $contestantInfoObject["mentor_name"]);
            $out .="<td>";
            foreach ($mentors as $mentor){
                if (array_search($mentor, $mentors) > 0){$out .=" / ";}
                if (!is_null($mentor["id"])) {
                    $out .="<a href='?name_id=".$mentor["id"]."'>";
                    $out .=$mentor["name"]."</a>";
                }
            }
            $out .="</td>";
            $mentors = array();
            foreach ($taskIDs as $taskID){
                $out .="<td>".$results[$taskID][$contestantInfoObject["contestant_id"]]."</td>";
            }
        } else {
            $mentors[] = array("id" => $contestantInfoObject["mentor_id"], "name" => $contestantInfoObject["mentor_name"]);
        }

    }

	$out .= "</table></div></center>";
	
	return $out;

}

}
