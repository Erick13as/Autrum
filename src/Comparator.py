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
from PIL import Image, ImageTk  # Import PIL to resize the image
import struct
import os
import noisereduce as nr
import librosa
import librosa.display

class AudioComparator:
    def __init__(self, root):
        self.root = root
        self.root.title("Comparador de Audio")
        self.root.geometry("800x400")

        # Loading and resizing the background image
        self.original_image = Image.open("BackgroundImage.jpg")
        self.resized_image = self.original_image.resize((800, 400), Image.Resampling.LANCZOS)
        self.background_image = ImageTk.PhotoImage(self.resized_image)
        self.background_label = tk.Label(root, image=self.background_image)
        self.background_label.place(relwidth=1, relheight=1)

        # Button style
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

        # Button to load ATM file
        self.load_button = tk.Button(root, text="Cargar Archivo ATM", command=self.load_atm_file, **self.button_style)
        self.load_button.place(relx=0.5, rely=0.1, anchor=tk.CENTER)

        # Button to record word
        self.record_button = tk.Button(root, text="Grabar Palabra", command=self.toggle_recording, **self.button_style)
        self.record_button.place(relx=0.5, rely=0.3, anchor=tk.CENTER)

        # Audio compare button
        self.compare_button = tk.Button(root, text="Comparar Audio", command=self.compare_audio, **self.button_style)
        self.compare_button.place(relx=0.5, rely=0.4, anchor=tk.CENTER)

        # Audio playback button
        self.play_button = tk.Button(root, text="Reproducir Audio", command=self.play_audio, **self.button_style)
        self.play_button.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        # Label to show recording status
        self.label_style = {
            "font": ("Helvetica", 12, "bold"),
            "bg": "#204054",
            "fg": "white",
        }
        self.status_label = tk.Label(root, text="Estado: Listo", **self.label_style)
        self.status_label.place(relx=0.5, rely=0.8, anchor=tk.CENTER)

        # Variable initialization
        self.is_original_audio_loaded = False
        self.is_audio_to_compare_recorded = False
        self.rate = 44100
        self.audio_to_compare_path = "temp.wav"
        self.original_audio = None
        self.audio_offset = 0
        self.is_recording = False  # Variable to control the recording status
        self.stream = None  # Variable to manage the recording flow

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

        # PyAudio configuration for recording
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
        wf = wave.open(self.audio_to_compare_path, 'wb')
        wf.setnchannels(1)
        wf.setsampwidth(self.audio.get_sample_size(pyaudio.paInt16))
        wf.setframerate(44100)
        wf.writeframes(b''.join(self.frames))
        wf.close()

        # Apply noise reduction
        self.reduce_noise(self.audio_to_compare_path)

        # Remove all reduced sound
        self.remove_silence(self.audio_to_compare_path)

        self.is_audio_to_compare_recorded = True

        messagebox.showinfo("Éxito", "Grabación finalizada.")

    def reduce_noise(self, file_path):
        # Read recorded file
        audio_data, sample_rate = sf.read(file_path)

        # Apply noise reduction
        reduced_noise = nr.reduce_noise(y=audio_data, sr=sample_rate)

        # Save processed audio without background noise
        sf.write(file_path, reduced_noise, sample_rate)
        messagebox.showinfo("Éxito", "Reducción de ruido aplicada correctamente.")
        
    def remove_silence(self, file_path):
        # Load audio without background noise
        audio_data, sample_rate = librosa.load(file_path, sr=None)

        # Detect intervals in which there is relevant speech or sound
        non_silent_intervals = librosa.effects.split(audio_data, top_db=40)  # Umbral de dB ajustable

        # Combine only the non-silent parts
        non_silent_audio = np.concatenate([audio_data[start:end] for start, end in non_silent_intervals])

        # Save audio without silence
        sf.write(file_path, non_silent_audio, sample_rate)

        messagebox.showinfo("Éxito", "Silencios eliminados correctamente.")

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
        if not self.is_original_audio_loaded:
            messagebox.showerror("Error", "Debe cargar el archivo ATM.")
            return
        if not self.is_audio_to_compare_recorded:
            messagebox.showerror("Error", "Debe grabar una palabra o frase para comparar.")
            return
        
        try:
            audio_to_compare, _ = sf.read(self.audio_to_compare_path) # Load audio to compare

            # Convert to mono data if necessary
            if len(audio_to_compare.shape) > 1:
                audio_to_compare = audio_to_compare[:, 0]
            if len(self.original_audio.shape) > 1:
                self.original_audio = self.original_audio[:, 0]

            # Calculate chunks
            chunk_size = len(audio_to_compare)
            overlap = chunk_size // 2
            num_chunks = (len(self.original_audio) - chunk_size) // (chunk_size - overlap) + 1

            def compute_fft(signal):
                signal_fft = fft(signal)
                signal_magnitude = np.abs(signal_fft)
                return signal_magnitude
            
            def compute_power_spectra(signal_magnitude):
                signal_power = signal_magnitude ** 2 # Get power spectra
                signal_power /= np.sum(signal_power) # Normalize power spectra
                return signal_power

            audio_to_compare_magnitude = compute_fft(audio_to_compare)
            audio_to_compare_power = compute_power_spectra(audio_to_compare_magnitude)

            def calculate_euclidean_distance(value_01, value_02):
                return np.sqrt(np.sum((value_01 - value_02) ** 2))
            
            comparisons = {}

            for i in range(num_chunks):
                start = i * (chunk_size - overlap)
                end = start + chunk_size
                chunk = self.original_audio[start:end]

                chunk_magnitude = compute_fft(chunk)
                chunk_power = compute_power_spectra(chunk_magnitude)

                fft_distance = calculate_euclidean_distance(chunk_magnitude, audio_to_compare_magnitude)
                power_distance = calculate_euclidean_distance(chunk_power, audio_to_compare_power)

                values = {
                    "start": start,
                    "fft_distance": fft_distance,
                    "power_distance": power_distance
                }

                comparisons[i] = values

            sorted_comparisons = sorted(comparisons.items(), key=lambda x: (x[1]["fft_distance"], x[1]["power_distance"]), reverse=False)

            _, values = sorted_comparisons[0] # Get first dict item

            self.audio_offset = values["start"]
            print("Offset", values["start"])
            print("FFT Distance", values["fft_distance"])
            print("Power Distance", values["power_distance"])
        except Exception as e:
            messagebox.showerror("Error", f"Error al comparar audio: {str(e)}")

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
