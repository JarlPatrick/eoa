<?php namespace tul_by_id {

function get_title($conn, $id): array {
    $sql = "SELECT subcontest.name AS subcontest_name,
        contest.name AS contest_name, tasks_link, description, age_group.name AS group_name
        FROM subcontest
        LEFT JOIN contest ON subcontest.contest_id = contest.id
        LEFT JOIN age_group ON subcontest.age_group_id = age_group.id
        WHERE subcontest.id=".$id.";";
    $result = $conn->query($sql);
    $footer = "";
	if ($result->num_rows == 1) {
        $row = $result->fetch_assoc();
        $out = "<center><h1>".$row["contest_name"]."<br>".$row["subcontest_name"]."</h1>";
        $title = $row["contest_name"] . " - " . $row["group_name"];
        if(!empty($row["tasks_link"])){
            $out .= "<h2><a href='".$row["tasks_link"]."'>Ülesanded</a></h2>";
        }
        if(!empty($row["description"])) {
            $footer .= "<p>".htmlspecialchars($row["description"])."</p>";
        }
	} else {
        return ["found" => false];
    }

	$out .= '<div style="overflow-x:auto;"><table class="sortable">';
	return ["found" => true, "title" => $title, "html" => $out, "footer" => $footer];
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
        ORDER BY ISNULL(placement), placement, contestant_id;";
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
    if($idsString == "") return array();
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

function has_content($objects, $col): bool {
    foreach ($objects as $object) {
        if(!is_null($object[$col])) {
            return true;
        }
    }
    return false;
}

function tulemus($conn, $id): array {
	
    $out = get_title($conn, $id);
    if(!$out["found"]) {
        return array("content" => "<h1>404</h1><div>Lehte ei leitud</div>",
            "status" => 404,
            "title" => "404 - EOA");
    }
    $title = $out["title"];
    $footer = $out["footer"];
    $out = $out["html"];
	$columns = get_columns($conn, $id);

    $contestantInfoObjects = get_contestant_info($conn, $id);
    $ageGroupHasContent = has_content($contestantInfoObjects, "age_group_name");
    $schoolHasContent = has_content($contestantInfoObjects, "school_id");
    $mentorHasContent = has_content($contestantInfoObjects, "mentor_id");

    $out .= "<tr><th>Koht</th>";
    $out .= "<th>Nimi</th>";
    $out .= $ageGroupHasContent ? "<th>Klass</th>" : "";
    $out .= $schoolHasContent ? "<th>Kool</th>" : "";
    $out .= $mentorHasContent ? "<th>Juhendaja</th>" : "";
    $taskIDs = array();
    foreach ($columns as $column) {
        $out .= "<th>".$column["name"]."</th>";
        $taskIDs[] = $column["id"];
    }
    $out.="</tr>";

    $results = get_results($conn, $taskIDs);
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
            $out .= $ageGroupHasContent ? "<td>".$contestantInfoObject["age_group_name"]."</td>" : "";
            $out .= $schoolHasContent ? "<td><a href='?school_id=".$contestantInfoObject["school_id"]."'>".$contestantInfoObject["school_name"]."</a></td>" : "";
            if ($mentorHasContent) {
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
            }
            foreach ($taskIDs as $taskID){
                $out .="<td>".$results[$taskID][$contestantInfoObject["contestant_id"]]."</td>";
            }
        } else {
            $mentors[] = array("id" => $contestantInfoObject["mentor_id"], "name" => $contestantInfoObject["mentor_name"]);
        }

    }

	$out .= "</table></div>" . $footer . "</center>";
	
	return array("title" => $title." - EOA",
                    "content" => $out,
                    "status" => 200);

}

}
