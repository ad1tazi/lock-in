import time
from PIL import Image
from utils import take_screenshot, describe_current_activity, convert_image_to_base64, is_user_on_task, show_disruptive_notification
import csv

DISRUPTIVE_NOTIF_TITLE = "Hey! Shithead!"
DISRUPTIVE_NOTIF_BODY = "You're a little neurodivergent pigboy who likes to play in the mud. Are you done fucking around? Are you ready to get back to work now?"
DISRUPTIVE_NOTIF_BUTTON = "Sorry, I'll focus now"
current_goal = ""

def change_goal():
    global current_goal
    new_goal = input("Enter your new goal (or press Enter to keep the current goal): ")
    if new_goal:
        current_goal = new_goal
        print(f"Goal updated to: {current_goal}")
    else:
        print(f"Goal unchanged: {current_goal}")

def set_goal():
    global current_goal
    current_goal = input("Enter your current goal: ")

def check_user_activity():
    with take_screenshot() as screenshot:
        base64_screenshot = convert_image_to_base64(screenshot)

        description = describe_current_activity(base64_screenshot)
    
        user_is_on_task = is_user_on_task(description, current_goal)

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
            csv_writer.writerow([timestamp, user_is_on_task, current_goal])

        del base64_screenshot

def main():
    global current_goal
    current_goal = input("Enter your initial goal: ")
    interval = 4
    
    while True:
        print("\n1. Check activity\n2. Change goal\n3. Quit")
        choice = input("Enter your choice (1/2/3): ")
        
        if choice == '1':
            check_user_activity()
        elif choice == '2':
            change_goal()
        elif choice == '3':
            print("Exiting program.")
            break
        else:
            print("Invalid choice. Please try again.")
        
        time.sleep(interval)

if __name__ == "__main__":
    main()