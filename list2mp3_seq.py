import youtube_dl

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
    'format': 'bestaudio',
    'outtmpl': '%(title)s.%(ext)s',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '0',
    }],
    'logger': MyLogger(),
    'progress_hooks': [my_hook],
}


##main
if __name__ == "__main__":
    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,developerKey=DEVELOPER_KEY)
    print
    print("Reading file 'titles.txt'.")
    with open("titles.txt") as f:

        titles = []
        for line in f:
            line = line.strip();
            if len(line) > 0:
                titles.append(line)

        lenTitles = len(titles)
        print("Total titles: " + str(lenTitles))
        print
        for i, title in enumerate(titles):
            print("(" + str(i + 1) + "/" + str(lenTitles) + ") " + title)
            print("\tSearching video")
            try:
                videoID, videoTitle = search_video(title);

                with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                    print("\tFound video: '" + videoTitle + "' - ID: " + videoID)
                    ydl.download(['http://www.youtube.com/watch?v=' + videoID])
                    print("\tDone")
            except HttpError, e:
                print "An HTTP error %d occurred:\n%s" % (e.resp.status, e.content)

        print("All titles downloaded and converted")
