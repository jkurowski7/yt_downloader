from downloader import Downloader
from tkinter import * 
from tkinter import ttk
import threading
from urllib.parse import urlparse
import googleapiclient.discovery
import math

API_KEY = 'AIzaSyDWoCULbR7K0sXu0IDCEX-67RVM91x5brA'
EXTENSIONS = ['mp4','webm', 'mp3', 'm4a',]
QUALITY = {'2160p 4k': 2160, '1440p HD': 1440, '1080p HD': 1080, '720p': 720, '480p': 480, '360p': 360}

def progress_hook(d):
    if d['status'] == "downloading":
        download_progress = round(((d["downloaded_bytes"]/1024**2)/(d["total_bytes"]/1024**2)) * 100)
        if d['speed']:
            download_speed = round(d['speed']*0.000001, 2)
        else:
            download_speed = ''
        id = d['info_dict']['id']
        f = d['info_dict']['format_id']
        
        download_data = (
            d['info_dict']['title'],
            f'{download_progress}% of {round(d["total_bytes"]/1024**2, 2)} MB',
            f"{d['eta']} s",
            f"{math.floor(d['elapsed'])} s",
            f'{download_speed} MB/s',
        )
        
        table.item(id+f, values = (download_data))
        
    if d['status'] == 'finished':
        pass
    
def start_download():
    url = url_input.get()
    dl = Downloader(url, progress_hook, ext = ext_input.get(), quality = QUALITY[quality_input.get()])
    t2 = threading.Thread(target = dl.get_info)
    t2.start()
    t = threading.Thread(target = dl.download)
    t.start()
    t2.join()
    ids = videos_id()
    
    if type(ids) == list:
        for i in ids:
            for f in dl.formats:
                table.insert('', END, iid=i+f, values = ('', '', '', '', '',)) 
    else:
        for f in dl.formats:
            table.insert('', END, iid=ids+f, values = ('', '', '', '', ''))
    
def videos_id():
    url = url_input.get()
    if 'list=' in url:
        parsed = urlparse(url)
        if parsed.path == '/watch':
            playlist_id = parsed.query.split('&list=')[1].split('&index=')[0]
        elif parsed.path == '/playlist':
            playlist_id = parsed.query[5:]
        return playlist_ids(playlist_id)
    else:
        return urlparse(url).query[2:].split('&t')[0]
    
def playlist_ids(id):
    youtube = googleapiclient.discovery.build("youtube", "v3", developerKey = API_KEY)
    
    request = youtube.playlistItems().list(
        part = "snippet",
        playlistId = id,
        maxResults = 50
    )
    response = request.execute()
    playlist_items = []
    i = 0
    while request is not None:
        response = request.execute()
        playlist_items += response["items"]
        request = youtube.playlistItems().list_next(request, response)
        i += 1
        
    playlist_items_ids = [item['snippet']['resourceId']['videoId'] for item in playlist_items]
    return playlist_items_ids
    
window = Tk()
window.title("YoutubeDL")
window.geometry("1200x300")
window.config(padx = 20, pady = 20)

title_label = Label(text = 'Youtube Downloader', font=("Arial", 20, "bold"))
title_label.pack()

frame2 = ttk.Frame(window)
frame2.pack()

url_input = Entry(frame2, text = "Video URL", font=("Arial", 12), width = 71)
url_input.pack(side = LEFT)

ext_input = ttk.Combobox(frame2, values=EXTENSIONS, state = "readonly")
ext_input.set('mp4')
ext_input.pack(side = LEFT)

quality_input = ttk.Combobox(frame2, values=list(QUALITY.keys()), state = "readonly")
quality_input.set('1080p HD')
quality_input.pack(side = LEFT)

download_button = ttk.Button(frame2, text = "Download", command = start_download)
download_button.pack(side = LEFT)

frame = ttk.Frame(window)
frame.pack()

columns = ('title', 'progress', 'eta', 'elapsed', 'speed')

table = ttk.Treeview(frame, columns = columns, show = 'headings')
table.pack()

table.heading('title', text = 'Title')
table.column('title', width = 400, anchor=CENTER)

table.heading('progress', text = 'Download progress')
table.column('progress', width = 150, anchor=CENTER)

table.heading('eta', text = 'Eta')
table.column('eta', width = 150, anchor=CENTER)

table.heading('elapsed', text = 'Time elapsed')
table.column('elapsed', width = 150, anchor=CENTER)

table.heading('speed', text = 'Download speed')
table.column('speed', width = 150, anchor=CENTER)

window.mainloop()
    
