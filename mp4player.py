import tkinter as tk
from PIL import Image, ImageTk
import imageio
import random
import threading
import time
from ffpyplayer.player import MediaPlayer

class BouncingPopup:
    def __init__(self, master, video_path):
        self.master = master
        self.master.overrideredirect(True)  # Remove window decorations
        self.master.attributes("-topmost", True)  # Set the window to be always on top

        # Set initial window size and position
        self.window_width = 200
        self.window_height = 150
        self.screen_width = self.master.winfo_screenwidth()
        self.screen_height = self.master.winfo_screenheight()
        self.x = random.randint(0, self.screen_width - self.window_width)
        self.y = random.randint(0, self.screen_height - self.window_height)
        self.dx = random.choice([10, 11])
        self.dy = random.choice([10, 11])
        self.master.geometry(f"{self.window_width}x{self.window_height}+{self.x}+{self.y}")

        # Create a canvas to display the video
        self.canvas = tk.Canvas(self.master, width=self.window_width, height=self.window_height, bg="black")
        self.canvas.pack()

        # Load the video
        self.video = imageio.get_reader(video_path)
        self.video_thread = threading.Thread(target=self.play_video, args=(video_path,))
        self.video_thread.daemon = True
        self.video_thread.start()

        # Start the bouncing movement
        self.move_popup()

    def move_popup(self):
        self.x += self.dx
        self.y += self.dy

        if self.x <= 0 or self.x >= self.screen_width - self.window_width:
            self.dx *= -1
        if self.y <= 0 or self.y >= self.screen_height - self.window_height:
            self.dy *= -1

        self.master.geometry(f"{self.window_width}x{self.window_height}+{self.x}+{self.y}")
        self.master.after(50, self.move_popup)

    def play_video(self, video_path):
        player = MediaPlayer(video_path)
        frame_generator = self.video.iter_data()
        delay = 1 / 30  # Assuming the video is 30 fps

        while True:
            start_time = time.time()
            val = player.get_frame()
            if val == 'eof':
                break
            if val is None:
                continue
            audio_frame, audio_t = val
            if audio_frame is None:
                continue

            try:
                video_frame = next(frame_generator)
                image = Image.fromarray(video_frame)
                image = image.resize((self.window_width, self.window_height), Image.LANCZOS)
                photo = ImageTk.PhotoImage(image)
                self.canvas.create_image(0, 0, anchor=tk.NW, image=photo)
                self.canvas.image = photo
            except StopIteration:
                break

            time_spent = time.time() - start_time
            time.sleep(max(0, delay - time_spent))

def popup(video_path):
    root = tk.Tk()
    BouncingPopup(root, video_path)
    root.mainloop()
