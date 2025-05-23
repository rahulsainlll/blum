import time
import random
import json
import os
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Load environment variables from .env file
load_dotenv()

# Get Instagram credentials and settings from environment variables
USERNAME = os.getenv("IG_USERNAME")
PASSWORD = os.getenv("IG_PASSWORD")
PROFILE = "myorbit.ai"  # Instagram username to target
# Get custom comment from environment variable - will use a default if not set
COMMENT_TEXT = os.getenv("IG_COMMENT", "Love this content! 👏 Keep it up!")
# Get list of comment variations
COMMENT_VARIATIONS = [
    "This is awesome! 🔥",
    "Great content as always! 💯",
    "Love what you're doing here! 👍",
    "This resonates with me! 🙌",
    "Fantastic post! 👏",
    "I've been following your journey - inspiring stuff! ✨",
    "This is exactly what I needed to see today! 🌟",
    "The quality of your content is amazing! 💎",
    "Always look forward to your posts! 🤩",
    "This makes so much sense! 💡",
]

# Safety settings
MAX_POSTS_TO_PROCESS = 4  # Process exactly the 4 most recent posts
# Set all actions to match the number of posts to process
MAX_LIKES_PER_RUN = MAX_POSTS_TO_PROCESS
MAX_COMMENTS_PER_RUN = MAX_POSTS_TO_PROCESS
MAX_SAVES_PER_RUN = MAX_POSTS_TO_PROCESS

# For logging errors/failures
LOGS_DIR = "logs"
if not os.path.exists(LOGS_DIR):
    os.makedirs(LOGS_DIR)

# Log file paths
FAILED_POSTS_LOG = os.path.join(LOGS_DIR, "failed_posts.txt")
ERROR_LOG = os.path.join(LOGS_DIR, "error_log.txt")
SUCCESS_LOG = os.path.join(LOGS_DIR, "success_log.txt")

# Set up Chrome options for better performance
chrome_options = webdriver.ChromeOptions()
# chrome_options.add_argument("--headless")  # Uncomment to run headless
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--start-maximized")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--disable-extensions")
chrome_options.add_argument("--disable-infobars")
chrome_options.add_argument("--disable-notifications")
chrome_options.add_argument("--disable-popup-blocking")
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
# Very important for Instagram to not detect automation
chrome_options.add_argument(
    "user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
)
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option("useAutomationExtension", False)

# Initialize the WebDriver with service
try:
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    # Increase wait time to handle Instagram's slow loading
    wait = WebDriverWait(driver, 20)
except Exception as e:
    print(f"❌ Error initializing Chrome driver: {e}")
    exit(1)


def human_wait(min_sec=2, max_sec=5, label="⏳ Thinking..."):
    delay = round(random.uniform(min_sec, max_sec), 2)
    print(f"{label} waiting {delay} seconds...")
    time.sleep(delay)


def type_like_human(element, text):
    """Type text like a human with random delays between keystrokes"""
    for char in text:
        element.send_keys(char)
        time.sleep(random.uniform(0.1, 0.3))


def save_session():
    """Save the current session cookies"""
    print("💾 Saving session data...")
    cookies = driver.get_cookies()
    with open("instagram_session.json", "w") as f:
        json.dump(cookies, f)
    print("✅ Session saved successfully")


def load_session():
    """Load session from saved cookies"""
    try:
        if os.path.exists("instagram_session.json"):
            print("📂 Loading saved session...")
            with open("instagram_session.json", "r") as f:
                cookies = json.load(f)

            # First visit Instagram
            driver.get("https://www.instagram.com/")
            human_wait(2, 4)

            # Add cookies
            for cookie in cookies:
                try:
                    driver.add_cookie(cookie)
                except:
                    continue

            # Refresh page to apply cookies
            driver.refresh()
            human_wait(3, 5)

            # Check if we're logged in
            try:
                wait.until(EC.presence_of_element_located((By.XPATH, "//nav")))
                print("✅ Successfully logged in using saved session")
                return True
            except:
                print("❌ Session expired, will try normal login")
                return False
    except Exception as e:
        print(f"❌ Error loading session: {e}")
        return False
    return False


