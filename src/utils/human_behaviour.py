import time
import random


def human_wait(min_sec=2, max_sec=5, label="⏳ Thinking..."):
    """Add a random delay to simulate human behavior"""
    delay = round(random.uniform(min_sec, max_sec), 2)
    print(f"{label} waiting {delay} seconds...")
    time.sleep(delay)


def type_like_human(element, text):
    """Type text like a human with random delays between keystrokes"""
    for char in text:
        element.send_keys(char)
        time.sleep(random.uniform(0.1, 0.3))
