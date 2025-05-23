import os
from datetime import datetime

# Log file paths
LOGS_DIR = "logs"
if not os.path.exists(LOGS_DIR):
    os.makedirs(LOGS_DIR)

FAILED_POSTS_LOG = os.path.join(LOGS_DIR, "failed_posts.txt")
ERROR_LOG = os.path.join(LOGS_DIR, "error_log.txt")
SUCCESS_LOG = os.path.join(LOGS_DIR, "success_log.txt")


def log_error(message, url=None):
    """Log errors to file with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    error_msg = f"[{timestamp}] {message}"
    if url:
        error_msg += f" URL: {url}"

    print(f"❌ {error_msg}")

    with open(ERROR_LOG, "a") as f:
        f.write(f"{error_msg}\n")

    if url:
        with open(FAILED_POSTS_LOG, "a") as f:
            f.write(f"{url}\n")


def log_success(action_type, url):
    """Log successful actions to file"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(SUCCESS_LOG, "a") as f:
        f.write(f"[{timestamp}] {action_type} - {url}\n")
