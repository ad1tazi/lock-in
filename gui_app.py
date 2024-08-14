import time
import csv
import tkinter as tk
from tkinter import messagebox
from PIL import Image
from utils import take_screenshot, describe_current_activity, convert_image_to_base64, is_user_on_task, show_disruptive_notification
from tkinter import ttk
from tkinter import font as tkfont
import asyncio
import threading
from concurrent.futures import ThreadPoolExecutor

DISRUPTIVE_NOTIF_TITLE = "Hey! Shithead!"
DISRUPTIVE_NOTIF_BODY = "You're a little neurodivergent pigboy who likes to play in the mud. Are you done fucking around? Are you ready to get back to work now?"
DISRUPTIVE_NOTIF_BUTTON = "Sorry, I'll focus now"

class LockInApp:
    def __init__(self, master):
        self.master = master
        self.master.title("lock_in.dev")
        self.master.geometry("400x300")
        self.master.configure(bg='#2A3B47')

        self.current_task = ""
        self.interval = 20

        # Custom font and colors
        self.font = ('Courier', 12, 'bold')
        self.fg_color = '#ffffff'  # White text
        self.bg_color = '#2A3B47'  # Dark blue-gray background
        self.button_fg = '#000000' # Black text for buttons
        self.button_bg = '#ffffff' # White background for buttons
        self.entry_bg = '#333333'  # Dark gray for entry widget

        # Create a custom font
        self.title_font = tkfont.Font(family="K2D", size=72, slant="italic", weight="bold")

        self.task_label = tk.Label(master, text="lock in", font=self.title_font, fg='#ffffff', bg=self.bg_color)
        self.task_label.pack(pady=20)

        # Replace the task_entry and set_task_button with a frame containing both
        self.input_frame = tk.Frame(master, bg=self.bg_color)
        self.input_frame.pack(pady=5)

        self.task_entry = tk.Entry(self.input_frame, width=30, font=self.font, fg=self.fg_color, bg=self.entry_bg, insertbackground=self.fg_color)
        self.task_entry.pack(side=tk.LEFT, padx=(0, 0))
        self.task_entry.bind('<Return>', self.toggle_monitoring)  # Add this line

        self.toggle_button = ttk.Button(self.input_frame, text="➤", width=3, command=self.toggle_monitoring)
        self.toggle_button.pack(side=tk.LEFT)

        self.monitoring = False  # Add this flag to track monitoring state

        self.loop = asyncio.new_event_loop()
        self.thread = threading.Thread(target=self.start_loop, daemon=True)
        self.thread.start()
        self.executor = ThreadPoolExecutor(max_workers=1)

    def start_loop(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

    def toggle_monitoring(self, event=None):  # Add 'event=None' parameter
        if not self.monitoring:
            self.start_monitoring()
        else:
            self.stop_monitoring()

    def start_monitoring(self):
        self.current_task = self.task_entry.get()
        if self.current_task:
            self.toggle_button.config(text="◼")  # Change button to stop symbol
            self.task_entry.config(state=tk.DISABLED)
            self.monitoring = True
            self.master.after(0, self.check_user_activity)
        else:
            messagebox.showwarning("No Task", "Please enter a task before starting.", icon='warning')

    def stop_monitoring(self):
        self.toggle_button.config(text="➤")  # Change button back to play symbol
        self.task_entry.config(state=tk.NORMAL)
        self.monitoring = False

    def check_user_activity(self):
        if not self.monitoring:
            return

        def callback(future):
            user_is_on_task = future.result()
            self.handle_activity_result(user_is_on_task)
            self.master.after(self.interval * 1000, self.check_user_activity)

        future = asyncio.run_coroutine_threadsafe(self.async_check_user_activity(), self.loop)
        future.add_done_callback(callback)

    async def async_check_user_activity(self):
        with take_screenshot() as screenshot:
            base64_screenshot = convert_image_to_base64(screenshot)

            description = await describe_current_activity(base64_screenshot)
            user_is_on_task = await is_user_on_task(description, self.current_task)

            del base64_screenshot
            return user_is_on_task

    def handle_activity_result(self, user_is_on_task):
        if not user_is_on_task:
            with open('.logs/activity_log.csv', 'r') as csv_file:
                csv_reader = list(csv.reader(csv_file))
                if len(csv_reader) >= 2:
                    last_two_rows = csv_reader[-2:]
                    if all(row[1].lower() == 'false' for row in last_two_rows):
                        show_disruptive_notification(DISRUPTIVE_NOTIF_TITLE, DISRUPTIVE_NOTIF_BODY, DISRUPTIVE_NOTIF_BUTTON)
                else:
                    show_disruptive_notification(DISRUPTIVE_NOTIF_TITLE, DISRUPTIVE_NOTIF_BODY, DISRUPTIVE_NOTIF_BUTTON)

        with open('.logs/activity_log.csv', 'a', newline='') as csv_file:
            csv_writer = csv.writer(csv_file)
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            csv_writer.writerow([timestamp, user_is_on_task, self.current_task])

def main():
    root = tk.Tk()
    root.configure(bg='#2A3B47')  # Set the root window background to dark blue-gray
    app = LockInApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()