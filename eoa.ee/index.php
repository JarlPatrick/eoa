<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Eesti Olümpiaadide Andmebaas</title>
    <meta name="google-site-verification" content=
    "m3yEMb5b8lxEu4ueaXfeF4SYYjskkfaMiyVRUtXvEHE">
    <meta name="viewport" content=
    "width=device-width, initial-scale=1">
    <link rel="stylesheet" href="/eoa.css">
    <script src="sorttable.js" type="text/javascript"></script>
    <script>

    function findperson(){
        if (document.getElementById('NIF').value != '') {
            var address = '/?name=' + document.getElementById('NIF').value;
            location.href = address;
        }
    }

    function search(ele) {
        if (event.key === 'Enter') {
            findperson();
        }
    }

    var openPanels;
    const panelKey = "sidenav-open-panels";
    const sidenavOpenKey = "sidenav-open";
    const sidenavScrollKey = "sidenav-scroll";
    var sidenavRoot;

    /* Set the width of the side navigation to 250px and the left margin of the page content to 250px, save the state */
    function openNav() {
        document.getElementById("mySidenav").style.width = "400px";
        document.getElementById("main").style.marginLeft = "400px";
        sessionStorage.setItem(sidenavOpenKey, "1");
    }

    /* Set the width of the side navigation to 0 and the left margin of the page content to 0, save the state */
    function closeNav() {
        document.getElementById("mySidenav").style.width = "0";
        document.getElementById("main").style.marginLeft = "0";
        sessionStorage.setItem(sidenavOpenKey, "");
    }

	function initnav(){
        sidenavRoot = document.getElementById("mySidenav");
        var acc = document.getElementsByClassName("accordion");
        var i;
        for (i = 0; i < acc.length; i++) {
            acc[i].addEventListener("click", function () {
                /* Toggle between adding and removing the "active" class,
                to highlight the button that controls the panel */
                this.classList.toggle("active");

                /* Toggle between hiding and showing the active panel */
                var panel = this.nextElementSibling;
                if (panel.style.display === "block") {
                    panel.style.display = "none";
                    openPanels.delete(panel.id);
                } else {
                    panel.style.display = "block";
                    openPanels.add(panel.id);
                }

                /* Update open panels */
                sessionStorage.setItem(panelKey, JSON.stringify([...openPanels]));
            });
        }

        /* Load open panels (none on first load) */
        if(!sessionStorage.getItem(panelKey)) {
            sessionStorage.setItem(panelKey, "[]");
        }
        openPanels = new Set(JSON.parse(sessionStorage.getItem(panelKey)));
        openPanels.forEach(id => {
            const el = document.getElementById(id);
            if(el) {
                el.style.display = "block";
                el.previousElementSibling.classList.toggle("active");
            }
        });

        /* Load menu open/closed state (closed on first load) */
        if(sessionStorage.getItem(sidenavOpenKey)) {
            openNav();
        }

        /* Load menu scroll (0 on first load) */
        if(!sessionStorage.getItem(sidenavScrollKey)) {
            sessionStorage.setItem(sidenavScrollKey, 0);
        }
        sidenavRoot.scrollTop = sessionStorage.getItem(sidenavScrollKey);
        sidenavRoot.addEventListener("scroll", function() {
            sessionStorage.setItem(sidenavScrollKey, sidenavRoot.scrollTop);
        });
	}
    </script>
</head>
<body>
    <div id="main">
        <div class="topnav">
            <a onclick="openNav()">
            <div class="manubtn"></div>
            <div class="manubtn"></div>
            <div class="manubtn"></div></a>
            <h1><a href="/">EESTI OLÜMPIAADIDE
            ANDMEBAAS</a></h1>
            <h1><a href="/?kool=true">KOOLID</a></h1>
            <h1><a href="/?hof=true">AUTABEL</a></h1>
            <div class="search-container">
                <button type="button" onclick=
                "findperson()">OTSI</button> <input type="text"
                placeholder="Õpilase/Juhendaja nimi..." name=
                "nameinput" id="NIF" onkeydown="search(this)">
            </div>
        </div>

<?php

include 'credentials.php';

$conn = new mysqli($servername, $username, $password, $dbname);

if ($conn->connect_error) {
	echo 'fail';
    die("Connection failed: " . $conn->connect_error);
}

require('code/esialgsed.php');
require('code/tulemus_by_id.php');
require('code/name_search.php');
require('code/sidenav.php');
require('code/mainpage.php');
require('code/koolid.php');
require('code/hof.php');

echo sidenav\get_sidenav($conn);

$queries = array();
parse_str($_SERVER['QUERY_STRING'], $queries);
if(!empty($queries['id'])){
	if((int)$queries['id'] > 0 and (int)$queries['id'] < 10000){
			echo tul_by_id\tulemus($conn,(int)$queries['id']);
	}
	/*if((int)$queries['id'] == 10000){
		$url2='https://docs.google.com/spreadsheets/d/e/2PACX-1vQsE0RId6TO33wjVXW_5I4rFbCuTn9lP7B02vEWRExfs5ZncIbPKlzuzydtWGRhf8z8uN-ZucoCCMIV/pub?output=csv';
		echo esialgsed\esialg($url2,6,"EMO sügisene lahtine noorem (ESIALGSED)","mata");
	}
	if((int)$queries['id'] == 10001){
		$url2='https://docs.google.com/spreadsheets/d/e/2PACX-1vQsE0RId6TO33wjVXW_5I4rFbCuTn9lP7B02vEWRExfs5ZncIbPKlzuzydtWGRhf8z8uN-ZucoCCMIV/pub?output=csv&single=true&gid=318187998';
		echo esialgsed\esialg($url2,6,"EMO sügisene lahtine vanem (ESIALGSED)","mata");
	}*/
}elseif(!empty($queries['name'])){
	echo name_s\search($conn, $queries['name']);
}elseif(!empty($queries['name_id'])){
	if((int)$queries['name_id'] > 0 and (int)$queries['name_id'] < 10000){
		echo name_s\single_name($conn, $queries['name_id']);
	}
}elseif(!empty($queries['kool'])){
	echo koolid\sum_kool($conn);
}elseif(!empty($queries['hof'])){
	echo hof\hof($conn);
}else{
	echo mainpage\get_mainpage($conn);
}

$conn->close();

?>
    </div>
</body>
</html>
