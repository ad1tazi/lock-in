import time
import tkinter as tk
from tkinter import messagebox
from PIL import Image
from utils.screenshot_poc import take_screenshot
from utils.llm_utils import describe_current_activity, convert_image_to_base64, is_user_on_task
from utils.offtask_popup_poc import show_disruptive_notification

class LockInApp:
    def __init__(self, master):
        self.master = master
        self.master.title("lock_in.dev")
        self.master.geometry("300x200")

        self.current_goal = ""
        self.interval = 20

        self.goal_label = tk.Label(master, text="Current Goal:")
        self.goal_label.pack()

        self.goal_entry = tk.Entry(master, width=40)
        self.goal_entry.pack()

        self.set_goal_button = tk.Button(master, text="Set Goal", command=self.set_goal)
        self.set_goal_button.pack()

        self.start_button = tk.Button(master, text="Start Monitoring", command=self.start_monitoring)
        self.start_button.pack()

        self.stop_button = tk.Button(master, text="Stop Monitoring", command=self.stop_monitoring, state=tk.DISABLED)
        self.stop_button.pack()

    def set_goal(self):
        self.current_goal = self.goal_entry.get()
        messagebox.showinfo("Goal Set", f"Current goal: {self.current_goal}")

    def start_monitoring(self):
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.master.after(0, self.check_user_activity)

    def stop_monitoring(self):
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.master.after_cancel(self.check_user_activity)

    def check_user_activity(self):
        with take_screenshot() as screenshot:
            base64_screenshot = convert_image_to_base64(screenshot)
            description = describe_current_activity(base64_screenshot)
        
            if not is_user_on_task(description, self.current_goal):
                show_disruptive_notification("Hey! Shithead!", "You're a little neurodivergent pigboy who likes to play in the mud. Are you done fucking around? Are you ready to get back to work now?", "Sorry, I'll focus now")

            del base64_screenshot

        self.master.after(self.interval * 1000, self.check_user_activity)

def main():
    root = tk.Tk()
    app = LockInApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()