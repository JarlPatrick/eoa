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
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css">
    <script src="sorttable.js" type="text/javascript"></script>
    <script src="eoa.js" type="text/javascript"></script>
  </head>
  <body>
    <div id="main">
      <div id="header">
        <div class="topnav">
          <a onclick="openNav()">
            <i class="fa fa-bars"></i>
          </a>
          <a href="/"><i class="fa fa-home"></i></a>
          <a href="/?kool=true">Koolid</a>
          <a href="/?hof=true">Autabel</a>
          <div class="search-container">
            <input type="text" placeholder="Nimi..."
                   name="nameinput" id="NIF" onkeydown="search(this)">
            <button type="submit" onclick="findperson()">
              <i class="fa fa-search"></i>
            </button>
          </div>
        </div>
      </div>
      <div id="body">
<?php

include 'credentials.php';

$conn = new mysqli($servername, $username, $password, $dbname);

if ($conn->connect_error) {
  echo "fail";
  die("Connection failed: " . $conn->connect_error);
}

require('code/esialgsed.php');
require('code/tulemus_by_id.php');
require('code/name_search.php');
require('code/sidenav.php');
require('code/mainpage.php');
require('code/koolid.php');
require('code/hof.php');
require('code/school_profile.php');

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
    echo name_s\person_profile($conn, $queries['name_id']);
  }
}elseif(!empty($queries['kool'])){
  echo koolid\sum_kool($conn);
}elseif(!empty($queries['hof'])){
  echo hof\hof($conn);
}elseif(!empty($queries['school_id'])){
  if((int)$queries['school_id'] > 0 and (int)$queries['school_id'] < 10000){
    echo school_profile\get_profile($conn, $queries['school_id']);
  }
}else{
  echo mainpage\get_mainpage($conn);
}

$conn->close();
?>
      </div>
      <div id="footer">
        <hr>
        Eesti Olümpiaadide Andmebaas
        <a style="float: right" href="mailto:eoakontakt@gmail.com">Kontakt: eoakontakt@gmail.com</a>
      </div>
    </div>
  </body>
</html>
