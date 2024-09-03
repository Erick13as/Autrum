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

class AudioComparator:
    def __init__(self, root):
        self.root = root
        self.root.title("Comparador de Audio")

        # Botón para cargar archivo ATM
        self.load_button = tk.Button(root, text="Cargar Archivo ATM", command=self.load_atm)
        self.load_button.pack()

        # Botón para grabar palabra
        self.record_button = tk.Button(root, text="Grabar Palabra", command=self.record_audio)
        self.record_button.pack()
        
        # Botón para comparar audio
        self.compare_button = tk.Button(root, text="Comparar Audio", command=self.compare_audio)
        self.compare_button.pack()

        # Botón para reproducir audio
        self.play_button = tk.Button(root, text="Reproducir Audio", command=self.play_audio)
        self.play_button.pack()

        # Label para mostrar estado de grabación
        self.status_label = tk.Label(root, text="Estado: Listo")
        self.status_label.pack()

        self.file_path = None
        self.recorded_audio_path = "recorded.wav"
        self.audio_data = None
        self.audio_offset = None

    def load_atm(self):
        self.file_path = filedialog.askopenfilename(filetypes=[("ATM Files", "*.atm")])
        if self.file_path:
            try:
                # Cargar y procesar archivo ATM
                self.audio_data = self.load_and_process_atm(self.file_path)
                messagebox.showinfo("Éxito", "Archivo ATM cargado exitosamente.")
                # Descomentar si quieres graficar el audio
                # self.plot_audio(self.audio_data, title="Audio ATM")
            except Exception as e:
                messagebox.showerror("Error", f"Error al cargar el archivo ATM: {str(e)}")

    def load_and_process_atm(self, file_path):
        try:
            with open(file_path, 'rb') as f:
                raw_data = f.read()
            
            audio_data = np.frombuffer(raw_data, dtype=np.int16)
            
            # Verifica que audio_data no esté vacío
            if len(audio_data) == 0:
                raise ValueError("Los datos de audio están vacíos.")
            
            temp_wav_path = "temp_audio.wav"
            sample_rate = 44100
            
            # Normalizar el audio_data para evitar problemas
            audio_data = np.int16(audio_data / np.max(np.abs(audio_data)) * 32767)
            
            # Asegúrate de que audio_data sea un array 1D si se requiere
            if len(audio_data.shape) > 1:
                audio_data = audio_data[:, 0]
            
            sf.write(temp_wav_path, audio_data, sample_rate)
            
            return temp_wav_path
        except Exception as e:
            raise ValueError(f"Error al procesar el archivo ATM: {str(e)}")

    def record_audio(self):
        self.status_label.config(text="Estado: Grabando...")
        self.root.update()
        
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 44100
        CHUNK = 1024
        RECORD_SECONDS = 5
        
        audio = pyaudio.PyAudio()
        stream = audio.open(format=FORMAT, channels=CHANNELS,
                            rate=RATE, input=True,
                            frames_per_buffer=CHUNK)
        frames = []

        for _ in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
            data = stream.read(CHUNK)
            frames.append(data)

        stream.stop_stream()
        stream.close()
        audio.terminate()

        wf = wave.open(self.recorded_audio_path, 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(audio.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))
        wf.close()
        
        self.status_label.config(text="Estado: Listo")
        messagebox.showinfo("Éxito", "Grabación de palabra finalizada.")
        # Descomentar si quieres graficar el audio
        # self.plot_audio(self.recorded_audio_path, title="Audio Grabado")

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
            recorded_audio, _ = sf.read(self.recorded_audio_path)
            atm_audio, _ = sf.read(self.audio_data)

            if len(recorded_audio) > len(atm_audio):
                recorded_audio = recorded_audio[:len(atm_audio)]  # Ajustar longitud
            elif len(atm_audio) > len(recorded_audio):
                atm_audio = atm_audio[:len(recorded_audio)]  # Ajustar longitud

            correlation, offset = self.calculate_correlation(atm_audio, recorded_audio)

            confidence = min(max(correlation * 100, 0), 100)
            messagebox.showinfo("Resultado", f"Confianza de coincidencia: {confidence:.2f}%")

            self.audio_offset = offset
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
        if not self.file_path:
            messagebox.showerror("Error", "Debe cargar el archivo ATM primero.")
            return
        
        try:
            if self.audio_offset is not None:
                atm_audio, _ = sf.read(self.audio_data)
                start = self.audio_offset
                sd.play(atm_audio[start:])
                sd.wait()
                messagebox.showinfo("Reproducción", "Reproducción de audio completa.")
            else:
                messagebox.showerror("Error", "Primero debe comparar el audio.")
        
        except Exception as e:
            messagebox.showerror("Error", f"Error al reproducir el audio: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = AudioComparator(root)
    root.mainloop()