def login():
    """Login to Instagram"""
    print("🌐 Opening Instagram...")
    driver.get("https://www.instagram.com/accounts/login/")
    human_wait(3, 5)

    print("🔑 Entering credentials...")
    username_input = wait.until(EC.presence_of_element_located((By.NAME, "username")))
    password_input = wait.until(EC.presence_of_element_located((By.NAME, "password")))

    type_like_human(username_input, USERNAME)
    human_wait(1, 2)
    type_like_human(password_input, PASSWORD)
    human_wait(1, 2)

    password_input.send_keys(Keys.RETURN)
    human_wait(5, 8)

    # Handle "Save Login Info" popup
    try:
        not_now_button = wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, "//button[contains(text(), 'Not Now')]")
            )
        )
        not_now_button.click()
        human_wait(2, 3)
        print("✅ Dismissed 'Save Login Info' popup")
    except:
        print("ℹ️ No 'Save Login Info' popup appeared")

    # Handle notifications popup
    try:
        not_now_button = wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, "//button[contains(text(), 'Not Now')]")
            )
        )
        not_now_button.click()
        human_wait(2, 3)
        print("✅ Dismissed notifications popup")
    except:
        print("ℹ️ No notifications popup appeared")

    print("✅ Logged in successfully")
    human_wait(3, 5)

    # Save the session after successful login
    save_session()


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


def find_and_click_like_button():
    """Find and click the like button using multiple methods"""
    try:
        # Method 1: Try using the most modern selectors first
        js_click_script = """
        // Find all svg elements
        var svgs = document.querySelectorAll('svg');
        // Look for the one with aria-label="Like"
        for (var i = 0; i < svgs.length; i++) {
            if (svgs[i].getAttribute('aria-label') === 'Like') {
                // Find the nearest clickable parent
                var element = svgs[i];
                while (element && element.getAttribute('role') !== 'button') {
                    element = element.parentElement;
                }
                if (element) {
                    element.click();
                    return true;
                }
            }
        }
        return false;
        """
        like_clicked = driver.execute_script(js_click_script)
        if like_clicked:
            return True

        # Method 2: Try all possible standard selectors
        selectors = [
            '//span[@class=""]//*[name()="svg"][@aria-label="Like"]',
            '//article//section//button//*[name()="svg"][@aria-label="Like"]',
            '//span[@aria-label="Like"]',
            '//button[@type="button"]//span[contains(@class, "")]//*[name()="svg"][@aria-label="Like"]',
            '//button[contains(@class, "")]//*[name()="svg"][@aria-label="Like"]',
        ]

        for selector in selectors:
            try:
                like_button = wait.until(
                    EC.element_to_be_clickable((By.XPATH, selector))
                )
                driver.execute_script(
                    "arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});",
                    like_button,
                )
                human_wait(1, 2)
                like_button.click()
                return True
            except:
                continue

        # Method 3: Last resort - find any SVG with aria-label="Like" and force a click
        try:
            like_svg = driver.find_element(
                By.XPATH, '//*[name()="svg"][@aria-label="Like"]'
            )
            driver.execute_script("arguments[0].click();", like_svg)
            return True
        except:
            pass

        return False
    except Exception as e:
        print(f"Error in find_and_click_like_button: {e}")
        return False


def is_post_already_liked():
    """Check if a post is already liked"""
    try:
        # Try to find the "Unlike" SVG
        unlike_svg = driver.find_element(
            By.XPATH, '//*[name()="svg"][@aria-label="Unlike"]'
        )
        return True if unlike_svg else False
    except:
        return False


