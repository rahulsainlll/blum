from src.platform.instagram.bot import InstagramBot
from src.utils.accounts import (
    TARGET_ACCOUNTS, POSTS_PER_ACCOUNT, BREAK_BETWEEN_ACCOUNTS,
    BREAK_BETWEEN_BATCHES, BATCH_SIZE, MAX_ACTIONS_PER_DAY,
    MAX_ACCOUNTS_PER_DAY
)
from src.utils.account_logger import AccountLogger
from src.platform.instagram.auth import login, load_session
import time
from datetime import datetime, timedelta


def main():
    """Main entry point for the social media automation tool"""
    try:
        # Initialize the account logger
        account_logger = AccountLogger()
        
        # Initialize the Instagram bot
        bot = InstagramBot()
        
        # Track daily limits
        daily_actions = 0
        daily_accounts = 0
        start_time = datetime.now()
        
        # Process accounts in batches
        for i in range(0, len(TARGET_ACCOUNTS), BATCH_SIZE):
            # Check daily limits
            if daily_accounts >= MAX_ACCOUNTS_PER_DAY:
                print(f"\n⚠️ Daily account limit reached ({MAX_ACCOUNTS_PER_DAY} accounts)")
                break
                
            # Get next batch of accounts
            current_batch = TARGET_ACCOUNTS[i:i+BATCH_SIZE]
            
            print(f"\n{'='*50}")
            print(f"Starting new batch - Processing accounts {i+1} to {min(i+BATCH_SIZE, len(TARGET_ACCOUNTS))}")
            print(f"Daily progress: {daily_accounts}/{MAX_ACCOUNTS_PER_DAY} accounts, {daily_actions}/{MAX_ACTIONS_PER_DAY} actions")
            print(f"{'='*50}\n")
            
            # Try to use saved session first, if not then login
            if not load_session(bot.driver, bot.wait):
                login(bot.driver, bot.wait)
            
            # Process each account in the current batch
            for account in current_batch:
                if daily_accounts >= MAX_ACCOUNTS_PER_DAY:
                    break
                    
                print(f"\n{'='*50}")
                print(f"Processing account: @{account}")
                print(f"{'='*50}\n")
                
                try:
                    # Process the account's posts
                    stats = bot.process_profile_posts(
                        profile=account,
                        max_posts=POSTS_PER_ACCOUNT
                    )
                    
                    # Update daily action count
                    actions_taken = stats['likes'] + stats['comments'] + stats['saves']
                    daily_actions += actions_taken
                    daily_accounts += 1
                    
                    # Log the account's activity
                    account_logger.log_account_activity(account, stats)
                    
                    # Check if we've hit the daily action limit
                    if daily_actions >= MAX_ACTIONS_PER_DAY:
                        print(f"\n⚠️ Daily action limit reached ({MAX_ACTIONS_PER_DAY} actions)")
                        break
                    
                    # Take a short break between accounts
                    if account != current_batch[-1]:  # If not the last account in batch
                        print(f"\n⏳ Taking a {BREAK_BETWEEN_ACCOUNTS} second break...")
                        time.sleep(BREAK_BETWEEN_ACCOUNTS)
                    
                except Exception as e:
                    print(f"❌ Error processing account @{account}: {e}")
                    continue
            
            # Save the session logs after processing the batch
            account_logger.save_session()
            
            # Log out after processing the batch
            bot.logout()
            
            # Take a longer break before the next batch (except for the last batch)
            if i + BATCH_SIZE < len(TARGET_ACCOUNTS) and daily_accounts < MAX_ACCOUNTS_PER_DAY:
                print(f"\n⏳ Taking a {BREAK_BETWEEN_BATCHES/60} minute break before next batch...")
                time.sleep(BREAK_BETWEEN_BATCHES)
                
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        raise
    finally:
        if 'bot' in locals():
            bot.driver.quit()
            print("\n🌐 Browser closed")
            
        # Print final statistics
        duration = datetime.now() - start_time
        print(f"\n📊 Session Summary:")
        print(f"  ⏱️ Duration: {duration}")
        print(f"  👥 Accounts processed: {daily_accounts}")
        print(f"  ❤️ Total actions: {daily_actions}")
        print(f"  📝 Logs saved to: logs/account_activity.json")


if __name__ == "__main__":
    main()
