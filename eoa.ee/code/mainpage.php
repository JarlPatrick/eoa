<?php namespace mainpage {

    function get_count($conn, $tableName): int {
        $sql = "SELECT COUNT(*) AS count FROM ".$tableName.";";
        $result = $conn->query($sql);
        return ($result->fetch_assoc())['count'];
    }

    function get_count_distinct($conn, $tableName, $column): int {
        $sql = "SELECT COUNT(DISTINCT $column) AS count FROM ".$tableName.";";
        $result = $conn->query($sql);
        return ($result->fetch_assoc())['count'];
    }

    function get_contests($conn, $year): array {
        $sql = "SELECT contest.id AS id, contest.name as contest_name,
        subcontest.id as subcontest_id, subcontest.name as subcontest_name FROM contest
        LEFT JOIN subcontest ON contest.id = subcontest.contest_id
        WHERE year = ".$year.";";
        $result = $conn->query($sql);
        $out = array();
        if ($result->num_rows > 0) {
            while($row = $result->fetch_assoc()) {
                $out[] = $row;
            }
        }
        return $out;
    }

	function main_stats($conn): string {
		$names = get_count($conn, "person");
		$schools = get_count($conn, "school");
		$subject = get_count($conn, "subject");
		$contest = get_count($conn, "contest");
		$year = get_count_distinct($conn, "contest", "year");
		
		$out = "<h2>Praeguse seisuga on andmebaasi sisestatud:</h2>";
		$out .= "<h3>".$subject." õppeaines ".$contest." võistlust ".$year." aasta jooksul</h3>";
		$out .= "<h3>".$names." inimest ".$schools." koolist</h3>";
		
		return $out;
	}
	
	function this_year_results($conn): string {
        $currentYear = date("Y");
        $currentMonth = date("n");
        if ($currentMonth < 9) {
            $currentYear -= 1;
        }
        $contestObjects = get_contests($conn, $currentYear);
        if (count($contestObjects) == 0) {
            $currentYear -= 1;
            $contestObjects = get_contests($conn, $currentYear);
            $out = "<br><h2>Eelmise õppeaasta tulemused (".($currentYear)."/".($currentYear+1).")</h2>";
        } else {
            $out = "<br><h2>Praeguse õppeaasta tulemused (".($currentYear)."/".($currentYear+1).")</h2>";
        }

        $oldContest = "";
		foreach($contestObjects as $contestObject){
            $contest = $contestObject['id'];
            if ($contest != $oldContest) {
                $oldContest = $contest;
                $out .="<h3>".$contestObject['contest_name']."</h3>";
            }
            $out .='<a href="?id='.$contestObject['subcontest_id'].'">'.$contestObject['subcontest_name'].'</a><br>';
		}
		return $out;
	}
	
	function get_mainpage($conn): array {
		$out = "<center>";
		$out .= "<h1>Tegemist on Eesti olümpiaadide andmebaasi koduleheküljega</h1><br>";
		$out .= main_stats($conn);
		$out .= this_year_results($conn);
		$out .= "</center>";
                return array("title" => "Eesti Olümpiaadide Andmebaas",
                    "content" => $out,
                    "status" => 200);
	}

}
