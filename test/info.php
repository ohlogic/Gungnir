

<html>
<body>

<h1>Welcome</h1>

<?php
error_reporting(E_ALL);
ini_set('display_errors', true);

ob_start();
phpinfo();
$info = ob_get_contents();
$info = str_replace("\n", "\n<br>", $info);
ob_end_clean();
echo $info;

?>

