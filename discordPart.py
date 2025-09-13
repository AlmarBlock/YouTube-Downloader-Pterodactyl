import discord
import re
from discord import app_commands, Webhook, Interaction
from downloader import downloader_video
import urllib.request
import json
import urllib
import asyncio
import time
import logging
import sys
import os

DISCORD_BOT_TOKEN = os.environ.get('DISCORD_BOT_TOKEN')

start_time = 0
end_time = 0
downloading = False
queue = []

# Clearing the logs.log file
with open('logs.log', 'w') as file:
    file.write('')
    file.close()

# Logger konfigurieren
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),   # Für die Ausgabe im Terminal
        logging.FileHandler('logs.log')   # Für die Ausgabe in eine Datei
    ]
)

def log(message):
    with open('logs.log', 'a') as file:
        file.write(message + '\n')
        file.close()
    print(message)

def get_usable_url(url):
    return "https://www.youtube.com/watch?v=" +  url.split("be/")[1].split("?si")[0]

def queue_to_string(queue, highlight=False):
    string = ""
    for i in range(len(queue)):
        if queue[i][1] == queue[-1][1] and not highlight:
            try:
                string = string + "\n**" + str(i+1) + ". [" + get_video_title(queue[i][1]) + "](" + queue[i][1] + ")**"
            except:
                string = string + "\n**" + str(i+1) + ". [" + queue[i][1] + "](" + queue[i][1] + ")**"
        else:
            try:
                string = string + "\n" + str(i+1) + ". [" + get_video_title(queue[i][1]) + "](" + queue[i][1] + ")"
            except:
                string = string + "\n" + str(i+1) + ". [" + queue[i][1] + "](" + queue[i][1] + ")"
    if string == "":
        return "Die Warteschlange ist leer."
    return string

def get_video_title(Video_URL):
    if "&t=" in Video_URL:
        Video_URL = Video_URL.split("&t")[0]
    if "shorts" not in Video_URL:
        VideoID = Video_URL.split("=")[-1]
    else:
        VideoID = Video_URL.split("/")[-1]
    params = {"format": "json", "url": "https://www.youtube.com/watch?v=%s" % VideoID}
    url = "https://www.youtube.com/oembed"
    query_string = urllib.parse.urlencode(params)
    url = url + "?" + query_string

    with urllib.request.urlopen(url) as response:
        response_text = response.read()
        data = json.loads(response_text.decode())
        return (data['title'])


def run():
    token = DISCORD_BOT_TOKEN

    #Sets some varibles, the are used in the hole Bot
    intents = discord.Intents.default()
    client = discord.Client(intents=intents)
    tree = app_commands.CommandTree(client)

    #Syncs the Commands the Discord
    @client.event
    async def on_ready():
        text = str(discord.version_info)
        pattern = r"major=(\d+), minor=(\d+), micro=(\d+)"
        matches = re.search(pattern, text)  
        if matches:
            major = matches.group(1)
            minor = matches.group(2)
            micro = matches.group(3)    
            version_string = "{}.{}.{}".format(major, minor, micro)
            log("Version: " + version_string)

        await client.change_presence(activity=discord.Game(name="YT-Downloader"))
        log("Activity! ✅")
        await tree.sync()
        log("Sync! ✅")
        log("Done! ✅")

    @tree.command()
    async def download_video(interaction: Interaction, url: str, downloader: str = "ffmpeg", transcode: bool = False, ping: bool = False):
        """Download a video from YouTube"""
        global downloading
        global start_time
        global queue

        # Erste Antwort sofort senden
        await interaction.response.defer(ephemeral=False)

        if downloader not in ["ffmpeg", "yt-dlp"]:
            await interaction.followup.send(content="**Bitte wähle einen gültigen Downloader aus.** \n\n `ffmpeg` oder `yt-dlp`")
            return
				
        if "youtu.be" in url:
            log("URL rewrite")
            url = get_usable_url(url)
						
        if downloading:
            queue.append((interaction.channel, url, downloader, transcode, ping, interaction.user.id))
            embed = discord.Embed(
                title="Ein Download ist bereits im Gange.",
                description=f'Der Download von: **"{get_video_title(url)} ({url})"** ist an position: **{str(len(queue))}**\n\n{queue_to_string(queue)}',
                color=0xFFCF11
            )
            await interaction.followup.send(embed=embed)
            return
        
        downloading = True
        start_time = time.time()
        
        log("Downloading video")
        try:
            video_title = get_video_title(url)
            embed = discord.Embed(
                title=video_title,
                description=f"Der Download von: {video_title} ({url}) hat begonnen.",
                color=0x00ff00
            )
        except:
            embed = discord.Embed(
                title="Download",
                description="Der Download hat begonnen. \n\n-# Der Title konnte nicht geladen werden.",
                color=0x00ff00
            )
        
        await interaction.followup.send(embed=embed)
        
        # Download im Hintergrund starten
        asyncio.create_task(handle_download(interaction.channel, url, downloader, transcode, ping, interaction.user.id))

    @tree.command()
    async def queue(interaction: Interaction):
        """See the queue"""
        global queue
        embed = discord.Embed(title="Warteschlange", description=queue_to_string(queue, True), color=0x00ff00)
        await interaction.response.send_message(embed=embed, ephemeral=False)

    @tree.command()
    async def remove(interaction: Interaction, nummer: int):
        """Entfernt ein Video aus der Warteschlange"""
        global queue
        if nummer < 1 or nummer > len(queue):
            embed = discord.Embed(title="Fehler", description="Ungültige Nummer", color=0xff0000)
            await interaction.response.send_message(embed=embed, ephemeral=False)
            return
        else:
            channel, url, downloader, transcode, ping, user_id = queue.pop(0)
            embed = discord.Embed(
                title="❌ Video entfernt ❌",
                description=f'Der Download von: **"{get_video_title(url)} ({url})"** wurde abgebrochen! \n\n{queue_to_string(queue)}',
                color=0xff0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=False)
        log("Removed video from queue")

    @tree.command()
    async def ping(interaction: Interaction):
        """Send a ping"""
        embed = discord.Embed(title="Pong", description="", color=0x00ff00)
        await interaction.response.send_message(embed=embed, ephemeral=False)


    client.run(token)