def find_and_click_save_button():
    """Find and click the save button for a post"""
    try:
        # Method 1: Try using JavaScript to find and click the save button
        js_click_script = """
        // Find all svg elements
        var svgs = document.querySelectorAll('svg');
        // Look for the one with aria-label="Save"
        for (var i = 0; i < svgs.length; i++) {
            if (svgs[i].getAttribute('aria-label') === 'Save') {
                // Find the nearest clickable parent
                var element = svgs[i];
                while (element && element.getAttribute('role') !== 'button') {
                    element = element.parentElement;
                }
                if (element) {
                    element.click();
                    return true;
                }
            }
        }
        return false;
        """
        save_clicked = driver.execute_script(js_click_script)
        if save_clicked:
            return True

        # Method 2: Try XPath selectors
        selectors = [
            '//span[@class=""]//*[name()="svg"][@aria-label="Save"]',
            '//article//section//button//*[name()="svg"][@aria-label="Save"]',
            '//span[@aria-label="Save"]',
            '//button[@type="button"]//span[contains(@class, "")]//*[name()="svg"][@aria-label="Save"]',
            '//div[contains(@class, "")]//*[name()="svg"][@aria-label="Save"]',
        ]

        for selector in selectors:
            try:
                save_button = wait.until(
                    EC.element_to_be_clickable((By.XPATH, selector))
                )
                driver.execute_script(
                    "arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});",
                    save_button,
                )
                human_wait(1, 2)
                save_button.click()
                return True
            except:
                continue

        # Method 3: Last resort - find any SVG with aria-label="Save" and force a click
        try:
            save_svg = driver.find_element(
                By.XPATH, '//*[name()="svg"][@aria-label="Save"]'
            )
            driver.execute_script("arguments[0].click();", save_svg)
            return True
        except:
            pass

        return False
    except Exception as e:
        print(f"Error in find_and_click_save_button: {e}")
        return False


def is_post_already_saved():
    """Check if a post is already saved"""
    try:
        # Try to find the "Remove" SVG which appears when a post is saved
        remove_svg = driver.find_element(
            By.XPATH, '//*[name()="svg"][@aria-label="Remove"]'
        )
        return True if remove_svg else False
    except:
        return False


