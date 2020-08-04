<?php namespace hof {	
	function all_names($conn) {
		$sql = "SELECT * FROM person;";
		$result = $conn->query($sql);
		$nimi = array();
		if ($result->num_rows > 0) {
			while($row = $result->fetch_assoc()) {
				$nimi[$row['id']] = $row["name"];
			}
		}
		return $nimi;
	}
	
	function all_conts($conn) {
		$sql = "SELECT * FROM contestant;";
		$result = $conn->query($sql);
		$out = array();
		if ($result->num_rows > 0) {
			while($row = $result->fetch_assoc()) {
				array_push($out, $row);
			}
		}
		return $out;
	}
	
	function hof($conn){
		$nimed = all_names($conn);
		$conts = all_conts($conn);
		$students = array();
		
		
		foreach($conts as &$c){
			$students[$c['person_id']][0]=$c['person_id'];
			$students[$c['person_id']][1]=$nimed[$c['person_id']];
			
			if(isset($students[$c['person_id']][2])){	$students[$c['person_id']][2]+=1;
			}else{	$students[$c['person_id']][2]=1;	}
			
			if(!isset($students[$c['person_id']][3])){	$students[$c['person_id']][3]=0;	}			
			if($c['placement'] == 1){	$students[$c['person_id']][3]+=1;	}
			
			if(!isset($students[$c['person_id']][4])){	$students[$c['person_id']][4]=0;	}			
			if($c['placement'] == 2){	$students[$c['person_id']][4]+=1;	}
			
			if(!isset($students[$c['person_id']][5])){	$students[$c['person_id']][5]=0;	}			
			if($c['placement'] == 3){	$students[$c['person_id']][5]+=1;	}
			
		}
		
		usort($students, function($a, $b) {	return $b[3] <=> $a[3];	});
		
		$out="<center><table class='sortable'>";
		$out.="<tr><th>NIMI</th><th>OSAVÕTTE</th><th>1. KOHTI</th><th>2. KOHTI</th><th>3. KOHTI</th></tr>";
		foreach($students as &$s){
			if($s[3] + $s[4] + $s[5] > 0){
				$out.="<tr><th><a href='?name_id=".$s[0]."'>".$s[1]."</a></th><th>".$s[2]."</th><th>".$s[3]."</th><th>".$s[4]."</th><th>".$s[5]."</th></tr>";
			}
		}
		$out.="</table></center>";
		return $out;
	}
}?>