from src.platform.instagram.bot import InstagramBot
from src.utils.accounts import TARGET_ACCOUNTS, POSTS_PER_ACCOUNT, BREAK_DURATION
from src.utils.account_logger import AccountLogger
from src.platform.instagram.auth import login, load_session
import time


def main():
    """Main entry point for the social media automation tool"""
    try:
        # Initialize the account logger
        account_logger = AccountLogger()
        
        # Initialize the Instagram bot
        bot = InstagramBot()
        
        # Process accounts in groups of 3
        for i in range(0, len(TARGET_ACCOUNTS), 3):
            # Get next 3 accounts (or remaining accounts)
            current_batch = TARGET_ACCOUNTS[i:i+3]
            
            print(f"\n{'='*50}")
            print(f"Starting new session - Processing accounts {i+1} to {min(i+3, len(TARGET_ACCOUNTS))}")
            print(f"{'='*50}\n")
            
            # Try to use saved session first, if not then login
            if not load_session(bot.driver, bot.wait):
                login(bot.driver, bot.wait)
            
            # Process each account in the current batch
            for account in current_batch:
                print(f"\n{'='*50}")
                print(f"Processing account: @{account}")
                print(f"{'='*50}\n")
                
                try:
                    # Process the account's posts
                    stats = bot.process_profile_posts(
                        profile=account,
                        max_posts=POSTS_PER_ACCOUNT
                    )
                    
                    # Log the account's activity
                    account_logger.log_account_activity(account, stats)
                    
                except Exception as e:
                    print(f"❌ Error processing account @{account}: {e}")
                    continue
            
            # Save the session logs after processing the batch
            account_logger.save_session()
            
            # Log out after processing the batch
            bot.logout()
            
            # Take a break before the next batch (except for the last batch)
            if i + 3 < len(TARGET_ACCOUNTS):
                print(f"\n⏳ Taking a {BREAK_DURATION/60} minute break before next session...")
                time.sleep(BREAK_DURATION)
                
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        raise
    finally:
        if 'bot' in locals():
            bot.driver.quit()
            print("\n🌐 Browser closed")


if __name__ == "__main__":
    main()
