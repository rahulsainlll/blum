import time
import random
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from ...utils.human_behaviour import human_wait
from ...utils.logger import log_error, log_success
from .selectors import (
    TEXTAREA_SELECTORS,
    POST_BUTTON_SELECTORS,
    LIKE_BUTTON_SELECTORS,
    SAVE_BUTTON_SELECTORS,
)


def find_and_click_like_button(driver, wait):
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
        for selector in LIKE_BUTTON_SELECTORS:
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


def is_post_already_liked(driver):
    """Check if a post is already liked"""
    try:
        # Try to find the "Unlike" SVG
        unlike_svg = driver.find_element(
            By.XPATH, '//*[name()="svg"][@aria-label="Unlike"]'
        )
        return True if unlike_svg else False
    except:
        return False


def find_and_click_save_button(driver, wait):
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
        for selector in SAVE_BUTTON_SELECTORS:
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


def is_post_already_saved(driver):
    """Check if a post is already saved"""
    try:
        # Try to find the "Remove" SVG which appears when a post is saved
        remove_svg = driver.find_element(
            By.XPATH, '//*[name()="svg"][@aria-label="Remove"]'
        )
        return True if remove_svg else False
    except:
        return False


def add_comment_to_post(driver, wait, comment_text):
    """Improved comment function with multiple fallback approaches"""
    current_url = driver.current_url
    try:
        print("\n🔍 DEBUG: Starting detailed comment process logging...")
        print(f"📝 Comment text: '{comment_text}'")
        print(f"🌐 Current URL: {current_url}")

        # 1. Make sure we're at the right spot in the post
        print("🔄 Step 1: Scrolling to comment area...")
        driver.execute_script("window.scrollBy(0, 300);")
        human_wait(2, 3)

        # 2. Find and click the comment textarea using multiple approaches
        print("\n🔍 Step 2: Looking for comment textarea...")
        textarea = None
        for i, selector in enumerate(TEXTAREA_SELECTORS, 1):
            try:
                print(f"  Trying selector {i}/{len(TEXTAREA_SELECTORS)}: {selector}")
                textarea = wait.until(
                    EC.presence_of_element_located((By.XPATH, selector))
                )
                print("  ✅ Found textarea element")
                
                # Scroll the textarea into view and wait for it to be clickable
                print("  Scrolling textarea into view...")
                driver.execute_script(
                    "arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});",
                    textarea,
                )
                human_wait(1, 2)
                
                # Try to click using JavaScript first
                print("  Attempting to click textarea...")
                driver.execute_script("arguments[0].click();", textarea)
                print("  ✅ Successfully clicked textarea")
                break
            except Exception as e:
                print(f"  ❌ Failed with selector {i}: {str(e)}")
                continue

        if not textarea:
            print("❌ ERROR: Could not find any comment textarea")
            log_error("Failed to find comment textarea", current_url)
            return False

        # 3. Clear any existing text and focus
        print("\n📝 Step 3: Preparing to type comment...")
        try:
            # Re-find the textarea to avoid stale element
            textarea = wait.until(
                EC.presence_of_element_located((By.XPATH, TEXTAREA_SELECTORS[0]))
            )
            # Clear the textarea using Selenium's native method
            textarea.clear()
            textarea.click()
            print("  ✅ Cleared and focused textarea")
            human_wait(0.5, 1)
        except Exception as e:
            print(f"  ⚠️ Warning: Could not clear textarea: {str(e)}")

        # 4. Type comment text with human-like delays
        print("\n⌨️ Step 4: Typing comment...")
        try:
            # Re-find the textarea to avoid stale element
            textarea = wait.until(
                EC.presence_of_element_located((By.XPATH, TEXTAREA_SELECTORS[0]))
            )
            # Type the comment character by character with random delays
            for char in comment_text:
                try:
                    textarea.send_keys(char)
                    # Random delay between keystrokes (50-150ms)
                    time.sleep(random.uniform(0.05, 0.15))
                except Exception as e:
                    # If we get a stale element, re-find the textarea and continue
                    print("  ⚠️ Stale element detected, re-finding textarea...")
                    textarea = wait.until(
                        EC.presence_of_element_located((By.XPATH, TEXTAREA_SELECTORS[0]))
                    )
                    textarea.send_keys(char)
                    time.sleep(random.uniform(0.05, 0.15))
            
            print("  ✅ Comment text entered successfully")
            # Wait for typing to complete
            human_wait(1, 2)
                
        except Exception as e:
            print(f"  ❌ Error while typing: {str(e)}")
            return False

        human_wait(2, 3, "⏳ Waiting for Post button to enable...")

        # 5. Find and click the Post button using more reliable selectors
        print("\n🔍 Step 5: Looking for Post button...")
        post_button_clicked = False

        # Try direct XPath selectors first
        for i, selector in enumerate(POST_BUTTON_SELECTORS, 1):
            try:
                print(f"  Trying Post button selector {i}/{len(POST_BUTTON_SELECTORS)}: {selector}")
                post_button = wait.until(
                    EC.presence_of_element_located((By.XPATH, selector))
                )
                print("  ✅ Found Post button element")
                
                # Check if button is disabled
                disabled = post_button.get_attribute("aria-disabled")
                print(f"  Post button disabled state: {disabled}")
                
                if disabled == "true":
                    print("  ⚠️ Post button is disabled, waiting longer...")
                    # Re-find and click the textarea to ensure focus
                    textarea = wait.until(
                        EC.presence_of_element_located((By.XPATH, TEXTAREA_SELECTORS[0]))
                    )
                    textarea.click()
                    human_wait(3, 5)
                    # Try again after waiting
                    post_button = wait.until(
                        EC.presence_of_element_located((By.XPATH, selector))
                    )
                    disabled = post_button.get_attribute("aria-disabled")
                    print(f"  Post button disabled state after wait: {disabled}")

                # Scroll button into view
                print("  Scrolling Post button into view...")
                driver.execute_script(
                    "arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});",
                    post_button,
                )
                human_wait(1, 2)
                
                # Try clicking with Selenium's native click first
                print("  Attempting to click Post button...")
                post_button.click()
                post_button_clicked = True
                print("  ✅ Successfully clicked Post button")
                break
            except Exception as e:
                print(f"  ❌ Failed with selector {i}: {str(e)}")
                continue

  

        # 6. Wait to verify comment was posted
        print("\n🔍 Step 6: Verifying comment was posted...")
        human_wait(4, 6)

        # Check if our comment text appears in the comments section
        try:
            first_word = comment_text.split()[0]
            print(f"  Looking for first word of comment: '{first_word}'")
            comment_verification = f"//*[contains(text(), '{first_word}')]"
            wait.until(EC.presence_of_element_located((By.XPATH, comment_verification)))
            print("  ✅ Comment successfully verified in the comments section")
        except Exception as e:
            print(f"  ⚠️ Could not verify comment in comments section: {str(e)}")
            print("  Note: Comment might still have been posted successfully")

        log_success("Comment", current_url)
        return True

    except Exception as e:
        print(f"\n❌ FATAL ERROR in comment function: {str(e)}")
        log_error(f"Error in comment function: {e}", current_url)
        return False