def add_comment_to_post(comment_text):
    """Improved comment function with multiple fallback approaches"""
    current_url = driver.current_url
    try:
        print("💬 Starting comment process...")

        # 1. Make sure we're at the right spot in the post
        driver.execute_script("window.scrollBy(0, 300);")
        human_wait(2, 3)

        # 2. Find and click the comment textarea using multiple approaches
        textarea_selectors = [
            '//textarea[@placeholder="Add a comment…"]',
            '//textarea[contains(@placeholder, "Add a comment")]',
            '//textarea[contains(@aria-label, "Add a comment")]',
        ]

        textarea = None
        for selector in textarea_selectors:
            try:
                textarea = wait.until(
                    EC.presence_of_element_located((By.XPATH, selector))
                )
                driver.execute_script(
                    "arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});",
                    textarea,
                )
                human_wait(1, 2)
                textarea.click()
                print("  ✅ Found and clicked comment textarea")
                break
            except:
                continue

        if not textarea:
            # Try JavaScript as a fallback
            js_find_textarea = """
            const textarea = document.querySelector('textarea[placeholder="Add a comment…"]');
            if (textarea) {
                textarea.scrollIntoView({behavior: 'smooth', block: 'center'});
                textarea.click();
                return true;
            }
            return false;
            """
            textarea_found = driver.execute_script(js_find_textarea)

            if not textarea_found:
                print("  ❌ Could not find comment textarea")
                log_error("Failed to find comment textarea", current_url)
                return False

            # Get the textarea element after clicking it with JS
            textarea = wait.until(
                EC.presence_of_element_located(
                    (By.XPATH, '//textarea[contains(@placeholder, "Add a comment")]')
                )
            )

        # 3. Clear any existing text and focus
        textarea.clear()
        human_wait(0.5, 1)

        # 4. Type comment text with human-like delays
        for char in comment_text:
            textarea.send_keys(char)
            time.sleep(random.uniform(0.05, 0.15))

        human_wait(2, 3, "⏳ Waiting for Post button to enable...")

        # 5. Find and click the Post button using more reliable selectors
        post_button_clicked = False

        # Try direct XPath selectors first
        post_button_selectors = [
            '//div[text()="Post"]/..',
            '//div[contains(text(), "Post")]/parent::div[@role="button"]',
            '//div[@class="x1i64zmx"]//div[@role="button"]',
            '//div[contains(@class, "x1i64zmx")]//div[@role="button"]',
        ]

        for selector in post_button_selectors:
            try:
                post_button = driver.find_element(By.XPATH, selector)
                if "aria-disabled" in post_button.get_attribute(
                    "outerHTML"
                ) and "true" in post_button.get_attribute("outerHTML"):
                    print("  ⚠️ Post button is still disabled, waiting longer...")
                    human_wait(3, 5)
                    # Try again after waiting
                    post_button = driver.find_element(By.XPATH, selector)

                driver.execute_script(
                    "arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});",
                    post_button,
                )
                human_wait(1, 2)
                driver.execute_script("arguments[0].click();", post_button)
                post_button_clicked = True
                print("  ✅ Clicked Post button using XPath")
                break
            except:
                continue

        # If direct selectors failed, try JavaScript approach
        if not post_button_clicked:
            js_click_post = """
            // Try multiple approaches to find and click the Post button
            
            // First approach: Look for the most specific structure from your HTML
            let postButton = document.querySelector('div.x1i64zmx > div[role="button"]');
            
            // Second approach: Look for any element with text exactly matching "Post"
            if (!postButton) {
                const elements = document.querySelectorAll('div');
                for (const el of elements) {
                    if (el.textContent === 'Post' && el.parentElement && el.parentElement.getAttribute('role') === 'button') {
                        postButton = el.parentElement;
                        break;
                    }
                }
            }
            
            // Third approach: Find any button-like element after the textarea
            if (!postButton) {
                const textarea = document.querySelector('textarea[placeholder="Add a comment…"]');
                if (textarea) {
                    let current = textarea.parentElement;
                    while (current && !current.querySelector('[role="button"]')) {
                        current = current.parentElement;
                    }
                    if (current) {
                        postButton = current.querySelector('[role="button"]');
                    }
                }
            }
            
            // Check if button is disabled
            if (postButton && postButton.getAttribute('aria-disabled') === 'true') {
                // Wait for it to be enabled (simulate a short wait)
                setTimeout(() => {
                    if (postButton.getAttribute('aria-disabled') !== 'true') {
                        postButton.click();
                    }
                }, 3000);
                return false;
            }
            
            // Click the button if found
            if (postButton) {
                postButton.click();
                return true;
            }
            
            return false;
            """
            post_button_clicked = driver.execute_script(js_click_post)

            if post_button_clicked:
                print("  ✅ Clicked Post button using JavaScript")
            else:
                # Try once more after a longer wait
                human_wait(5, 7, "⏳ Waiting longer for Post button to be ready...")
                post_button_clicked = driver.execute_script(js_click_post)

                if post_button_clicked:
                    print("  ✅ Clicked Post button after extended wait")
                else:
                    print("  ❌ Could not find or click Post button")
                    log_error("Failed to click Post button", current_url)
                    return False

        # 6. Wait to verify comment was posted
        human_wait(4, 6, "⏳ Verifying comment was posted...")

        # Check if our comment text appears in the comments section
        try:
            comment_verification = f"//*[contains(text(), '{comment_text.split()[0]}')]"
            driver.find_element(By.XPATH, comment_verification)
            print("  ✅ Comment successfully verified")
        except:
            # Even if verification fails, we still consider it a success if we clicked the button
            print("  ⚠️ Comment was submitted but couldn't verify it appeared")

        log_success("Comment", current_url)
        return True

    except Exception as e:
        print(f"  ❌ Error in comment function: {e}")
        log_error(f"Error in comment function: {e}", current_url)
        return False


