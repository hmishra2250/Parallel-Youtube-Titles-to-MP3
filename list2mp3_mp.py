import youtube_dl
import multiprocessing
from multiprocessing import Manager
from apiclient.discovery import build
from apiclient.errors import HttpError

import sys


# Set DEVELOPER_KEY to the API key value from the APIs & auth > Registered apps
# tab of
#   https://console.developers.google.com/project
# Please ensure that you have enabled the YouTube Data API for your project.
DEVELOPER_KEY = ""
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"
DOWNLOAD_PATH = "/home/him/Music/"
TITLES_FILE = "/home/him/Titles-Youtube-Mp3/titles.txt"
ERRORS_FILE = "/home/him/Titles-Youtube-Mp3/errors.txt"
ARCHIVE_FILE = "/home/him/Titles-Youtube-Mp3/archive.txt"
MAX_NUM_PROCESSES = 10

def search_video(title):
  search_response = youtube.search().list(
    q=title,
    part="id,snippet",
    maxResults=10
  ).execute()

  for search_result in search_response.get("items", []):
    if search_result["id"]["kind"] == "youtube#video":
        return search_result["id"]["videoId"], search_result["snippet"]["title"]


##youtube_dl configuration
class MyLogger(object):
    def debug(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        print(msg)

def my_hook(d):
    if d['status'] == 'downloading':
        sys.stdout.write('\r\033[K')
        sys.stdout.write('\tDownloading... ETA: ' + str(d["eta"]) + " seconds")
        sys.stdout.flush()
    elif d['status'] == 'finished':
        sys.stdout.write('\r\033[K')
        sys.stdout.write('\tDownload complete\n\tConverting video to mp3')
        sys.stdout.flush()

ydl_opts = {
    'writethumbnail': True,
#    'download_archive': ARCHIVE_FILE,
    'format': 'bestaudio/best',
    'outtmpl': DOWNLOAD_PATH + '%(title)s.%(ext)s',
    'postprocessors': [
        {
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '0',
        },
        {
            'key': 'FFmpegMetadata',
        },
        {
            'key': 'EmbedThumbnail',
        }
    ],
    'logger': MyLogger(),
    'progress_hooks': [my_hook],
}


def DownloadSong(title):
    videoID = -1
    try:
        print("Searching Title " + title)
        videoID, videoTitle = search_video(title)
        
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            print("\tFound video: '" + videoTitle + "' - ID: " + videoID)
            ydl.download(['http://www.youtube.com/watch?v=' + videoID])
        return (title, True, videoID)
    except Exception as e:
        print "Some error for videoID %s and title %s stating %s occurred:\n%s" % (videoID, title, e.message, e.args)
        return (title, False, videoID)
        

def Run():
    print("Reading file " + TITLES_FILE)
    errors = []
    with open(TITLES_FILE) as f:
        titles = []
        for line in f:
            line = line.strip();
            if len(line) > 0:
                titles.append(line)

        lenTitles = len(titles)
        print("Total titles: " + str(lenTitles))
    pool = multiprocessing.Pool(processes=MAX_NUM_PROCESSES)
    status = pool.map(DownloadSong, titles)
    errors = []
    success = []
    for ind in status:
        if not ind[1]:
            errors.append(ind[0]) 
        else:
            success.append(ind[2])
            
    with open(ERRORS_FILE, 'w') as f:
        for x in errors:
            f.write(x + '\n')
            
    with open(ARCHIVE_FILE, "a") as f:
        for x in success:
            f.write('\n' + 'youtube ' + x)
    

##main
if __name__ == "__main__":
    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,developerKey=DEVELOPER_KEY)
    Run()
    
                    
  



