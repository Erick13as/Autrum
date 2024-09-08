import tkinter as tk
from tkinter import filedialog, messagebox
import numpy as np
import soundfile as sf
import pyaudio
import wave
import sounddevice as sd
import matplotlib.pyplot as plt
from scipy.fft import fft, fftfreq
from scipy.signal import correlate
from PIL import Image, ImageTk  # Importar PIL para redimensionar la imagen
import struct
import os

class AudioComparator:
    def __init__(self, root):
        self.root = root
        self.root.title("Comparador de Audio")
        self.root.geometry("800x400")

        # Cargar y redimensionar la imagen de fondo
        self.original_image = Image.open("BackgroundImage.jpg")
        self.resized_image = self.original_image.resize((800, 400), Image.Resampling.LANCZOS)
        self.background_image = ImageTk.PhotoImage(self.resized_image)
        self.background_label = tk.Label(root, image=self.background_image)
        self.background_label.place(relwidth=1, relheight=1)

        # Estilo de los botones
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

        # Botón para cargar archivo ATM
        self.load_button = tk.Button(root, text="Cargar Archivo ATM", command=self.load_atm_file, **self.button_style)
        self.load_button.place(relx=0.5, rely=0.1, anchor=tk.CENTER)

        # Botón para grabar palabra
        self.record_button = tk.Button(root, text="Grabar Palabra", command=self.toggle_recording, **self.button_style)
        self.record_button.place(relx=0.5, rely=0.3, anchor=tk.CENTER)

        # Botón para comparar audio
        self.compare_button = tk.Button(root, text="Comparar Audio", command=self.compare_audio, **self.button_style)
        self.compare_button.place(relx=0.5, rely=0.4, anchor=tk.CENTER)

        # Botón para reproducir audio
        self.play_button = tk.Button(root, text="Reproducir Audio", command=self.play_audio, **self.button_style)
        self.play_button.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        # Label para mostrar estado de grabación
        self.label_style = {
            "font": ("Helvetica", 12, "bold"),
            "bg": "#204054",
            "fg": "white",
        }
        self.status_label = tk.Label(root, text="Estado: Listo", **self.label_style)
        self.status_label.place(relx=0.5, rely=0.8, anchor=tk.CENTER)

        # Inicialización de variables
        self.is_original_audio_loaded = False
        self.is_audio_to_compare_recorded = False
        self.rate = 44100
        self.file_path = None
        self.recorded_audio_path = "recorded.wav"
        self.original_audio = None
        self.audio_offset = 0
        self.is_recording = False  # Variable para controlar el estado de grabación
        self.stream = None  # Variable para manejar el flujo de grabación

    def load_atm_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("ATM files", "*.atm")])
        self.file_name = os.path.basename(file_path)
        if file_path:
            with open(file_path, 'rb') as af:
                audio_len = struct.unpack('I', af.read(4))[0]            
                self.original_audio = np.frombuffer(af.read(audio_len * 2), dtype=np.int16)  # Cada muestra es un int16

                self.is_original_audio_loaded = True

                messagebox.showinfo("Éxito", "Archivo ATM cargado exitosamente.")
        
    def toggle_recording(self):
        if not self.is_recording:
            self.start_recording()
        else:
            self.stop_recording()

    def start_recording(self):
        self.status_label.config(text="Estado: Grabando...")
        self.record_button.config(text="Detener Grabación")
        self.is_recording = True

        # Configuración de PyAudio para grabación
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 44100
        CHUNK = 1024

        self.frames = []  # Almacena los frames de audio grabados

        self.audio = pyaudio.PyAudio()
        self.stream = self.audio.open(format=FORMAT, channels=CHANNELS,
                                      rate=RATE, input=True,
                                      frames_per_buffer=CHUNK)

        # Graba en un bucle hasta que se detenga la grabación
        self.record_audio_loop()

    def record_audio_loop(self):
        if self.is_recording:
            data = self.stream.read(1024)
            self.frames.append(data)
            self.root.after(1, self.record_audio_loop)  # Llamada recursiva para continuar grabando

    def stop_recording(self):
        self.status_label.config(text="Estado: Listo")
        self.record_button.config(text="Grabar Palabra")
        self.is_recording = False

        self.stream.stop_stream()
        self.stream.close()
        self.audio.terminate()

        # Guardar la grabación en un archivo WAV
        wf = wave.open(self.recorded_audio_path, 'wb')
        wf.setnchannels(1)
        wf.setsampwidth(self.audio.get_sample_size(pyaudio.paInt16))
        wf.setframerate(44100)
        wf.writeframes(b''.join(self.frames))
        wf.close()

        messagebox.showinfo("Éxito", "Grabación finalizada.")

    def plot_audio(self, file_path, title):
        try:
            audio, sample_rate = sf.read(file_path)
            N = len(audio)
            T = 1.0 / sample_rate
            x = np.linspace(0.0, N*T, N, endpoint=False)
            yf = fft(audio)
            xf = fftfreq(N, T)[:N//2]

            plt.figure(figsize=(12, 6))
            plt.subplot(2, 1, 1)
            plt.plot(x, audio)
            plt.title(f'{title} - Dominio del Tiempo')
            plt.xlabel('Tiempo [s]')
            plt.ylabel('Amplitud')

            plt.subplot(2, 1, 2)
            plt.plot(xf, 2.0/N * np.abs(yf[:N//2]))
            plt.title(f'{title} - Dominio de Frecuencia')
            plt.xlabel('Frecuencia [Hz]')
            plt.ylabel('Magnitud')

            plt.tight_layout()
            plt.show()
        except Exception as e:
            messagebox.showerror("Error", f"Error al graficar el audio: {str(e)}")

    def compare_audio(self):
        if not self.file_path or not self.recorded_audio_path:
            messagebox.showerror("Error", "Debe cargar el archivo ATM y grabar la palabra primero.")
            return
        
        try:
            # Load audios
            recorded_audio, _ = sf.read(self.recorded_audio_path)
            atm_audio, _ = sf.read(self.audio_data)

            # Mono data
            if len(recorded_audio.shape) > 1:
                recorded_audio = recorded_audio[:, 0]
            if len(atm_audio.shape) > 1:
                atm_audio = atm_audio[:, 0]

            chunk_size = len(recorded_audio)
            overlap = chunk_size // 2

            num_chunks = (len(atm_audio) - chunk_size) // (chunk_size - overlap) + 1

            recorded_audio_fft = fft(recorded_audio)
            recorded_audio_magnitude = np.abs(recorded_audio_fft)

            for i in range(num_chunks):
                start = i * (chunk_size - overlap)
                end = start + chunk_size
                chunk = atm_audio[start:end]

                chunk_fft = fft(chunk)
                chunk_magnitude = np.abs(chunk_fft)

                distance = np.sqrt(np.sum((chunk_magnitude - recorded_audio_magnitude) ** 2))
                print(distance)
            
            # if len(recorded_audio) > len(atm_audio):
            #     recorded_audio = recorded_audio[:len(atm_audio)]  # Ajustar longitud
            # elif len(atm_audio) > len(recorded_audio):
            #     atm_audio = atm_audio[:len(recorded_audio)]  # Ajustar longitud

            # correlation, offset = self.calculate_correlation(atm_audio, recorded_audio)

            # confidence = min(max(correlation * 100, 0), 100)
            # messagebox.showinfo("Resultado", f"Confianza de coincidencia: {confidence:.2f}%")

            self.audio_offset = 0
            # Descomentar si quieres graficar los audios después de la comparación
            # self.plot_audio(self.audio_data, title="Audio ATM")
            # self.plot_audio(self.recorded_audio_path, title="Audio Grabado")
        except Exception as e:
            messagebox.showerror("Error", f"Error al comparar audio: {str(e)}")

    def calculate_correlation(self, audio1, audio2):
        correlation = correlate(audio2, audio1, mode='valid')
        max_corr = correlation.max() if len(correlation) > 0 else 0
        offset = np.argmax(correlation) if len(correlation) > 0 else 0
        return max_corr, offset

    def play_audio(self):
        if not self.is_original_audio_loaded:
            messagebox.showerror("Error", "Debe cargar el archivo ATM primero.")
            return
        
        try:
            sd.play(self.original_audio[self.audio_offset:], self.rate)        
        except Exception as e:
            messagebox.showerror("Error", f"Error al reproducir el audio: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = AudioComparator(root)
    root.mainloop()
