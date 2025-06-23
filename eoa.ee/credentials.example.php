<?php
$servername = getenv("DB_HOST") ?: "mariadb";
$username   = getenv("DB_USER") ?: "eoamanager";
$password   = getenv("DB_PASSWORD");
$dbname     = getenv("DB_NAME") ?: "eoa";
