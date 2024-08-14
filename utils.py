import json
from PIL import Image
from io import BytesIO
import base64
from openai import OpenAI
import os
from dotenv import load_dotenv
import mss
import mss.tools
from PIL import Image
import subprocess

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

openai = OpenAI(api_key=OPENAI_API_KEY)

DESCRIBE_SCREEN_PROMPT_START = """You will be given a screenshot of a computer screen. Your task is to provide an extremely detailed description of what appears to be happening on the screen and what the user seems to be doing.

Here is the screenshot:
<screenshot>"""

DESCRIBE_SCREEN_PROMPT_END = """</screenshot>

Carefully examine the screenshot and follow these steps:

1. Overall Layout:
Describe the general layout of the screen, including the number of windows or applications visible, the presence of a taskbar or dock, and any other prominent features. Include this in <layout> tags.

2. Main Elements:
Identify and describe the main elements visible on the screen, such as open applications, web browsers, documents, or media players. Include this in <main_elements> tags.

3. Detailed Descriptions:
For each main element or area of interest, provide a detailed description of what you see. Include information such as:
- Text content (if legible)
- Images or graphics
- UI elements (buttons, menus, toolbars)
- Color schemes
- Any unusual or noteworthy features
Include each detailed description in separate <detail> tags.

4. User Activity:
Based on the visible content, infer what the user appears to be doing. Consider:
- Open applications and their content
- Active windows or tabs
- Visible cursor position or text selection
- Any work in progress or partially completed tasks
Include your inference about the user's activity in <user_activity> tags.

5. Additional Observations:
Note any other relevant details that might provide insight into the user's actions or intentions. This could include the time displayed, battery status, network connections, or any other contextual information. Include these observations in <additional_observations> tags.

Format your entire response within <screen_description> tags. Be as detailed and specific as possible in your descriptions, but do not make assumptions about information that is not visible in the screenshot. If any part of the screen is unclear or illegible, mention this in your description.

Begin your analysis now."""

ON_TASK_PROMPT_START = """You are tasked with determining whether a user is on task or not based on a description of their screen and their current goal. Your job is to analyze the information provided and make a judgment.

First, you will be given a description of the user's screen:
<screenshot_description>"""

ON_TASK_PROMPT_MIDDLE = """</screenshot_description>

Next, you will be provided with the user's current goal:
<user_goal>"""

ON_TASK_PROMPT_END = """</user_goal>

Carefully analyze the screenshot description and compare it to the user's goal. Consider whether the content visible on the screen aligns with or supports the user's stated objective.

In your justification, briefly explain your reasoning. Consider the following:
1. Does the content on the screen relate to the user's goal?
2. Are there any elements that suggest the user is working towards their objective?
3. Is there anything in the screenshot that indicates the user might be off-task?

Provide your response in JSON format as follows:
{
"justification": "<Your brief explanation here>",
"on_task": <true or false>
}

Ensure that your justification is concise but informative, and that the "on_task" value accurately reflects your conclusion based on the provided information.

Please respond in JSON format."""

def convert_image_to_base64(image: Image.Image) -> str:
    rgb_image = image.convert('RGB')
    buffered = BytesIO()
    rgb_image.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    
    return img_str

def describe_current_activity(frame: str) -> str:
    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": DESCRIBE_SCREEN_PROMPT_START
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{frame}"  # Ensure no space after 'base64,'
                        }
                    },
                    {
                        "type": "text",
                        "text": DESCRIBE_SCREEN_PROMPT_END
                    }
                ]
            }
        ]
    )
    return response.choices[0].message.content

def is_user_on_task(activity_description: str, goal: str) -> bool:
    prompt = ON_TASK_PROMPT_START + activity_description + ON_TASK_PROMPT_MIDDLE + goal + ON_TASK_PROMPT_END
    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        response_format={"type": "json_object"},
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    content_str = response.choices[0].message.content
    content_dict = json.loads(content_str)
    return content_dict["on_task"]

def take_screenshot() -> Image.Image:
    with mss.mss() as sct:
        screenshot = sct.grab(sct.monitors[0])
        pil_image = Image.frombytes("RGB", screenshot.size, screenshot.rgb)
        return pil_image

def show_disruptive_notification(title, message, ok_button="OK"):
    script = f'''
    tell application "System Events"
        activate
        display dialog "{message}" with title "{title}" buttons {{"{ok_button}"}} default button 1 with icon caution
    end tell
    '''
    subprocess.run(["osascript", "-e", script])