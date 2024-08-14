import mss
import mss.tools
from PIL import Image

def take_screenshot() -> Image.Image:
    with mss.mss() as sct:
        screenshot = sct.grab(sct.monitors[0])
        pil_image = Image.frombytes("RGB", screenshot.size, screenshot.rgb)
        return pil_image