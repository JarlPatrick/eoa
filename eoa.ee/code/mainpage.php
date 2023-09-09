<?php namespace mainpage {
	
	function get_all($conn, $tbname): array {
		$sql = "SELECT * FROM ".$tbname.";";
		$result = $conn->query($sql);
		$out = array();
		if ($result->num_rows > 0) {
			while($row = $result->fetch_assoc()) {
				array_push($out, $row);
			}
		}
		return $out;
	}
	
	function get_table($conn, $tbname, $sis): array {
		$sql = "SELECT * FROM ".$tbname." ".$sis.";";
		$result = $conn->query($sql);
		$out = array();
		if ($result->num_rows > 0) {
			while($row = $result->fetch_assoc()) {
				array_push($out, $row);
			}
		}
		return $out;
	}

	function main_stats($conn): string {
		$names = get_all($conn, "person");
		$schools = get_all($conn, "school");
		$subject = get_all($conn, "subject");
		$contest = get_all($conn, "contest");
		$year = get_all($conn, "year");
		
		$out = "<h2>Praeguse seisuga on andmebaasi sisestatud:</h2>";
		$out .= "<h3>".count($subject)." õppeaines ".count($contest)." võistlust ".count($year)." aasta jooksul</h3>";
		$out .= "<h3>".count($names)." inimest ".count($schools)." koolist</h3>";
		
		return $out;
	}
	
	function this_year_results($conn): string {
        $currentYear = date("Y");
        $currentMonth = date("n");
        if ($currentMonth < 9) {
            $currentYear -= 1;
        }
        $contests = get_table($conn, "contest", "WHERE year=".$currentYear );
        if (count($contests) == 0) {
            $currentYear -= 1;
            $contests = get_table($conn, "contest", "WHERE year=".$currentYear );
            $out = "<br><h2>Eelmise õppeaasta tulemused (".($currentYear)."/".($currentYear+1).")</h2>";
        } else {
            $out = "<br><h2>Praeguse õppeaasta tulemused (".($currentYear)."/".($currentYear+1).")</h2>";
        }
		foreach($contests as $c){
			$out .="<h3>".$c['name']."</h3>";
			$subcontests = get_table($conn, "subcontest", "WHERE contest_id=".$c['id'] );
			foreach($subcontests as $s){
				$out .='<a href="?id='.$s['id'].'">'.$s['name'].'</a><br>';
			}
		}
		return $out;
	}
	
	function get_mainpage($conn): string {
		$out = "<center>";
		$out .= "<h1>Tegemist on Eesti olümpiaadide andmebaasi koduleheküljega</h1><br>";
		$out .= main_stats($conn);
		$out .= this_year_results($conn);
		$out .= "</center>";
		return $out;
	}

}
