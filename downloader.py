import subprocess
import asyncio
import logging
import sys
import os

SMB_HOST = os.environ.get('SMB_HOST')
SMB_LOCATION = os.environ.get('SMB_LOCATION')

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

def thumbnail_transcoding(file_title, thumbnail_file_type):
    thumbnail_file = file_title + "." + thumbnail_file_type
    thumbnail_file_out = file_title + ".jpg"

    #Converting thumbnail
    log("\nConverting thumbnail")
    command = ["ffmpeg", "-i", thumbnail_file, thumbnail_file_out]
    result = subprocess.run(command, capture_output=True, text=True)
    command = ["rm", thumbnail_file]
    result = subprocess.run(command, capture_output=False, text=True)
    log("\nThumbnail converted")

    return thumbnail_file_out

def video_transcoding(file_title, video_file_type):
    video_file = file_title + "." + video_file_type
    video_file_out = file_title + ".mp4"

    #Converting video
    log("\nConverting video")
    command = ["ffmpeg", "-i", video_file, video_file_out]
    result = subprocess.run(command, capture_output=True, text=True)
    command = ["rm", video_file]
    result = subprocess.run(command, capture_output=False, text=True)
    log("\nVideo converted")

    return video_file_out

def downloader_video(url, downloader, transcode):
    log("\nDownloading video (url: " + url + ")")
    #check file bofore
    command = ["ls"]
    result = subprocess.run(command, capture_output=True, text=True)
    files_befor = result.stdout

    #download video
    command = ["./yt-dlp", "--downloader", downloader, "--write-thumbnail", url] #NOTE - output to mount/ (in whole script)
    result = subprocess.run(command, capture_output=True, text=True)
    log(result.stdout)

    #check file after
    command = ["ls"]
    result = subprocess.run(command, capture_output=True, text=True)
    files_after = result.stdout

    #check the differance and get file / video title
    try:
        file_differance = []
        files_befor_list = files_befor.split('\n')
        files_after_list = files_after.split('\n')
        for file in files_after_list:
            if file not in files_befor_list:
                file_differance.append(file)

        video_file_type = ""
        thumbnail_file_type = ""
        video_pos = 0

        file_ending = file_differance[0].split('.')[-1]
        if file_ending == "mkv" or file_ending == "mp4" or file_ending == "webm":
            video_pos = 0
            video_file_type = file_ending
        else:
            thumbnail_file_type = file_ending
    
        file_ending = file_differance[1].split('.')[-1]
        if file_ending == "mkv" or file_ending == "mp4" or file_ending == "webm":
            video_pos = 1
            video_file_type = file_ending
        else:
            thumbnail_file_type = file_ending
    except:
            log("Download Failed")
            return 
    file_title = file_differance[video_pos][:-len(video_file_type)-1]
    video_title = file_differance[video_pos][:-len(video_file_type)-15]

    log("Video title: " + video_title)
    log("File title: " + file_title)

    if not video_file_type in ["mkv", "mp4", "webm"] or transcode and not video_file_type in ["mp4"]:
        video_file_out = video_transcoding(file_title, video_file_type)
    else:
        video_file_out = file_title + "." + video_file_type
    if not thumbnail_file_type in ["jpg"]:
        thumbnail_file_out = thumbnail_transcoding(file_title, thumbnail_file_type)
    else:
        thumbnail_file_out = file_title + "." + thumbnail_file_type

    #Rename video and thumbnail
    log("\nRenaming video and thumbnail")
    command = ["mv", video_file_out, video_title + ".mp4"]
    result = subprocess.run(command, capture_output=False, text=True)
    command = ["mv", thumbnail_file_out, video_title + ".jpg"]
    result = subprocess.run(command, capture_output=False, text=True)

    #upload video and thumbnail
    log("\nUploading video and thumbnail")
    command = ["sudo", "mount", "-t", "cifs", "-o", "credentials=credentials", f"//{SMB_HOST}{SMB_LOCATION}", "/media/"]
    result = subprocess.run(command, capture_output=False, text=True)
    command = ["sudo", "mkdir", "/media/" + video_title]
    result = subprocess.run(command, capture_output=False, text=True)
    command = ["sudo", "mv", video_title + ".jpg", "/media/" + video_title + "/folder.jpg"]
    result = subprocess.run(command, capture_output=False, text=True)
    command = ["sudo", "mv", video_title + ".mp4", "/media/" + video_title + "/" + video_title + ".mp4"]
    result = subprocess.run(command, capture_output=False, text=True)
    command = ["sudo", "umount", "-t", "cifs", "/media/"]
    result = subprocess.run(command, capture_output=False, text=True)
        
    log("\nDone")
