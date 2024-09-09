import tkinter as tk
import threading
import subprocess
from PIL import Image, ImageTk

class Autrum:
    def __init__(self, root):
            self.root = root
            self.root.title("Autrum - Main Window")
            self.root.geometry("800x400")

            # Upload and resize background image
            self.original_image = Image.open("BackgroundImage.jpg")
            self.resized_image = self.original_image.resize((800, 400), Image.Resampling.LANCZOS)
            self.background_image = ImageTk.PhotoImage(self.resized_image)
            self.background_label = tk.Label(root, image=self.background_image)
            self.background_label.place(relwidth=1, relheight=1)

            # Title design
            self.title_label = tk.Label(root, text="Autrum", font=("Helvetica", 32, "bold"), bg="#204054", fg="white")
            self.title_label.place(relx=0.5, rely=0.1, anchor=tk.CENTER)

            # Button style
            self.button_style = {
                "font": ("Helvetica", 12, "bold"),
                "bg": "#204054",
                "fg": "white",
                "activebackground": "#104E8B",
                "activeforeground": "#F0F0F0",
                "bd": 0,
                "highlightthickness": 0,
                "relief": "flat",
                "width": 20  # Set button width to make them uniform
            }

            # Create buttons for each mode
            self.analyzer_button = tk.Button(root, text="Analizador", command=self.open_analyzer, **self.button_style)
            self.player_button = tk.Button(root, text="Reproductor", command=self.open_player, **self.button_style)
            self.comparator_button = tk.Button(root, text="Comparador", command=self.open_comparator, **self.button_style)

            # Position the buttons
            self.analyzer_button.place(relx=0.5, rely=0.4, anchor=tk.CENTER)
            self.player_button.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
            self.comparator_button.place(relx=0.5, rely=0.6, anchor=tk.CENTER)

    def open_analyzer(self):
        threading.Thread(target=self.run_program, args=("analizador.py",)).start()

    def open_player(self):
        threading.Thread(target=self.run_program, args=("reproductor.py",)).start()

    def open_comparator(self):
        threading.Thread(target=self.run_program, args=("comparator.py",)).start()

    def run_program(self, script_name):
        subprocess.Popen(['python', script_name])

if __name__ == "__main__":
    root = tk.Tk()
    app = Autrum(root)
    root.mainloop()
