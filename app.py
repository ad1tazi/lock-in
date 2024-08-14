import time
from PIL import Image
from utils.screenshot_poc import take_screenshot
from utils.llm_utils import describe_current_activity, convert_image_to_base64, is_user_on_task
from utils.offtask_popup_poc import show_disruptive_notification

current_goal = ""

def set_goal():
    global current_goal
    current_goal = input("Enter your current goal: ")

def check_user_activity():
    with take_screenshot() as screenshot:
        base64_screenshot = convert_image_to_base64(screenshot)

        description = describe_current_activity(base64_screenshot)

        print(f"Current Goal     : {current_goal}")
        print(f"Current Screenshot : {description}")
    
        if not is_user_on_task(description, current_goal):
            show_disruptive_notification("Hey! Shithead!", "You're a little neurodivergent pigboy who likes to play in the mud. Are you done fucking around? Are you ready to get back to work now?", "Sorry, I'll focus now")

        del base64_screenshot

def main():
    global current_goal
    current_goal = input("Enter your initial goal: ")
    interval = 10
    
    while True:
        time.sleep(interval)
        check_user_activity()
        
        # Allow user to modify goal
        # if input("Do you want to change your goal? (y/n): ").lower() == 'y':
        #     set_goal()

if __name__ == "__main__":
    main()