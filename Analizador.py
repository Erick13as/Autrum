import tkinter as tk
from tkinter import messagebox, filedialog
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
        self.loaded_file_path = None  
        self.is_recently_recorded = False  

        # Configuración del micrófono
        self.audio = pyaudio.PyAudio()
        self.format = pyaudio.paInt16
        self.channels = 1
        self.rate = 44100
        self.chunk = 1024
        self.recording_duration = 5  # Duración en segundos para actualizar el gráfico

        # Elementos de la interfaz gráfica
        self.start_button = tk.Button(root, text="Iniciar Grabación", command=self.start_recording)
        self.stop_button = tk.Button(root, text="Parar Grabación", command=self.stop_recording, state=tk.DISABLED)
        self.continue_button = tk.Button(root, text="Continuar Grabación", command=self.continue_recording, state=tk.DISABLED)
        self.save_button = tk.Button(root, text="Guardar Grabación", command=self.save_recording, state=tk.DISABLED)
        self.plot_button = tk.Button(root, text="Graficar Señal", command=self.plot_last_recording, state=tk.DISABLED)
        self.load_button = tk.Button(root, text="Cargar Archivo WAV", command=self.load_wav_file)

        self.start_button.pack(pady=10)
        self.stop_button.pack(pady=10)
        self.continue_button.pack(pady=10)
        self.save_button.pack(pady=10)
        self.plot_button.pack(pady=10)
        self.load_button.pack(pady=10)

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

        self.ax1.set_xlim(0, self.chunk * self.recording_duration)
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

        # Cierra todas las ventanas de gráficos existentes y abre el gráfico en tiempo real
        plt.close('all')
        self.fig, (self.ax1, self.ax2) = plt.subplots(1, 2, figsize=(10, 4))
        self.line1, = self.ax1.plot([], [])
        self.line2, = self.ax2.plot([], [])
        self.ax1.set_title("Señal en el dominio del tiempo")
        self.ax1.set_xlabel("Muestras")
        self.ax1.set_ylabel("Amplitud")
        self.ax2.set_title("Transformada de Fourier")
        self.ax2.set_xlabel("Frecuencia (Hz)")
        self.ax2.set_ylabel("Amplitud")

        self.ax1.set_xlim(0, self.chunk * self.recording_duration)
        self.ax1.set_ylim(-32768, 32767)
        self.ax2.set_xlim(0, self.rate / 2)
        self.ax2.set_ylim(0, 1)

        self.fig.tight_layout()
        plt.ion()
        plt.show()

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
            data = []
            for _ in range(0, int(self.rate / self.chunk * self.recording_duration)):
                if not self.is_recording:
                    break
                chunk_data = self.stream.read(self.chunk)
                data.append(chunk_data)
                self.frames.append(chunk_data)
            if data:
                self.latest_data = b''.join(data)
                # Usar after para actualizar el gráfico en el hilo principal con toda la señal
                self.root.after(0, self.update_graph)

    def update_graph_periodically(self):
        if hasattr(self, 'latest_data'):
            self.update_graph()
        self.root.after(self.update_interval, self.update_graph_periodically)

    def update_graph(self, data=None):
        # Usar todos los frames acumulados si data es None
        if data is None:
            data = b''.join(self.frames)
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
            yf = 2.0/len(signal) * np.abs(yf[0:len(signal)//2])  # Aseguramos que yf tenga la misma longitud que xf
            
            # Guardar archivo ATM
            with open(atm_file_path, 'wb') as af:
                # Guardar el audio original
                af.write(struct.pack('I', len(signal)))
                af.write(signal.tobytes())
                
                # Guardar los datos de la FFT
                af.write(struct.pack('I', len(xf)))
                af.write(xf.tobytes())
                af.write(yf.tobytes())
            
            self.last_file_path = wav_file_path
            self.plot_button.config(state=tk.NORMAL)
            self.update_buttons(saved=True)
            messagebox.showinfo("Guardado", f"Grabación guardada como {wav_file_path} y {atm_file_path}")

    def plot_last_recording(self):
        # Cierra cualquier ventana de gráfico existente
        plt.close('all')

        if self.last_file_path and os.path.exists(self.last_file_path):
            signal, xf, yf = self.load_signal_and_fft(self.last_file_path)

            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))
            ax1.plot(np.arange(len(signal)), signal)
            ax1.set_title("Señal en el dominio del tiempo")
            ax1.set_xlabel("Muestras")
            ax1.set_ylabel("Amplitud")

            ax2.plot(xf, yf)
            ax2.set_title("Transformada de Fourier")
            ax2.set_xlabel("Frecuencia (Hz)")
            ax2.set_ylabel("Amplitud")

            fig.tight_layout()
            plt.show()

            # Guarda el archivo ATM solo si el archivo no se grabó recientemente
            if not self.is_recently_recorded and self.loaded_file_path:
                atm_file_path = self.loaded_file_path.replace('.wav', '.atm')

                # Genera los datos de la FFT
                signal = np.frombuffer(b''.join(self.frames), dtype=np.int16)
                yf = fft(signal)
                xf = np.fft.fftfreq(len(signal), 1.0/self.rate)[:len(signal)//2]
                yf = 2.0/len(signal) * np.abs(yf[0:len(signal)//2])

                with open(atm_file_path, 'wb') as af:
                    af.write(struct.pack('I', len(signal)))
                    af.write(signal.tobytes())
                    af.write(struct.pack('I', len(xf)))
                    af.write(xf.tobytes())
                    af.write(yf.tobytes())

    def load_signal_and_fft(self, file_path):
        with wave.open(file_path, 'rb') as wf:
            signal = np.frombuffer(wf.readframes(wf.getnframes()), dtype=np.int16)
        
        N = len(signal)
        T = 1.0 / self.rate
        
        # Calculamos la FFT
        yf = fft(signal)
        
        # Aseguramos que xf y yf tengan la misma longitud
        xf = np.fft.fftfreq(N, T)[:N//2]  # Tomamos solo la mitad positiva de las frecuencias
        yf = 2.0/N * np.abs(yf[0:N//2])  # Tomamos solo la mitad positiva del espectro
        
        return signal, xf, yf

    def load_wav_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("WAV files", "*.wav")])
        if file_path:
            self.loaded_file_path = file_path
            self.is_recently_recorded = False  # Resetear bandera
            signal, xf, yf = self.load_signal_and_fft(file_path)

            plt.close('all')
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))
            ax1.plot(np.arange(len(signal)), signal)
            ax1.set_title("Señal en el dominio del tiempo")
            ax1.set_xlabel("Muestras")
            ax1.set_ylabel("Amplitud")

            ax2.plot(xf, yf)
            ax2.set_title("Transformada de Fourier")
            ax2.set_xlabel("Frecuencia (Hz)")
            ax2.set_ylabel("Amplitud")

            fig.tight_layout()
            plt.show()

            # Activar botón de graficar
            self.plot_button.config(state=tk.NORMAL)

    def update_buttons(self, recording=False, saved=False):
        self.start_button.config(state=tk.DISABLED if recording else tk.NORMAL)
        self.stop_button.config(state=tk.NORMAL if recording else tk.DISABLED)
        self.continue_button.config(state=tk.DISABLED if recording else tk.NORMAL)
        self.save_button.config(state=tk.NORMAL if not recording and self.frames else tk.DISABLED)
        self.plot_button.config(state=tk.NORMAL if not recording and saved and self.frames else tk.DISABLED)
        self.load_button.config(state=tk.DISABLED if recording else tk.NORMAL)

if __name__ == "__main__":
    root = tk.Tk()
    app = AudioAnalyzerApp(root)
    root.mainloop()
