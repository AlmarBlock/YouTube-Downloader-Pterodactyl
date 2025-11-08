# YouTube-Downloader - Pterodactyl
A small YouTube Downloader that runs on Pterodactyl and uploads the content to an SMB share.

## Prerequisites 
- Working Pterodactyl and Wings server
- SMB server with valid credentials
- Discord bot with working token
- Knowledge on how to add a Discord bot to a server and the usage of Application Commands

## Installation
1. Download the [egg-youtube-downloader.json](https://raw.githubusercontent.com/AlmarBlock/YouTube-Downloader-Pterodactyl/refs/heads/main/egg-youtube-downloader.json)

2. Add the egg to your Pterodactyl installation.

3. Run the following command on your Wings host machine and follow the steps:
    ```bash
    bash <(curl -s https://raw.githubusercontent.com/AlmarBlock/YouTube-Downloader-Pterodactyl/refs/heads/main/install_mount.sh)
    ```
    *Note: On some systems, you must already be logged in as root before executing the one-line command (adding sudo in front of the command does not work).*

4. Create three new mounts in the Pterodactyl web panel:

    1. 
        - The source must be set to the local mount path where you want to save the downloaded videos. It should be a subfolder of the local path you entered in step three.
        - The target must be set to `/mount`
        <hr>
    2. 
        - The source must be set to the path of the temp folder that you entered in the third step.
        - The target must be set to `/mount_temp`
        <hr>
    3. 
        - The source must be set to the local mount path where you want to save the downloaded playlists or shows. It should be a subfolder of the local path you entered in step three.
        - The target must be set to `/mount_playlist`

    *Note: Make sure that both Nodes and Eggs are set to the correct ones (Egg must be set to "YouTube Downloader").*

5. Create a new server using the egg. Make sure to set the `Discord Bot Token` variable to your token.

6. After the installation script has finished installing the server, go back to the web panel and add all three mounts to the server.

7. Start the server.

## Cookie File
Some websites require a cookie file to make the site think that you are logged in.  
This is currently only available for `YouTube.com`.  
If necessary, follow the yt-dlp documentation to create a `cookies.txt` file: <br>
https://github.com/yt-dlp/yt-dlp/wiki/FAQ#how-do-i-pass-cookies-to-yt-dlp
    
After creating the file, place it in the top-level directory of your server.  
Make sure the file name is `cookies.txt`.


## Shoutout
This project would not be possible without the work of the [yt-dlp](https://github.com/yt-dlp/yt-dlp) project.
