import yt_dlp
from tkinter import *
from tkinter import messagebox as MessageBox
from tkinter import ttk
import threading
from PIL import Image, ImageTk
import requests
from io import BytesIO
import os



downloading = False
paused = False
cancelled = False
current_video_url = ""
download_thread = None
progress_info = {}

def update_progress_bar(d):
    global progress_info
    if d['status'] == 'downloading':
        total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate', 1)
        downloaded_bytes = d.get('downloaded_bytes', 0)
        percent_complete = (downloaded_bytes / total_bytes) * 100

        progress_info['percent_complete'] = percent_complete
        progress_info['downloaded_bytes'] = downloaded_bytes
        progress_info['total_bytes'] = total_bytes

        progress_bar['value'] = percent_complete
        progress_label.config(text=f"{percent_complete:.2f}%")
        size_label.config(
            text=f"Descargado: {downloaded_bytes / (1024 * 1024):.2f}MB de {total_bytes / (1024 * 1024):.2f}MB"
        )
        root.update_idletasks()

def download_video():
    global downloading, cancelled, current_video_url, progress_info
    enlace = videos.get()
    current_video_url = enlace
    downloading = True
    cancelled = False

    try:
        with yt_dlp.YoutubeDL() as ydl:
            info_dict = ydl.extract_info(enlace, download=False)
        
        title = info_dict.get('title', 'N/A')
        duration = info_dict.get('duration', 0)
        thumbnail_url = info_dict.get('thumbnail', '')

        title_label.config(text=f"Título: {title}")
        duration_label.config(text=f"Duración: {duration // 60}:{duration % 60:02} minutos")

        if thumbnail_url:
            response = requests.get(thumbnail_url)
            img_data = response.content
            img = Image.open(BytesIO(img_data))
            img = img.resize((160, 90), Image.LANCZOS) 
            img_tk = ImageTk.PhotoImage(img)
            thumbnail_label.config(image=img_tk)
            thumbnail_label.image = img_tk

        ydl_opts = {
            'format': 'bestvideo+bestaudio/best',
            'outtmpl': '%(title)s.%(ext)s',
            'progress_hooks': [update_progress_bar],
            'noprogress': True,
            'quiet': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            while downloading and not cancelled:
                if paused:
                    continue
                ydl.download([enlace])

        if not cancelled:
            MessageBox.showinfo("Éxito", "Descarga completada con éxito.")
        else:
            MessageBox.showinfo("Cancelado", "Descarga cancelada.")
    except Exception as e:
        if not cancelled:
            MessageBox.showerror("Error", f"Error al descargar el video: {e}")
    finally:
        downloading = False
        progress_bar['value'] = 0
        progress_label.config(text="0.00%")
        size_label.config(text="")
        download_button.config(state="normal")
        pause_button.config(state="disabled")
        cancel_button.config(state="disabled")
        resume_button.config(state="disabled")

def start_download():
    global download_thread
    download_button.config(state="normal")
    pause_button.config(state="normal")
    cancel_button.config(state="normal")
    resume_button.config(state="disabled")
    download_thread = threading.Thread(target=download_video)
    download_thread.start()

def pause_download():
    global paused
    paused = True
    pause_button.config(state="disabled")
    resume_button.config(state="normal")

def resume_download():
    global paused
    paused = False
    pause_button.config(state="normal")
    resume_button.config(state="disabled")

def cancel_download():
    global downloading, cancelled
    cancelled = True
    downloading = False
    download_thread.join()
    MessageBox.showinfo("Cancelación", "La descarga ha sido cancelada.")
    download_button.config(state="normal")
    pause_button.config(state="disabled")
    resume_button.config(state="disabled")
    cancel_button.config(state="disabled")

root = Tk()
root.config(bd=45)
root.title("Descargar Videos")

videos = Entry(root, width=50)
videos.grid(row=0, column=0, columnspan=2, padx=10, pady=10)

download_button = Button(root, text="Descargar", command=start_download)
download_button.grid(row=1, column=0, padx=10, pady=10)

pause_button = Button(root, text="Pausar", command=pause_download, state="disabled")
pause_button.grid(row=1, column=1, padx=10, pady=10)

resume_button = Button(root, text="Reanudar", command=resume_download, state="disabled")
resume_button.grid(row=2, column=0, padx=10, pady=10)

cancel_button = Button(root, text="Cancelar", command=cancel_download, state="disabled")
cancel_button.grid(row=2, column=1, padx=10, pady=10)


progress_bar = ttk.Progressbar(root, orient='horizontal', length=300, mode='determinate')
progress_bar.grid(row=3, column=0, columnspan=2, pady=10)


progress_label = Label(root, text="0.00%")
progress_label.grid(row=4, column=0, columnspan=2)

size_label = Label(root, text="")
size_label.grid(row=5, column=0, columnspan=2)

title_label = Label(root, text="Título: ")
title_label.grid(row=6, column=0, columnspan=2)

duration_label = Label(root, text="Duración: ")
duration_label.grid(row=7, column=0, columnspan=2)

thumbnail_label = Label(root)
thumbnail_label.grid(row=8, column=0, columnspan=2)

root.mainloop()
