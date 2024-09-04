import tkinter as tk
from tkinter import messagebox, filedialog
import sounddevice as sd
import time
from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt
from scipy.fft import fft
import struct
from PIL import Image, ImageTk  # Importar PIL para redimensionar la imagen

class AudioPlayer:
    def __init__(self, root):
        self.root = root
        self.root.title("Autrum - Reproductor de Audio")
        self.root.geometry("800x400")

        self.signal = ""
        self.xf = ""
        self.yf = ""
        self.rate = 44100
        self.position = 0
        self.pause = False
        self.open_file = False
        self.cancel = False
        self.start_time = 0

        # Cargar y redimensionar la imagen de fondo
        self.original_image = Image.open("BackgroundImage.jpg")
        self.resized_image = self.original_image.resize((800, 400), Image.Resampling.LANCZOS)
        self.background_image = ImageTk.PhotoImage(self.resized_image)
        self.background_label = tk.Label(root, image=self.background_image)
        self.background_label.place(relwidth=1, relheight=1)

        # Estilo de los botones
        self.button_style = {
            "font": ("Helvetica", 12, "bold"),
            "bg": "#1E90FF",
            "fg": "white",
            "activebackground": "#104E8B",
            "activeforeground": "#F0F0F0",
            "bd": 0,
            "highlightthickness": 0,
            "relief": "flat"
        }

        # Elementos de la interfaz gráfica
        self.load_button = tk.Button(root, text="Cargar Archivo WAV", command=self.load_atm_file, **self.button_style)
        self.start_button = tk.Button(root, text="Reproducir Audio", command=self.play_audio, state=tk.DISABLED, **self.button_style)
        self.stop_button = tk.Button(root, text="Detener Reproducción", command=self.pause_audio, state=tk.DISABLED, **self.button_style)
        self.resume_button = tk.Button(root, text="Reanudar Reproducción", command=self.resume_audio, state=tk.DISABLED, **self.button_style)
        self.cancel_button = tk.Button(root, text="Cancelar Reproducción", command=self.cancel_audio, state=tk.DISABLED, **self.button_style)

        # Centrar los botones
        self.load_button.place(relx=0.5, rely=0.1, anchor=tk.CENTER)
        self.start_button.place(relx=0.5, rely=0.3, anchor=tk.CENTER)
        self.stop_button.place(relx=0.5, rely=0.4, anchor=tk.CENTER)
        self.resume_button.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        self.cancel_button.place(relx=0.5, rely=0.6, anchor=tk.CENTER)
    
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

    def play_audio(self):
        self.start_time = time.time()
        self.pause = False
        self.update_buttons(playing=True)
        plt.close('all')
        # Reproduce el audio desde la posición actual
        sd.play(self.signal[self.position:], self.rate)
        self.plot_audio()

    def pause_audio(self):
        if not self.pause:
            self.pause = True
            self.update_buttons()
            stream = sd.get_stream()
            if stream and stream.active:
                tempo = time.time()
                elapsed_time = time.time() - self.start_time 
                self.position += int(elapsed_time * self.rate)
                sd.stop()

    def resume_audio(self):
        if self.pause:
            self.start_time = time.time()
            self.pause = False
            sd.play(self.signal[self.position:], self.rate)
            self.update_buttons(playing=True)

    def cancel_audio(self):
        self.cancel = True
        plt.close('all')
        stream = sd.get_stream()
        if stream and stream.active:
            sd.stop()
        self.update_buttons()
    
    def load_atm_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("ATM files", "*.atm")])
        if file_path:
            with open(file_path, 'rb') as af:
                # Leer la longitud de la señal de audio
                signal_len = struct.unpack('I', af.read(4))[0]
                # Leer la señal de audio
                self.signal = np.frombuffer(af.read(signal_len * 2), dtype=np.int16)  # Cada muestra es un int16
                
                # Leer la longitud de los datos FFT (xf)
                fft_len = struct.unpack('I', af.read(4))[0]
                # Leer las frecuencias (xf) y las magnitudes de la FFT (yf)
                self.xf = np.frombuffer(af.read(fft_len * 8), dtype=np.float64)  # Cada frecuencia es un float64
                self.yf = np.frombuffer(af.read(fft_len * 8), dtype=np.float64)
            self.open_file = True
            self.update_buttons(open_file=True)

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