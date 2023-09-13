<?php

include 'credentials.php';

$conn = new mysqli($servername, $username, $password, $dbname);

if ($conn->connect_error) {
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

$page_content = array();
if(!empty($_GET['id'])){
  if((int)$_GET['id'] > 0){
    $page_content = tul_by_id\tulemus($conn,(int)$_GET['id']);
  }
}elseif(!empty($_GET['name'])){
  $page_content = name_s\search($conn, $_GET['name']);
}elseif(!empty($_GET['name_id'])){
  if((int)$_GET['name_id'] > 0){
    $page_content = name_s\person_profile($conn, $_GET['name_id']);
  }
}elseif(!empty($_GET['kool'])){
  $page_content = koolid\sum_kool($conn);
}elseif(!empty($_GET['hof'])){
  $page_content = hof\hof($conn);
}elseif(!empty($_GET['school_id'])){
  if((int)$_GET['school_id'] > 0){
    $page_content = school_profile\get_profile($conn, $_GET['school_id']);
  }
}else{
  $page_content = mainpage\get_mainpage($conn);
}
http_response_code($page_content['status']);
?>
<!DOCTYPE html>
<html>
  <head>
    <meta charset="UTF-8">
    <title><?= $page_content['title'] ?></title>
    <meta name="google-site-verification" content=
                "m3yEMb5b8lxEu4ueaXfeF4SYYjskkfaMiyVRUtXvEHE">
    <meta name="viewport" content=
                "width=device-width, initial-scale=1">
<?php
if($_SERVER['REQUEST_URI'] != '/')
    echo '<meta name="robots" content="noindex">';
?>
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

echo sidenav\get_sidenav($conn);

echo $page_content['content'];

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
