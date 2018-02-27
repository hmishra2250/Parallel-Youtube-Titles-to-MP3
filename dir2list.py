import os
import sys
reload(sys)
sys.setdefaultencoding("utf-8")
import traceback

import magic
from pymediainfo import MediaInfo

DIRECTORIES = ["~/data/Songs-C3/", "~/data/Songs-C2/", "~/data/Songs-C1/"]
OUTFILE = "./titles.txt"

def check_video_pymediainfo(path):
    fileinfo = MediaInfo.parse(path)
    
    for track in  fileinfo.tracks:
        if track.track_type == "Video":
            return True
    
    return False
    
def check_video_magic(path):
    f = magic.Magic(mime=True)
    if 'video' in f.from_file(path):
        return True
    return False


##main
if __name__ == "__main__":
    videos = []
    for directory in DIRECTORIES:
        work_dir = os.path.expanduser(directory)
        dirs = os.listdir(work_dir)
        for file_path in dirs:
            temp_path = work_dir + file_path
            if os.path.isdir(temp_path):
                continue
            try:
                if check_video_magic(temp_path):
                    temp  = file_path.split('.') 
                    song_name = "".join(temp[:-1])
                    videos.append(song_name)
            except Exception as e:
                traceback.print_exc()
                print("Error processing file " + temp_path)
    outfile = open(OUTFILE, 'w')
    for x in videos:
        outfile.write(x + '\n')
    outfile.close
              
