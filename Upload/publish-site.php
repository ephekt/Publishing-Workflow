<html>
  <body>

<?php
// prepend a base path if Predis is not present in your "include_path".
require 'Predis/Autoloader.php';

Predis\Autoloader::register();

//Hostname for Redis server
define("REDIS_HOST", "10.12.27.245");
//Channel to inform process workers of new work
define("PROCESS_CHANNEL", "Process City Data");
//List to push new jobs onto
define("WORK_QUEUE", "processCD");
//Message to send to channel to indicate work needs to be done
define("WORK_MESSAGE", "process");
//Path to dump uploaded files for sftp
define("UPLOAD_PATH", "/home/user/Delphi/test");
//The location of the machine info for the joyent servers
define("MACHINE_INFO", "/etc/delphi/data/machineinfo.json");

class UploadedFile{
/*********************************************************************************//**
 *  WebApplication
 *====================================================================================
 * @author Abbey Hawk Sparrow
 *An application abstraction, so the app doesn't directly reference any specific server
 *************************************************************************************/
    protected $name;
    public function  __construct($name){
        $this->name = $name;
    }

    public function exists(){
        $res = array_key_exists($this->name, $_FILES);
        return $res;
    }

    public function saveAs($path){
        move_uploaded_file($_FILES[$this->name]['tmp_name'], $path);
        chmod($path , 0755);
        return file_exists($path);
    }

    public function tempName(){
      return $_FILES[$this->name]['tmp_name'];
    }

    public function remoteName(){
        return $_FILES[$this->name]['name'];
    }

    public function size(){
        return $_FILES[$this->name]['size'];
    }

    public function type(){
        return $_FILES[$this->name]['type'];
    }

    public function read(){
        return file_get_contents($_FILES[$this->name]['tmp_name']);
    }
}

class Upload{
  public static function uploadedFile($name){
    $file = new UploadedFile($name);
    if($file->exists()) return $file;
    return false;
  }

  private function publishSite(){
    $connection = ssh2_connect($message->payload->host, 22);
    //ssh2_auth_password($connection, 'username', 'password');

    $sftp = ssh2_sftp($connection);
    $stream = fopen("ssh2.sftp://".$message->payload->path, 'r');
    //Process data      
    //Redirect to site
  }

  public function uploadData(){
    $identstr = file_get_contents(MACHINE_INFO);
    $info = json_decode($identstr);
    $info = $info->identity;
      //This should reflect potentially multiple uploads
      //Uhh, or something like that
    $cityData = Upload::uploadedFile("uploaded");
    if ($cityData === false){
      echo "Upload failed";
      return;
    }

    //TODO: Channel should be hash of all uploaded file paths
    $channel = sha1($cityData->tempName());
    //TODO: Make neccessary directories?
    $uploadLocation = UPLOAD_PATH . $channel;
    $cityData->saveAs($uploadLocation);
    $redis = new Predis\Client(array(
    'scheme' => 'tcp',
    'host'   => REDIS_HOST,
    'read_write_timeout' => 0));

    $r2 = new Predis\Client(array(
    'scheme' => 'tcp',
    'host'   => REDIS_HOST,
    'read_write_timeout' => 0));

    $job = array('path' => $uploadLocation, 'host' => $info->private_ip, 'hash' => $channel);

    $redis->rpush(WORK_QUEUE, json_encode($job));
    $pubsub = $redis->pubSub();
    $pubsub->subscribe($channel); 
    $r2->publish(PROCESS_CHANNEL, WORK_MESSAGE);
    $r2->quit();

    foreach ($pubsub as $message) {
      echo $message->payload;
      switch ($message->kind) {
      case 'message':
        //$payload = json_encode($message->payload);
        switch ($payload) {
        case 'success':
          $pubsub->unsubscribe();
          unset($pubsub);
          echo "success";
          break;
        case 'failure':
          $pubsub->unsubscribe();
          unset($pubsub);
          echo "failure";
          //Notify them that a human needs to look at it

          break;
        }
      }
    }
  }
}


Upload::uploadData()
?>
  </body>
</html>