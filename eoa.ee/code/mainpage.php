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
		$Cid = "54";
		#$out="<br><h2>Mata sügisese lahtise ESIALGSED tulemused (2020)</h2>";
		#$out.='<a href="?id=10000">NOOREM</a><br>';
		#$out.='<a href="?id=10001">VANEM</a>';
		$out = "<br><h2>Praeguse õppeaasta tulemused (2020/2021)</h2>";
		$contests = get_table($conn, "contest", "WHERE year_id=".$Cid );
		foreach($contests as &$c){
			$out .="<h3>".$c['name']."</h3>";
			$subcontests = get_table($conn, "subcontest", "WHERE contest_id=".$c['id'] );
			foreach($subcontests as &$s){
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
