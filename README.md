# Parallel-Youtube-Titles-to-MP3

Search and download a list of videos (from their title) from Youtube in Parallel and convert them to mp3 along with their metadata information and thumbnails. Metadata information is very helpful where we want to load and classify music in our music players. Also adding parallelism speeds up the process by multiple times! The idea can be easily extended to download from youtube urls or playlists in parallel. Better create your own use case and make a pull request ;)


## What is Parallel-Youtube-Titles-to-MP3?

This is a python script that does the following:

* Reads the file 'titles.txt', which contains a list of videos to search for
    * For example it can contain the name of a few songs you want to download and convert to mp3
    * Each line of the file is a video to search for 
* Searches Youtube via the Youtube API looking for a video matching the given keywords
    * Try to use specific keywords
    * The script just does a simple search and get the url of the first video
* Download and convert the video to mp3 along with their metadata in parallel
    * To achieve this it uses the youtube-dl module/library 
    * The file will be called "{video_title}.mp3"

## How to use Parallel-Youtube-Titles-to-MP3?

1. Install Python 2 (Should work with python3, although not tested)
2. Install pip
3. Fork/Clone/Download this repository
4. Install the required packages via pip
    * pip install -r requirements.txt
5. Obtain a YouTube API key
    * Go to https://console.cloud.google.com/
    * Create a new project 
    * Your Project > Enable APIs and Services > YouTube Data API v3 > Enable
    * Inside the newly enabled API, click create credentials. Copy the generated API key.
6. Set your API key in ["list2mp3_seq.py"](list2mp3_seq.py) and ["list2mp3_mp.py"](list2mp3_mp.py)
    * Find DEVELOPER_KEY
    * Set DEVELOPER_KEY = {your_api_key}
7. Fill the file "titles.txt" (or any other file, just describe this using TITLES_FILE variable) with the videos to search and download.
    * Rememeber to use the exact video title or keywords that will get a specific video
    * One video per line
8. Set the ERRORS_FILE to write error titles to a file, ARCHIVE_FILE to maintain the archive of already downloaded list of songs (in youtube-dl compatible form) and MAX_NUM_PROCESSES to determine the maximum number of processes to download songs in parallel
9. Run the script
    * python list2mp3_seq.py for sequential running (If you have interent bandwidth issues or some other problem)
    * python list2mp3_mp.py for Parallel and time saving run
    * Enjoy your mp3s

## Additional Utilities

This repository also includes dir2list.py, which go through a list of directories (non-recursively), finds all the video files and list them to titles.txt file. I have had downloaded all songs in the form of videos and had a tough time managing the volume of data. Thus, I wrote this script to extract the title of the videos and download the mp3 songs for all those titles.

## Youtube-dl command for the same

`youtube-dl --write-thumbnail --format 'bestaudio/best' --output '%(title)s.%(ext)s' --embed-thumbnail --add-metadata --extract-audio --audio-format 'mp3' "URL"`

## Additional Information

The inspiration for this project comes from [Cristian Baldi's](https://github.com/crisbal) project [Titles-Youtube-Mp3](https://github.com/crisbal/Titles-Youtube-Mp3), which is a sequential version without metadata information. Hence there was trouble managing all songs in different media players. Hence, I wrote this script to do the same in parallel!

## Use case

This might be illegal (depending on the copyright rules of the videos) but you could use this script if you have a list of the tiles of your favourite songs (list that you generated from Pandora or Spotify for example) and you want to get the mp3s of the songs so you can listen to them on your PC or Phone.

## Need help?

If you need any help just create an Issue.

## Want to help?

If you want to improve the code and submit a pull request feel free to do so.

## Licensce

GPL v3







 