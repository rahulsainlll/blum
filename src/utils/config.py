import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Instagram credentials and settings
USERNAME = os.getenv("IG_USERNAME")
PASSWORD = os.getenv("IG_PASSWORD")


# Comment settings
COMMENT_TEXT =  "Amazing work as always! "
COMMENT_VARIATIONS = [
    "Your talent is truly inspiring! ",
    "Another masterpiece!",
    "You're a legend! ",
    "Incredible performance!",
    "Your work continues to amaze!",
    "A true artist!",
    "Your dedication shows in every role! ",
    "Always a pleasure to see your work! ",
    "You're an inspiration to many! ",
    "Keep shining bright! ",
]

# Chrome options
CHROME_OPTIONS = {
    "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "arguments": [
        "--no-sandbox",
        "--disable-dev-shm-usage",
        "--start-maximized",
        "--disable-gpu",
        "--disable-extensions",
        "--disable-infobars",
        "--disable-notifications",
        "--disable-popup-blocking",
        "--disable-blink-features=AutomationControlled",
    ],
}
