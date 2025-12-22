import subprocess
import logging
import sys
import os
import shutil

temp_folder = "/mount_temp/"
mount_playlist = "/mount_playlist/"
mount_videos = "/mount/"

def log(message):
    with open('logs.log', 'a') as file:
        file.write(message + '\n')
        file.close()
    print(message)

# Logger konfigurieren
logging.basicConfig(
    level=logging.ERROR,
    format='%(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),   # Für die Ausgabe im Terminal
        logging.FileHandler('logs.log')   # Für die Ausgabe in eine Datei
    ]
)

def download_using_yt_dlp(url, downloader, save_path, naming_convention):
    command = ["./yt-dlp", "--downloader", downloader, "-P", save_path, "-o", naming_convention, "--js-runtimes", "deno:/home/container/deno", "--write-thumbnail", "--convert-thumbnails", "png", url]
    result = subprocess.run(command, capture_output=True, text=True)
    if "HTTP Error 403" in result.stderr:
        log("YouTube download failed: HTTP Error 403: Forbidden")
        return [0, "YouTube download failed: HTTP Error 403: Forbidden"]
    if "Video unavailable" in result.stderr:
        log("YouTube download failed: Video unavailable")
        return [0, "YouTube download failed: Video unavailable"]
    return [1, result]
    

def downloader_video(url, downloader, transcode, playlist, staffel):
    if playlist and staffel:
        return_val = download_playlist(url, downloader, playlist, staffel)
    else:
        return_val = download_video(url, downloader)

    if return_val[0] == 0:
        return 0, return_val[1]
    
    try:
        if transcode:
            log("\nTranscoding enabled, but transcoding functionality is not implemented in this version.")
        upload_video(playlist)
    except Exception as e:
        log("\nDownload Logs (stdout): " + return_val[1].stdout)
        log("\nDownload Logs (stderr): " + return_val[1].stderr)
        log("\nError during upload: " + str(e))
        return 0, "Error during upload: " + str(e)
    return 1, None

def download_video(url, downloader):
    save_path = temp_folder
    naming_convention = "%(title)s.%(ext)s"
    log("\nDownloading video (url: " + url + ")")
    return download_using_yt_dlp(url, downloader, save_path, naming_convention)

def download_playlist(url, downloader, playlist, staffel):
    save_path = temp_folder + playlist + "/Staffel " + str(staffel)
    command = ["mkdir", "-p", save_path]
    subprocess.run(command, capture_output=False, text=True)
    naming_convention = "%(playlist_index)02d - %(title)s.%(ext)s"
    log("\nDownloading playlist (url: " + url + ")")
    log("Playlist name: " + str(playlist))
    return download_using_yt_dlp(url, downloader, save_path, naming_convention)

def upload_video(playlist):
    log("\nUploading video and thumbnail")
    if playlist:
        upload_location = mount_playlist + playlist + "/"
        local_location = temp_folder + playlist + "/"
        log("Local location: " + local_location)
        log("Upload location: " + upload_location)
        os.makedirs(upload_location, exist_ok=True)
        for item in os.listdir(local_location):
            src = os.path.join(local_location, item)
            dest = os.path.join(upload_location, item)
            shutil.move(src, dest)
            log(f"✓ Verschoben: {item}")
    else:
        filename = os.listdir(temp_folder)[0]
        name = os.path.splitext(filename)[0]
        log("Video name: " + name)
        upload_location = f"{mount_videos}{name}/"
        local_location = temp_folder
        log("Local location: " + local_location)
        log("Upload location: " + upload_location)
        os.makedirs(upload_location, exist_ok=True)
        for item in os.listdir(local_location):
            src = os.path.join(local_location, item)
            dest = os.path.join(upload_location, item)
            shutil.move(src, dest)
            log(f"✓ Verschoben: {item}")

    for item in os.listdir(temp_folder):
        item_path = os.path.join(temp_folder, item)
        if os.path.isfile(item_path):
            os.remove(item_path)
        elif os.path.isdir(item_path):
            shutil.rmtree(item_path)

    log("\nUpload Done")