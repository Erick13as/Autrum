import tkinter as tk
from tkinter import messagebox
import pyaudio
import wave
import threading
import os
from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt
from scipy.fft import fft
import struct

class AudioAnalyzerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Autrum - Analizador de Audio")
        self.root.geometry("800x400")

        self.is_recording = False
        self.frames = []
        self.stream = None
        self.last_file_path = None

        # Configuración del micrófono
        self.audio = pyaudio.PyAudio()
        self.format = pyaudio.paInt16
        self.channels = 1
        self.rate = 44100
        self.chunk = 1024

        # Elementos de la interfaz gráfica
        self.start_button = tk.Button(root, text="Iniciar Grabación", command=self.start_recording)
        self.stop_button = tk.Button(root, text="Parar Grabación", command=self.stop_recording, state=tk.DISABLED)
        self.continue_button = tk.Button(root, text="Continuar Grabación", command=self.continue_recording, state=tk.DISABLED)
        self.save_button = tk.Button(root, text="Guardar Grabación", command=self.save_recording, state=tk.DISABLED)
        self.plot_button = tk.Button(root, text="Graficar Señal", command=self.plot_last_recording, state=tk.DISABLED)

        self.start_button.pack(pady=10)
        self.stop_button.pack(pady=10)
        self.continue_button.pack(pady=10)
        self.save_button.pack(pady=10)
        self.plot_button.pack(pady=10)

        # Inicializar la figura de Matplotlib
        self.fig, (self.ax1, self.ax2) = plt.subplots(1, 2, figsize=(10, 4))
        self.line1, = self.ax1.plot([], [])
        self.line2, = self.ax2.plot([], [])
        self.ax1.set_title("Señal en el dominio del tiempo")
        self.ax1.set_xlabel("Muestras")
        self.ax1.set_ylabel("Amplitud")
        self.ax2.set_title("Transformada de Fourier")
        self.ax2.set_xlabel("Frecuencia (Hz)")
        self.ax2.set_ylabel("Amplitud")

        self.ax1.set_xlim(0, self.chunk)
        self.ax1.set_ylim(-32768, 32767)
        self.ax2.set_xlim(0, self.rate / 2)
        self.ax2.set_ylim(0, 1)

        self.fig.tight_layout()
        plt.ion()
        plt.show()

        # Configurar la actualización periódica
        self.update_interval = 50  # en milisegundos
        self.update_graph_periodically()

    def start_recording(self):
        self.is_recording = True
        self.frames = []
        self.stream = self.audio.open(format=self.format, channels=self.channels, rate=self.rate, input=True, frames_per_buffer=self.chunk)
        self.update_buttons(recording=True)
        threading.Thread(target=self.record_audio).start()

    def stop_recording(self):
        self.is_recording = False
        self.update_buttons(recording=False)
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()

    def continue_recording(self):
        self.is_recording = True
        self.stream = self.audio.open(format=self.format, channels=self.channels, rate=self.rate, input=True, frames_per_buffer=self.chunk)
        self.update_buttons(recording=True)
        threading.Thread(target=self.record_audio).start()

    def record_audio(self):
        while self.is_recording:
            data = self.stream.read(self.chunk)
            self.frames.append(data)
            # Almacenar los datos para la próxima actualización de la gráfica
            self.latest_data = data

    def update_graph_periodically(self):
        if hasattr(self, 'latest_data'):
            self.update_graph(self.latest_data)
        self.root.after(self.update_interval, self.update_graph_periodically)

    def update_graph(self, data):
        signal = np.frombuffer(data, dtype=np.int16)
        self.line1.set_data(np.arange(len(signal)), signal)

        N = len(signal)
        T = 1.0 / self.rate
        yf = fft(signal)
        xf = np.fft.fftfreq(N, T)[:N//2]
        self.line2.set_data(xf, 2.0/N * np.abs(yf[0:N//2]))

        self.ax1.set_xlim(0, len(signal))
        self.ax1.set_ylim(signal.min(), signal.max())
        self.ax2.set_ylim(0, max(2.0/N * np.abs(yf[0:N//2])))

        self.fig.canvas.draw_idle()

    def save_recording(self):
        if self.frames:
            if not os.path.exists('audio'):
                os.makedirs('audio')
            
            current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            wav_file_path = os.path.join('audio', f"{current_time}.wav")
            atm_file_path = os.path.join('audio', f"{current_time}.atm")
            
            # Guardar archivo WAV
            with wave.open(wav_file_path, 'wb') as wf:
                wf.setnchannels(self.channels)
                wf.setsampwidth(self.audio.get_sample_size(self.format))
                wf.setframerate(self.rate)
                wf.writeframes(b''.join(self.frames))
                
            # Generar FFT de toda la señal grabada
            signal = np.frombuffer(b''.join(self.frames), dtype=np.int16)
            yf = fft(signal)
            xf = np.fft.fftfreq(len(signal), 1.0/self.rate)[:len(signal)//2]
            
            # Guardar archivo ATM
            with open(atm_file_path, 'wb') as af:
                # Guardar el audio original
                af.write(struct.pack('I', len(signal)))
                af.write(signal.tobytes())
                
                # Guardar los datos de la FFT
                af.write(struct.pack('I', len(xf)))
                af.write(xf.tobytes())
                af.write(yf[:len(signal)//2].tobytes())
            
            self.last_file_path = wav_file_path
            self.plot_button.config(state=tk.NORMAL)
            messagebox.showinfo("Guardado", f"Grabación guardada como {wav_file_path} y {atm_file_path}")

    def plot_last_recording(self):
        if self.last_file_path and os.path.exists(self.last_file_path):
            plt.close(self.fig)  # Cerrar la ventana de las gráficas en tiempo real
            signal, rate = self.load_wave_file(self.last_file_path)

            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))
            ax1.plot(np.arange(len(signal)), signal)
            ax1.set_title("Señal en el dominio del tiempo")
            ax1.set_xlabel("Muestras")
            ax1.set_ylabel("Amplitud")

            N = len(signal)
            T = 1.0 / rate
            yf = fft(signal)
            xf = np.fft.fftfreq(N, T)[:N//2]
            ax2.plot(xf, 2.0/N * np.abs(yf[0:N//2]))
            ax2.set_title("Transformada de Fourier")
            ax2.set_xlabel("Frecuencia (Hz)")
            ax2.set_ylabel("Amplitud")

            fig.tight_layout()
            plt.show()
        else:
            messagebox.showerror("Error", "No se encontró el archivo de grabación.")

    def load_wave_file(self, file_path):
        with wave.open(file_path, 'rb') as wf:
            frames = wf.readframes(wf.getnframes())
            signal = np.frombuffer(frames, dtype=np.int16)
            rate = wf.getframerate()
            return signal, rate

    def update_buttons(self, recording):
        if recording:
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            self.continue_button.config(state=tk.DISABLED)
            self.save_button.config(state=tk.DISABLED)
        else:
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            self.continue_button.config(state=tk.NORMAL)
            self.save_button.config(state=tk.NORMAL)

    def on_closing(self):
        if self.is_recording:
            self.is_recording = False
        self.audio.terminate()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = AudioAnalyzerApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
