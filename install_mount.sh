echo "Setup Script for YouTube Downloader on Pterodactyl"
echo "This script is supposted to run on the wings host system, please aboard if this is not the case. (^C)"

apt update
apt install cifs-utils -y

echo "Please enter the following details for the SMB mount configuration:"
read -p "Enter the path to the local mount location: 
" loc
read -p "Enter the username for the SMB-Share: 
" name
read -p "Enter the password for the SMB-Share: 
" pass
read -p "Enter the domain/hostname of the SMB-Share: 
" host
read -p "Enter the remote path of the SMB share (must start with \"/\"): 
(It is recommended to choose a path that is not too deep in the directory structure, but rather a slightly higher-level folder. This makes it easier to navigate into subfolders later through the Pterodactyl web interface.) 
" remote

echo "Please enter the following details for the temporary folder configuration used during transcoding:"
read -p "Enter the path to local temp folder: " temp

sudo echo $name > ~/smbcredentials
sudo echo $pass >> ~/smbcredentials

mkdir -p $loc
mkdir -p $temp

chmod -R +777 $loc
chmod -R +777 $temp 

echo "# SMB-Mount für Pterodactyl" >> /etc/fstab
echo "//${host}${remote}  $loc  cifs  credentials=/home/${whoami}/smbcredentials,uid=999,gid=1001,file_mode=0770,dir_mode=0775,iocharset=utf8,rw,vers=3.0,nofail,x-systemd.automount  0 0" >> /etc/fstab

sudo systemctl daemon-reload
mount -a

echo "Make sure that both ${loc} and ${temp} are writable by Pterodactyl (aka. Wings Agent)! And that both folders are listed in the wings config as allowed_mounts."
echo "To learn more about allowed_mounts, please visit: https://pterodactyl.io/guides/mounts.html"