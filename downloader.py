from yt_dlp import YoutubeDL
import os
import itertools
import json

DOWNLOAD_PATH = os.path.expanduser("~/Desktop/youtube")
AUDIO_FOR_MERGING = {'mp4': 'm4a', 'webm': 'webm',}

class Downloader:
    
    new_id = itertools.count()
    
    def __init__(self, url, progress_hook, ext = 'mp4', quality = 1080, path = DOWNLOAD_PATH,):
        self.id = next(Downloader.new_id)
        self.urls = [url]
        self.ext = ext
        self.ydl_opts = {
            'paths': {'home': path},
            'outtmpl': {'default': '%(title)s.%(ext)s'},
            'logger': Logger(),
            'progress_hooks': [progress_hook],
            }
        self.formats = 0
        
        if '&list' in self.urls[0] or '?list' in self.urls[0]:
            self.ydl_opts['outtmpl'] = {'default': '%(playlist_title)s/%(title)s.%(ext)s',}
            
        if self.ext not in ['mp4', 'webm',]:
            self.ydl_opts['format'] = f'ba[ext={ext}]'
            self.ydl_opts['postprocessors'] = [{  # Extract audio using ffmpeg
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'm4a',
                    }]
        else:
            self.ydl_opts['format'] = f'bv[ext={ext}][height<={quality}]+ba[ext={AUDIO_FOR_MERGING[ext]}]/bv+ba'
    
    def download(self):
        with YoutubeDL(self.ydl_opts) as ydl:
            ydl.download(self.urls)
    
    def get_info(self):
        with YoutubeDL(self.ydl_opts) as ydl:
            info = ydl.extract_info(self.urls[0], download=False)
            self.formats = info['format_id'].split('+')   
            
class Logger:
    def debug(self, msg):
        # For compatibility with youtube-dl, both debug and info are passed into debug
        # You can distinguish them by the prefix '[debug] '
        if msg.startswith('[debug] '):
            pass
        else:
            self.info(msg)

    def info(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        print(msg)