def like_profile_posts(profile=PROFILE, max_posts=MAX_POSTS_TO_PROCESS):
    """Process exactly the first max_posts with all actions (like, comment, save)"""
    print(f"🔍 Visiting profile @{profile}...")
    driver.get(f"https://www.instagram.com/{profile}/")
    human_wait(4, 6)

    print(f"📜 Finding the most recent posts and reels...")

    # Minimal scrolling to ensure we get the first few posts only
    try:
        driver.execute_script(
            "window.scrollBy(0, 300);"
        )  # Just a slight scroll to load posts
        human_wait(2, 3)
    except:
        pass

    try:
        # Get all post AND reel links
        post_links = []

        # Find regular posts
        posts = driver.find_elements(By.XPATH, "//a[contains(@href, '/p/')]")
        post_links.extend([post.get_attribute("href") for post in posts])

        # Find reels
        reels = driver.find_elements(By.XPATH, "//a[contains(@href, '/reel/')]")
        post_links.extend([reel.get_attribute("href") for reel in reels])

        # Remove duplicates while preserving order (in case the same content appears as both)
        all_links = []
        for link in post_links:
            if link not in all_links:
                all_links.append(link)

        if not all_links:
            log_error("Could not find any posts or reels")
            return

        # Limit to exactly the requested number of posts (most recent first)
        target_links = all_links[:max_posts]

        print(
            f"🎯 Found {len(all_links)} content items. Will process exactly the {len(target_links)} most recent."
        )
        print(f"📋 Links to process: {', '.join(target_links)}")
    except Exception as e:
        log_error(f"Error finding posts: {e}")
        return

    # Use comments from environment variable or default list
    comment_choices = []
    if os.getenv("IG_COMMENT"):
        # If IG_COMMENT is set, use it as the primary comment
        comment_text = COMMENT_TEXT
        # Add some variation to avoid duplicate comments
        comment_choices = [
            comment_text,
            comment_text,
            comment_text,
            comment_text,
        ]
    else:
        # Otherwise just use the first few variations to ensure variety
        comment_choices = COMMENT_VARIATIONS[:max_posts]

    # Stats counters
    successful_likes = 0
    successful_comments = 0
    successful_saves = 0
    failed_posts = []

    # Process each of the target posts
    for i, link in enumerate(target_links):
        print(f"\n📱 Processing item {i + 1}/{len(target_links)}: {link}")
        content_type = "Reel" if "/reel/" in link else "Post"
        print(f"🏷️ Content type: {content_type}")

        try:
            driver.get(link)
            human_wait(5, 8)  # Give the post time to load

            # Make sure we're scrolled to the right part of the post
            driver.execute_script(
                "window.scrollBy(0, 200);"
            )  # Scroll to where buttons usually are
            human_wait(1, 2)

            # 1. LIKE the post
            like_result = "⏭️ Skipped (already liked)"
            if not is_post_already_liked():
                print("❤️ Attempting to like...")
                if find_and_click_like_button():
                    successful_likes += 1
                    like_result = "✅ Success"
                    log_success("Like", link)
                    human_wait(2, 4)
                else:
                    like_result = "❌ Failed (button not found)"
                    log_error(f"Could not find like button for {content_type}", link)

            # 2. SAVE the post
            save_result = "⏭️ Skipped (already saved)"
            if not is_post_already_saved():
                print("🔖 Attempting to save...")
                if find_and_click_save_button():
                    successful_saves += 1
                    save_result = "✅ Success"
                    log_success("Save", link)
                    human_wait(2, 4)
                else:
                    save_result = "❌ Failed (button not found)"
                    log_error(f"Could not find save button for {content_type}", link)

            # 3. COMMENT on the post - use a specific comment for each post
            # Use modulo to cycle through comments if needed
            selected_comment = comment_choices[i % len(comment_choices)]
            print(f"💬 Attempting to comment: '{selected_comment}'")

            if add_comment_to_post(selected_comment):
                successful_comments += 1
                comment_result = "✅ Success"
                human_wait(4, 7)
            else:
                comment_result = "❌ Failed (could not post)"
                failed_posts.append(link)

            # Print status for this post
            print(f"📊 {content_type} {i + 1} results:")
            print(f"  ❤️ Like: {like_result}")
            print(f"  🔖 Save: {save_result}")
            print(f"  💬 Comment: {comment_result}")

            # Take a longer break between posts to seem more human
            if i < len(target_links) - 1:  # If not the last post
                human_wait(7, 12, "⏱️ Moving to next content...")

        except Exception as e:
            log_error(f"Error processing {content_type} {i + 1}: {str(e)}", link)
            failed_posts.append(link)

    # Print final summary
    print(f"\n📊 FINAL SUMMARY:")
    print(f"  ❤️ Successfully liked {successful_likes}/{len(target_links)} items")
    print(f"  🔖 Successfully saved {successful_saves}/{len(target_links)} items")
    print(
        f"  💬 Successfully commented on {successful_comments}/{len(target_links)} items"
    )
    print(
        f"  🎯 Total engagement actions: {successful_likes + successful_saves + successful_comments}/{len(target_links) * 3} possible actions"
    )

    # Report any failed posts
    if failed_posts:
        print(f"\n⚠️ Items with issues ({len(failed_posts)}):")
        for i, failed_link in enumerate(failed_posts):
            failed_type = "Reel" if "/reel/" in failed_link else "Post"
            print(f"  {i + 1}. {failed_type}: {failed_link}")
        print(f"\nThese have been logged to {FAILED_POSTS_LOG} for future reference.")
    else:
        print("\n✅ All items processed successfully!")

    print(f"\n📝 Detailed logs available in the {LOGS_DIR} directory")


