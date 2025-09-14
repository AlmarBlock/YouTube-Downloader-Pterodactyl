echo "Setup Script for YouTube Downloader on Pterodactyl"
echo "This script is supposted to run on the wings host system, please aboard if this is not the case. (^C)"

apt update
apt install cifs-utils -y

echo "Please enter the following details for the SMB mount configuration:"
read -p "Enter the path to the local mount location: " loc
read -p "Enter the username for the SMB-Share: " name
read -p "Enter the password for the SMB-Share: " pass
read -p "Enter the domain/hostname of the SMB-Share: " host
read -p "Enter the remote path of the SMB-Share (must start with \"/\"): " remote

echo "Please enter the following details for the temporary folder configuration used during transcoding:"
read -p "Enter the path to local temp folder: " temp

sudo echo $name > ~/credentials
sudo echo $pass >> ~/credentials

mkdir -p $loc
mkdir -p $temp

chmod -R +777 $loc
chmod -R +777 $temp 

echo "# SMB-Mount für Pterodactyl" >> /etc/fstab
echo "//${host}${remote} $loc cifs credentials=${PWD}credentials,iocharset=utf8,file_mode=0777,dir_mode=0777,noperm,x-systemd.automount,_netdev,nofail 0 0" >> /etc/fstab

sudo systemctl daemon-reload
mount -a

echo "Make sure that both ${loc} and ${temp} are writable by Pterodactyl (aka. Wings Agemt)! And that both folders are listed in the wings config as allowed_mounts."
echo "To learn more about allowed_mounts, please visit: https://pterodactyl.io/guides/mounts.html"