import subprocess

def show_disruptive_notification(title, message, ok_button="OK"):
    script = f'''
    tell application "System Events"
        activate
        display dialog "{message}" with title "{title}" buttons {{"{ok_button}"}} default button 1 with icon caution
    end tell
    '''
    subprocess.run(["osascript", "-e", script])