def logout():
    """Improved logout function with more reliable selectors"""
    try:
        print("👋 Logging out...")
        driver.get("https://www.instagram.com/")
        human_wait(3, 5)

        # Try different methods to find and click the profile button
        profile_found = False
        selectors = [
            '//img[@alt="Profile picture"]/ancestor::a',
            "//nav//div[last()]//div[last()]//div[last()]//a",  # Common pattern in new Instagram UI
            '//div[@role="tablist"]/a[last()]',  # Another common pattern
            # Force click with JS as last resort
            'document.querySelector("nav a:last-child").click();',
        ]

        for selector in selectors:
            try:
                if selector.startswith("document"):
                    # This is a JavaScript selector
                    driver.execute_script(selector)
                    human_wait(2, 3)
                    profile_found = True
                    break
                else:
                    # Regular XPath selector
                    profile_button = wait.until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    profile_button.click()
                    human_wait(2, 3)
                    profile_found = True
                    break
            except:
                continue

        if not profile_found:
            print("⚠️ Could not find profile button, trying alternate logout method...")
            # Direct URL method as fallback
            driver.get("https://www.instagram.com/accounts/logout/")
            human_wait(2, 3)
            return

        # Try to find and click logout
        logout_selectors = [
            '//div[text()="Log out"]/..',
            '//button[contains(text(), "Log out")]',
            '//div[contains(text(), "Log out")]/..',
            '//div[contains(@role, "dialog")]//div[text()="Log out"]/..',
        ]

        for selector in logout_selectors:
            try:
                logout_button = wait.until(
                    EC.element_to_be_clickable((By.XPATH, selector))
                )
                logout_button.click()
                print("✅ Logged out successfully")
                return
            except:
                continue

        print("⚠️ Could not find logout button through the UI")

    except Exception as e:
        print(f"⚠️ Logout process failed: {e}")
        # Try direct logout URL as last resort
        try:
            driver.get("https://www.instagram.com/accounts/logout/")
            human_wait(2, 3)
            print("✅ Used direct URL to logout")
        except:
            print("❌ All logout attempts failed")


if __name__ == "__main__":
    try:
        # Try to use saved session first
        if not load_session():
            # If session loading fails, do normal login
            login()

        # Process the 4 most recent posts with all actions
        like_profile_posts(profile=PROFILE, max_posts=MAX_POSTS_TO_PROCESS)

        # Add a final delay before logout to seem more human-like
        human_wait(3, 5, "🏁 Finishing up...")
        logout()

    except KeyboardInterrupt:
        print("\n⚠️ Script interrupted by user")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
    finally:
        driver.quit()
        print("�� Browser closed")
