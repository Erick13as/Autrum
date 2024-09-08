import tkinter as tk
from tkinter import messagebox, filedialog
import sounddevice as sd
import time
from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt
from scipy.fft import fft
import struct
import os
from PIL import Image, ImageTk

class AudioPlayer:
    def __init__(self, root):
        self.root = root
        self.root.title("Autrum - Reproductor de Audio")
        self.root.geometry("800x400")

        self.signal = ""
        self.xf = ""
        self.yf = ""
        # Rate for the audio stream.
        self.rate = 44100
        self.position = 0
        self.pause = False
        self.open_file = False
        self.cancel = False
        self.start_time = 0
        self.file_name = ""

        # Upload and resize background image.
        self.original_image = Image.open("BackgroundImage.jpg")
        self.resized_image = self.original_image.resize((800, 400), Image.Resampling.LANCZOS)
        self.background_image = ImageTk.PhotoImage(self.resized_image)
        self.background_label = tk.Label(root, image=self.background_image)
        self.background_label.place(relwidth=1, relheight=1)

        # Button style.
        self.button_style = {
            "font": ("Helvetica", 12, "bold"),
            "bg": "#204054",
            "fg": "white",
            "activebackground": "#104E8B",
            "activeforeground": "#F0F0F0",
            "bd": 0,
            "highlightthickness": 0,
            "relief": "flat"
        }

        # Create the buttons for the UI.
        self.load_button = tk.Button(root, text="Cargar Archivo WAV", command=self.load_atm_file, **self.button_style)
        self.start_button = tk.Button(root, text="Reproducir Audio", command=self.play_audio, state=tk.DISABLED, **self.button_style)
        self.stop_button = tk.Button(root, text="Detener Reproducción", command=self.pause_audio, state=tk.DISABLED, **self.button_style)
        self.resume_button = tk.Button(root, text="Reanudar Reproducción", command=self.resume_audio, state=tk.DISABLED, **self.button_style)
        self.cancel_button = tk.Button(root, text="Cancelar Reproducción", command=self.cancel_audio, state=tk.DISABLED, **self.button_style)

        # Place the buttons.
        self.load_button.place(relx=0.5, rely=0.1, anchor=tk.CENTER)
        self.start_button.place(relx=0.5, rely=0.3, anchor=tk.CENTER)
        self.stop_button.place(relx=0.5, rely=0.4, anchor=tk.CENTER)
        self.resume_button.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        self.cancel_button.place(relx=0.5, rely=0.6, anchor=tk.CENTER)

        # Label style.
        self.label_style = {
            "font": ("Helvetica", 12, "bold"),
            "bg": "#204054",
            "fg": "white",
        }

        # Create and place the label.
        self.label = tk.Label(root, text="", **self.label_style)
        self.label.place(relx=0.5, rely=0.8, anchor=tk.CENTER)
    
    # Function that allows to plot the audio.
    def plot_audio(self):
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))
        ax1.plot(np.arange(len(self.signal)), self.signal)
        ax1.set_title("Señal en el dominio del tiempo")
        ax1.set_xlabel("Muestras")
        ax1.set_ylabel("Amplitud")
        ax2.plot(self.xf, self.yf)
        ax2.set_title("Transformada de Fourier")
        ax2.set_xlabel("Frecuencia (Hz)")
        ax2.set_ylabel("Amplitud")
        fig.tight_layout()
        plt.show()

    # Plays the audio stored in the "signal" variable.
    def play_audio(self):
        # Stores the start time.
        self.start_time = time.time()
        self.pause = False
        self.update_buttons(playing=True)
        plt.close('all')
        self.label.config(text="Reproduciendo Audio...")
        # Plays the audio from the current position.
        sd.play(self.signal[self.position:], self.rate)
        # Shows the graph 
        self.plot_audio()

    # Pauses the audio and stores the elapsed time.
    def pause_audio(self):
        if not self.pause:
            self.pause = True
            self.update_buttons()
            stream = sd.get_stream()
            # checks for an active stream representing the audio.
            if stream and stream.active:
                tempo = time.time()
                # Calculates the elapsed time in seconds from start to this moment.
                elapsed_time = time.time() - self.start_time 
                # Using the elapsed seconds calculates the stream position multiplying by the rate.
                self.position += int(elapsed_time * self.rate)
                # Stops the audio stream.
                sd.stop()
                self.label.config(text="Audio Pausado")

    # Resumes the audio based on the current position.
    def resume_audio(self):
        if self.pause:
            self.start_time = time.time()
            self.pause = False
            # Starts an stream from the current position.
            sd.play(self.signal[self.position:], self.rate)
            self.update_buttons(playing=True)
            self.label.config(text="Reproduciendo Audio...")

    # Cancels the audio stream and closes the graph.
    def cancel_audio(self):
        self.cancel = True
        # Closes all Tkinter windows showing the graph.
        plt.close('all')
        # Gets the current active audio stream.
        stream = sd.get_stream()
        if stream and stream.active:
            # Stops the audio stream
            sd.stop()
        # Updates the buttons. Only the start and load file buttons are active. 
        self.update_buttons(playing=False)
        self.start_button.config(state=tk.NORMAL)
        self.resume_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.DISABLED)
        self.cancel_button.config(state=tk.DISABLED)
        self.position = 0
        self.label.config(text="")
    
    # Opens an atm file and extract the audio and the information for its graph.
    def load_atm_file(self):
        # Checks for .atm files.
        file_path = filedialog.askopenfilename(filetypes=[("ATM files", "*.atm")])
        self.file_name = os.path.basename(file_path)
        if file_path:
            with open(file_path, 'rb') as af:
                # Reads the length of the audio signal.
                signal_len = struct.unpack('I', af.read(4))[0]
                # Reads the audio signal.
                self.signal = np.frombuffer(af.read(signal_len * 2), dtype=np.int16)  
                
                # Reads the length of the FFT data.
                fft_len = struct.unpack('I', af.read(4))[0]
                # Stores the frequency in xf and the magnitude in yf.
                self.xf = np.frombuffer(af.read(fft_len * 8), dtype=np.float64)  
                self.yf = np.frombuffer(af.read(fft_len * 8), dtype=np.float64)
            self.open_file = True
            self.update_buttons(open_file=True)
            # Position in 0 so it starts playing from the start.
            self.position = 0
            self.label.config(text="Se cargó el archivo " + self.file_name)

    # Updates the state of the buttons. Active or Disabled.
    def update_buttons(self, open_file=False,playing=False):
        self.load_button.config(state=tk.DISABLED if open_file else tk.NORMAL)
        self.start_button.config(state=tk.NORMAL if open_file else tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL if playing or self.pause else tk.DISABLED)
        self.resume_button.config(state=tk.NORMAL if self.pause else tk.DISABLED)
        self.cancel_button.config(state=tk.NORMAL if playing or self.pause else tk.DISABLED)
        

if __name__ == "__main__":
    root = tk.Tk()
    app = AudioPlayer(root)
    root.mainloop()