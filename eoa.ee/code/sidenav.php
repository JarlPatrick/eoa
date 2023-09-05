<?php namespace sidenav {
    function get_contests($conn): array {
        $sql = "SELECT contest.id as id, subject_id, subject.name as subject_name,
            year_id, year.name as year_name, type.name as type_name, subcontest.id as subcontest_id,
            age_group.name as age_group_name FROM contest
            LEFT JOIN subject ON contest.subject_id = subject.id
            LEFT JOIN year ON contest.year_id = year.id
            LEFT JOIN type ON contest.type_id = type.id
            LEFT JOIN subcontest ON contest.id = subcontest.contest_id
            LEFT JOIN age_group ON subcontest.age_group_id = age_group.id
            ORDER BY subject_id, year.name DESC,
            FIELD(type_id, 17, 18, 20, 16, 19, 21, 1) DESC,
            FIELD(age_group.name,'1', '2', '3', '4', '5', '6', '7', '8', '7-8', '9',
                'Põhikool B- ja C-keel', 'Põhikool A-keel', 'Põhikool', '10', '9-10', 'Noorem',
                '11', '12', '11-12', 'Vanem', 'Gümnaasium B- ja C-keel', 'Gümnaasium A-keel', 'Gümnaasium',
                'Koond', 'Avatud') DESC;";
        $result = $conn->query($sql);
        $out = array();
        if ($result->num_rows > 0) {
            while($row = $result->fetch_assoc()) {
                $out[] = $row;
            }
        }
        return $out;
    }
	
	function get_sidenav($conn): string {
        $contestObjects = get_contests($conn);
        $subject = "";
        $year = "";
        $contest = "";
        $subContest = "";

        $out = '<div id="mySidenav" class="sidenav"><a href="javascript:void(0)" class="closebtn" onclick="closeNav()">&times;</a>';
        foreach ($contestObjects as $contestObject) {
            $aine = $contestObject['subject_id'];
            $aasta = $contestObject['year_id'];
            $comp = $contestObject['id'];
            $subComp = $contestObject['subcontest_id'];
            if ($aine != $subject) {
                if ($subject != "") {
                    $out .= '</div></div>';
                }
                $subject = $aine;
                $out .= '<button class="accordion">'.$contestObject['subject_name'].'</button><div class="panel" id="s'.$aine.'">';
                $year = "";
            } if ($aasta != $year) {
                if ($year != "") {
                    $out .= '</div>';
                }
                $year = $aasta;
                $out .= '<button class="accordion">'.$contestObject['year_name'].'</button><div class="panel" id="s'.$aine.'y'.$aasta.'">';
            } if ($comp != $contest) {
                $contest = $comp;
                $out .= '<h1>'.$contestObject['type_name'].'</h1>';
            } if ($subComp != $subContest) {
                $subContest = $subComp;
                $out .= '<a href="?id='.$subComp.'">'.$contestObject['age_group_name'].'</a>';
            }
        }
        if ($subject != "") {
            $out .= '</div></div>';
        }
		$out .= '</div><script>initnav();</script>';
		
		return $out;
	}
}
