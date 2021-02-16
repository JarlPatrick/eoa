<?php namespace sidenav {
	
	function get_all($conn, $tbname){
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
	
	function get_all_by_id($conn, $tbname){
		$sis = get_all($conn, $tbname);
		$out = array();
		foreach($sis as $s){
			$out[$s['id']] = $s['name'];
		}
		return $out;
	}
	
	function get_table($conn, $tbname, $sis){
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
	
	function get_sidenav($conn){
		$ained = get_all($conn, "subject");
		$aastad = get_all($conn, "year");
		$type = get_all_by_id($conn, "type");
		$vanus = get_all_by_id($conn, "age_group");
		
		usort($aastad, function($a, $b) {
			return $b['name'] <=> $a['name'];
		});
		
		$out = '<div id="mySidenav" class="sidenav"><a href="javascript:void(0)" class="closebtn" onclick="closeNav()">&times;</a>';
		foreach($ained as &$aine){
			$out .= '<button class="accordion">'.$aine['name'].'</button><div class="panel" id="s'.$aine['id'].'">';
			foreach($aastad as &$aasta){
				$comps = get_table($conn, "contest", "WHERE subject_id=".$aine['id']." AND year_id=".$aasta['id'] );
				if(count($comps) > 0){
					$out .= '<button class="accordion">'.$aasta['name'].'</button><div class="panel" id="s'.$aine['id'].'y'.$aasta['id'].'">';
					foreach($comps as &$comp){
						$out .= '<h1>'.$type[$comp['type_id']].'</h1>';
						$subcomps = get_table($conn, "subcontest", "WHERE contest_id=".$comp['id'] );
						foreach($subcomps as &$subcomp){
							$out .= '<a href="?id='.$subcomp['id'].'">'.$vanus[$subcomp['age_group_id']].'</a>';
						}
					}
					$out .= '</div>';
				}
			}
			$out .= '</div>';
		}
		$out .= '</div><script>initnav();</script>';
		
		return $out;
	}
}?>