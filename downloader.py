import subprocess
import logging
import sys
import os
import shutil
from dotenv import load_dotenv

load_dotenv()

temp_folder = "./mount_temp/"
mount_playlist = "./mount_playlist/"
mount_videos = "./mount/"

def log(message, level="INFO"):
    if level in ["INFO", "WARNING", "ERROR"]:
        with open('logs.log', 'a') as file:
            file.write(message + '\n')
            file.close()
    if level in ["ERROR", "INFO", "WARNING"]:
        print(message)
    if level == "DEBUG" and os.environ.get('DEBUG_MODE') == 'True':
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
        log("YouTube download failed: HTTP Error 403: Forbidden", "ERROR")
        return [0, "YouTube download failed: HTTP Error 403: Forbidden"]
    if "Video unavailable" in result.stderr:
        log("YouTube download failed: Video unavailable", "ERROR")
        return [0, "YouTube download failed: Video unavailable"]
    return [1, result]
    

def downloader_entry_point(url, downloader, transcode, playlist, staffel, scale_width):
    global temp_folder

    if playlist and staffel:
        return_val = download_playlist(url, downloader, playlist, staffel)
    else:
        return_val = download_video(url, downloader)

    log("------------------------------------", "DEBUG")
    log(str(return_val[0][0]), "DEBUG")
    log("------------------------------------", "DEBUG")
    log(str(return_val[0][1]), "DEBUG")
    log("------------------------------------", "DEBUG")
    log(str(return_val[1]), "DEBUG")
    log("------------------------------------", "DEBUG")

    if return_val[0][0] == 0: #Check standart-out
        return 0, return_val[0][1] #Report Progress from YT-DLP 

    #Transcode to resolution
    for item in os.listdir(temp_folder):
        src = os.path.join(temp_folder, item)
        if os.path.isfile(src) and item.endswith((".mp4", ".mkv", ".webm")):
            transcode_video(src, scale_width)
    
    try:
        if transcode:
            log("\nTranscoding enabled, but transcoding functionality is not implemented in this version.", "WARNING")
        upload_video(playlist)
    except Exception as e:
        log("\nDownload Logs (stdout): " + return_val[1].stdout, "ERROR")
        log("\nDownload Logs (stderr): " + return_val[1].stderr, "ERROR")
        log("\nError during upload: " + str(e), "ERROR")
        return 0, "Error during upload: " + str(e)
    return 1, None

def download_video(url, downloader):
    save_path = temp_folder
    naming_convention = "%(title)s.%(ext)s"
    log("\nDownloading video (url: " + url + ")", "INFO")
    return download_using_yt_dlp(url, downloader, save_path, naming_convention), save_path

def download_playlist(url, downloader, playlist, staffel):
    save_path = temp_folder + playlist + "/Staffel " + str(staffel)
    command = ["mkdir", "-p", save_path]
    subprocess.run(command, capture_output=False, text=True)
    naming_convention = "%(playlist_index)02d - %(title)s.%(ext)s"
    log("\nDownloading playlist (url: " + url + ")", "INFO")
    log("Playlist name: " + str(playlist), "INFO")
    return download_using_yt_dlp(url, downloader, save_path, naming_convention), save_path

def transcode_video(input_file, scale_width=1080):
    log("\nTranscoding video (input file: " + input_file + ")", "INFO")
    output_file = os.path.splitext(input_file)[0] + "_" + str(scale_width) + ".mp4"
    command = ["ffmpeg", "-i", input_file, "-filter:v", f"scale={scale_width}:-1", "-c:a", "copy", output_file]
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        log("Transcoding failed: " + result.stderr, "ERROR")
    else:
        log("Transcoding successful: " + output_file, "INFO")
        os.remove(input_file)  # Remove the original file after transcoding

def upload_video(playlistName):
    log("\nUploading video and thumbnail")
    if playlistName:
        upload_location = mount_playlist + playlistName + "/"
        local_location = temp_folder + playlistName + "/"
        log("Local location: " + local_location, "INFO")
        log("Upload location: " + upload_location, "INFO")
        os.makedirs(upload_location, exist_ok=True)
        for item in os.listdir(local_location):
            src = os.path.join(local_location, item)
            dest = os.path.join(upload_location, item)
            shutil.move(src, dest)
            log(f"✓ Verschoben: {item}")
    else:
        filename = os.listdir(temp_folder)[0]
        name = os.path.splitext(filename)[0]
        log("Video name: " + name, "INFO")
        upload_location = f"{mount_videos}{name}/"
        local_location = temp_folder
        log("Local location: " + local_location, "INFO")
        log("Upload location: " + upload_location, "INFO")
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

    log("\nUpload Done", "INFO")