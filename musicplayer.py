import tkinter as tk
from tkinter import filedialog, Listbox
import pygame
from tkinter import messagebox
import os

class MusicPlayer:
    def __init__(self, root):
        self.root = root
        self.root.title("Prince Music Player")
        self.root.geometry("620x400")
        self.root.configure(bg="lightblue")

        # Initialize pygame mixer
        pygame.mixer.init()

        # Current song and playing state
        self.current_song = None
        self.paused = False
        self.volume = 0.5
        pygame.mixer.music.set_volume(self.volume)

        # Playlist file to save selected songs
        self.playlist_file = "playlist.txt"
        self.song_paths = {}  # Dictionary to map displayed song names to full paths

        # Create GUI components
        self.create_widgets()

        # Load playlist if it exists
        self.load_playlist()

    def create_widgets(self):
        # App title
        title_label = tk.Label(self.root, text="My Music Player", font=("Helvetica", 16, "bold"), bg="lightblue", width=30)
        title_label.grid(row=0, column=0, columnspan=2, pady=10)

        # Left frame for controls (play, pause, stop, volume)
        control_frame = tk.Frame(self.root, bg="lightblue", width=250, height=300)
        control_frame.grid(row=1, column=0, padx=10, pady=20, sticky="n")
        control_frame.grid_propagate(False)  # Disable frame auto-sizing

        # Current song display in left column (larger)
        self.current_song_label = tk.Label(control_frame, text="No song playing", font=("Helvetica", 12), bg="lightblue", width=30)
        self.current_song_label.pack(pady=22)

        # Play and Stop buttons (side by side, square)
        button_frame = tk.Frame(control_frame, bg="lightblue")
        button_frame.pack(pady=5)

        self.play_button = tk.Button(button_frame, text="Play", width=8, height=2, command=self.play_song)
        self.play_button.pack(side=tk.LEFT, padx=5)

        self.stop_button = tk.Button(button_frame, text="Stop", width=8, height=2, command=self.stop_song)
        self.stop_button.pack(side=tk.LEFT, padx=5)

        # Pause button below Play and Stop
        self.pause_button = tk.Button(control_frame, text="Pause", width=15, command=self.pause_resume_song)
        self.pause_button.pack(pady=5)

        # Volume slider below Pause
        volume_label = tk.Label(control_frame, text="Volume", bg="lightblue", width=15)
        volume_label.pack(pady=10)
        self.volume_slider = tk.Scale(control_frame, from_=0, to=100, orient=tk.HORIZONTAL, command=self.set_volume, bg="lightblue", length=180)
        self.volume_slider.set(50)
        self.volume_slider.pack()

        # Right frame for playlist and song management
        playlist_frame = tk.Frame(self.root, bg="lightblue", width=250, height=300)
        playlist_frame.grid(row=1, column=1, padx=10, pady=20, sticky="n")
        playlist_frame.grid_propagate(False)  # Disable frame auto-sizing

        # Playlist box
        self.playlist_box = Listbox(playlist_frame, bg="white", width=35, height=10)
        self.playlist_box.pack(pady=10)

        # Add Songs and Clear Playlist buttons (side by side)
        button_frame2 = tk.Frame(playlist_frame, bg="lightblue")
        button_frame2.pack(pady=5)

        self.add_button = tk.Button(button_frame2, text="Add Songs", width=15, command=self.add_songs)
        self.add_button.pack(side=tk.LEFT, padx=5)

        self.clear_button = tk.Button(button_frame2, text="Clear Playlist", width=15, command=self.clear_playlist)
        self.clear_button.pack(side=tk.LEFT, padx=5)

    def truncate_song_name(self, song_name, length=25):
        """Truncate long song names for display."""
        return song_name if len(song_name) <= length else song_name[:length] + "..."

    def add_songs(self):
        files = filedialog.askopenfilenames(
            title="Select Songs", filetypes=(("Audio Files", "*.mp3 *.wav"), ("All Files", "*.*"))
        )
        for file in files:
            song_name = os.path.basename(file)  # Get the song name only
            truncated_name = self.truncate_song_name(song_name)
            if song_name not in self.song_paths:  # Avoid duplicate entries
                self.playlist_box.insert(tk.END, truncated_name)
                self.song_paths[truncated_name] = file  # Map truncated name to full path
                self.save_playlist()

    def play_song(self):
        try:
            selected_song_index = self.playlist_box.curselection()
            if selected_song_index:
                truncated_name = self.playlist_box.get(selected_song_index)
                song_path = self.song_paths[truncated_name]
                self.current_song = song_path
                self.current_song_label.config(text=f"Playing: {truncated_name}")
                pygame.mixer.music.load(song_path)
                pygame.mixer.music.play()
                self.paused = False
            else:
                messagebox.showinfo("Info", "Please select a song from the playlist.")
        except Exception as e:
            messagebox.showerror("Error", f"Error playing song: {str(e)}")

    def pause_resume_song(self):
        if self.current_song:
            if not self.paused:
                pygame.mixer.music.pause()
                self.paused = True
                self.pause_button.config(text="Resume")
            else:
                pygame.mixer.music.unpause()
                self.paused = False
                self.pause_button.config(text="Pause")

    def stop_song(self):
        pygame.mixer.music.stop()
        self.current_song_label.config(text="No song playing")
        self.current_song = None
        self.paused = False
        self.pause_button.config(text="Pause")

    def set_volume(self, volume):
        self.volume = int(volume) / 100
        pygame.mixer.music.set_volume(self.volume)

    def save_playlist(self):
        with open(self.playlist_file, "w") as f:
            for song_name, path in self.song_paths.items():
                f.write(f"{song_name}|{path}\n")

    def load_playlist(self):
        if os.path.exists(self.playlist_file):
            with open(self.playlist_file, "r") as f:
                lines = f.readlines()
                for line in lines:
                    parts = line.strip().split("|")
                    if len(parts) == 2:  # Ensure there are exactly two parts
                        song_name, path = parts
                        truncated_name = self.truncate_song_name(song_name)
                        self.playlist_box.insert(tk.END, truncated_name)
                        self.song_paths[truncated_name] = path  # Map truncated name to full path

    def clear_playlist(self):
        """Clear all songs from the playlist and remove saved playlist file."""
        self.playlist_box.delete(0, tk.END)  # Clear Listbox
        self.song_paths.clear()  # Clear dictionary mapping
        if os.path.exists(self.playlist_file):
            os.remove(self.playlist_file)  # Delete the playlist file
        self.current_song_label.config(text="No song playing")  # Reset current song label

# Main application
if __name__ == "__main__":
    root = tk.Tk()
    app = MusicPlayer(root)
    root.mainloop()
