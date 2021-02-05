<?php

$servername = "localhost";
$username = "";
$password = "";
$dbname = "eoa";

$conn = new mysqli($servername, $username, $password, $dbname);

if ($conn->connect_error) {
	echo 'fail';
    die("Connection failed: " . $conn->connect_error);
}

$myfile = fopen("main.html","r") or die ("error");
echo fread($myfile,filesize("main.html"));
fclose($myfile);

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


echo "</body></html>";

?>
