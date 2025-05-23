import json
import os
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from ...utils.human_behaviour import human_wait, type_like_human
from ...utils.config import USERNAME, PASSWORD


def save_session(driver):
    """Save the current session cookies"""
    print("💾 Saving session data...")
    cookies = driver.get_cookies()
    with open("instagram_session.json", "w") as f:
        json.dump(cookies, f)
    print("✅ Session saved successfully")


def load_session(driver, wait):
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


def login(driver, wait):
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
    save_session(driver)


def logout(driver, wait):
    """Improved logout function with more reliable selectors"""
    try:
        print("👋 Logging out...")
        driver.get("https://www.instagram.com/")
        human_wait(3, 5)

        # Try different methods to find and click the profile button
        profile_found = False
        from .selectors import PROFILE_BUTTON_SELECTORS

        for selector in PROFILE_BUTTON_SELECTORS:
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
        from .selectors import LOGOUT_BUTTON_SELECTORS

        for selector in LOGOUT_BUTTON_SELECTORS:
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