import concurrent.futures

# Ändere die handle_download Funktion, um den Download in einem separaten Thread auszuführen
async def handle_download(channel, url: str, downloader: str, transcode: bool, ping: bool, user_id: int):
    global start_time
    global end_time
    loop = asyncio.get_running_loop()
    with concurrent.futures.ThreadPoolExecutor() as pool:
        await loop.run_in_executor(pool, downloader_video, url, downloader, transcode)
    log("Done")
    end_time = time.time()
    run_time = end_time - start_time
    run_hours = int(run_time // 3600)
    run_minutes = int((run_time % 3600) // 60)
    run_seconds = int(run_time % 60)
    log("Time: " + str(run_hours) + ":" + str(run_minutes) + ":" + str(run_seconds))
    if ping:
        try:
            embed = discord.Embed(title="✅ " + get_video_title(url) + " ✅", description="In: `" + str(run_hours) + ":" + str(run_minutes) + ":" + str(run_seconds) + "`\n|| <@" + str(user_id) + "> ||", color=0x00ff00)
        except:
            embed = discord.Embed(title="✅ Done ✅", description="In: `" + str(run_hours) + ":" + str(run_minutes) + ":" + str(run_seconds) + "`\n|| <@" + str(user_id) + "> ||", color=0x00ff00)
    else:
        try:
            embed = discord.Embed(title="✅ " + get_video_title(url) + " ✅", description="In: `" + str(run_hours) + ":" + str(run_minutes) + ":" + str(run_seconds) + "`", color=0x00ff00)
        except:
            embed = discord.Embed(title="✅ Done ✅", description="In: `" + str(run_hours) + ":" + str(run_minutes) + ":" + str(run_seconds) + "`", color=0x00ff00)
    #try:
    await channel.send(embed=embed)
    #except:
        #log("Could not send message")
    if len(queue) > 0:
        channel, url, downloader, transcode, ping, user_id = queue.pop(0)
        log("Downloading video")
        try:
            embed = discord.Embed(title=get_video_title(url), description="Der Download von: " + get_video_title(url) + ' (' + url + ') hat begonnen.', color=0x00ff00)
        except:
            embed = discord.Embed(title="Download", description="Der Download hat begonnen. \n\n-# Der Title konnte nicht geladen werden.", color=0x00ff00)
        await channel.send(embed=embed)
        asyncio.create_task(handle_download(channel, url, downloader, transcode, ping, user_id))
    else:
        global downloading
        downloading = False

if __name__ == "__main__":
    run()

#if __name__ == "__main__":
#    url = "https://www.youtube.com/watch?v=Abg1moXGLFU"
#    downloader = "ffmpeg"
#    download_video(url, downloader)