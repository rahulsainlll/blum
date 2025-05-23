from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from src.utils.config import (
    COMMENT_TEXT,
    COMMENT_VARIATIONS,
    CHROME_OPTIONS,
)
from src.utils.human_behaviour import human_wait
from src.utils.logger import log_error, log_success
from .auth import login, load_session, logout
from .actions import (
    find_and_click_like_button,
    is_post_already_liked,
    find_and_click_save_button,
    is_post_already_saved,
    add_comment_to_post,
)


class InstagramBot:
    def __init__(self):
        self.setup_driver()
        self.wait = WebDriverWait(self.driver, 20)

    def setup_driver(self):
        """Set up the Chrome WebDriver with appropriate options"""
        chrome_options = webdriver.ChromeOptions()
        for arg in CHROME_OPTIONS["arguments"]:
            chrome_options.add_argument(arg)
        chrome_options.add_argument(f"user-agent={CHROME_OPTIONS['user_agent']}")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option("useAutomationExtension", False)

        try:
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
        except Exception as e:
            print(f"❌ Error initializing Chrome driver: {e}")
            raise

    def process_profile_posts(self, profile, max_posts):
        """Process exactly the first max_posts with all actions (like, comment, save)"""
        print(f"🔍 Visiting profile @{profile}...")
        self.driver.get(f"https://www.instagram.com/{profile}/")
        human_wait(4, 6)

        # Stats dictionary to track activities
        stats = {
            "username": profile,
            "posts_processed": 0,
            "likes": 0,
            "comments": 0,
            "saves": 0,
            "failed_posts": [],
            "processed_links": []
        }

        print(f"📜 Finding the most recent posts and reels...")

        # Minimal scrolling to ensure we get the first few posts only
        try:
            self.driver.execute_script("window.scrollBy(0, 300);")
            human_wait(2, 3)
        except:
            pass

        try:
            # Get all post AND reel links
            post_links = []

            # Find regular posts
            posts = self.driver.find_elements(By.XPATH, "//a[contains(@href, '/p/')]")
            post_links.extend([post.get_attribute("href") for post in posts])

            # Find reels
            reels = self.driver.find_elements(
                By.XPATH, "//a[contains(@href, '/reel/')]"
            )
            post_links.extend([reel.get_attribute("href") for reel in reels])

            # Remove duplicates while preserving order
            all_links = []
            for link in post_links:
                if link not in all_links:
                    all_links.append(link)

            if not all_links:
                log_error(f"Could not find any posts or reels for @{profile}")
                return stats

            # Limit to exactly the requested number of posts (most recent first)
            target_links = all_links[:max_posts]
            stats["posts_processed"] = len(target_links)

            print(
                f"🎯 Found {len(all_links)} content items for @{profile}. Will process exactly the {len(target_links)} most recent."
            )
            print(f"📋 Links to process: {', '.join(target_links)}")
        except Exception as e:
            log_error(f"Error finding posts for @{profile}: {e}")
            return stats

        # Use comments from environment variable or default list
        comment_choices = []
        if COMMENT_TEXT:
            # If IG_COMMENT is set, use it as the primary comment
            comment_text = COMMENT_TEXT
            # Add some variation to avoid duplicate comments
            comment_choices = [
                comment_text,
                comment_text,
                comment_text ,
                comment_text ,
            ]
        else:
            # Otherwise just use the first few variations to ensure variety
            comment_choices = COMMENT_VARIATIONS[:max_posts]

        # Process each of the target posts
        for i, link in enumerate(target_links):
            print(f"\n📱 Processing item {i + 1}/{len(target_links)}: {link}")
            content_type = "Reel" if "/reel/" in link else "Post"
            print(f"🏷️ Content type: {content_type}")

            try:
                self.driver.get(link)
                human_wait(5, 8)  # Give the post time to load

                # Make sure we're scrolled to the right part of the post
                self.driver.execute_script("window.scrollBy(0, 200);")
                human_wait(1, 2)

                # 1. LIKE the post
                like_result = "⏭️ Skipped (already liked)"
                if not is_post_already_liked(self.driver):
                    print("❤️ Attempting to like...")
                    if find_and_click_like_button(self.driver, self.wait):
                        stats["likes"] += 1
                        like_result = "✅ Success"
                        log_success("Like", link)
                        human_wait(2, 4)
                    else:
                        like_result = "❌ Failed (button not found)"
                        log_error(
                            f"Could not find like button for {content_type}", link
                        )

                # 2. SAVE the post
                save_result = "⏭️ Skipped (already saved)"
                if not is_post_already_saved(self.driver):
                    print("🔖 Attempting to save...")
                    if find_and_click_save_button(self.driver, self.wait):
                        stats["saves"] += 1
                        save_result = "✅ Success"
                        log_success("Save", link)
                        human_wait(2, 4)
                    else:
                        save_result = "❌ Failed (button not found)"
                        log_error(
                            f"Could not find save button for {content_type}", link
                        )

                # 3. COMMENT on the post - use a specific comment for each post
                # Use modulo to cycle through comments if needed
                selected_comment = comment_choices[i % len(comment_choices)]
                print(f"💬 Attempting to comment: '{selected_comment}'")

                if add_comment_to_post(self.driver, self.wait, selected_comment):
                    stats["comments"] += 1
                    comment_result = "✅ Success"
                    human_wait(4, 7)
                else:
                    comment_result = "❌ Failed (could not post)"
                    stats["failed_posts"].append(link)

                # Add to processed links
                stats["processed_links"].append({
                    "url": link,
                    "type": content_type,
                    "like": like_result,
                    "save": save_result,
                    "comment": comment_result
                })

                # Print status for this post
                print(f"📊 {content_type} {i + 1} results:")
                print(f"  ❤️ Like: {like_result}")
                print(f"  🔖 Save: {save_result}")
                print(f"  💬 Comment: {comment_result}")

                # Take a longer break between posts to seem more human
                if i < len(target_links) - 1:  # If not the last post
                    human_wait(7, 12, "⏱️ Moving to next content...")

            except Exception as e:
                log_error(f"Error processing {content_type} {i + 1} for @{profile}: {str(e)}", link)
                stats["failed_posts"].append(link)

        # Print final summary
        print(f"\n📊 FINAL SUMMARY for @{profile}:")
        print(f"  ❤️ Successfully liked {stats['likes']}/{len(target_links)} items")
        print(f"  🔖 Successfully saved {stats['saves']}/{len(target_links)} items")
        print(
            f"  💬 Successfully commented on {stats['comments']}/{len(target_links)} items"
        )
        print(
            f"  🎯 Total engagement actions: {stats['likes'] + stats['saves'] + stats['comments']}/{len(target_links) * 3} possible actions"
        )

        # Report any failed posts
        if stats["failed_posts"]:
            print(f"\n⚠️ Items with issues ({len(stats['failed_posts'])}):")
            for i, failed_link in enumerate(stats["failed_posts"]):
                failed_type = "Reel" if "/reel/" in failed_link else "Post"
                print(f"  {i + 1}. {failed_type}: {failed_link}")
            print(
                f"\nThese have been logged to logs/failed_posts.txt for future reference."
            )
        else:
            print("\n✅ All items processed successfully!")

        print(f"\n📝 Detailed logs available in the logs directory")
        
        return stats

    def logout(self):
        """Log out from Instagram"""
        try:
            logout(self.driver, self.wait)
            print("👋 Successfully logged out")
        except Exception as e:
            print(f"❌ Error during logout: {e}")
