"""
Logger for tracking Instagram account activities
"""
import os
import json
from datetime import datetime
from .logger import log_error, log_success

class AccountLogger:
    def __init__(self):
        self.logs_dir = "logs"
        self.accounts_log_file = os.path.join(self.logs_dir, "accounts_activity.json")
        self.ensure_logs_directory()
        self.current_session = {
            "start_time": datetime.now().isoformat(),
            "accounts": {}
        }
        # Load existing logs if any
        self.load_existing_logs()

    def ensure_logs_directory(self):
        """Ensure the logs directory exists"""
        if not os.path.exists(self.logs_dir):
            os.makedirs(self.logs_dir)

    def load_existing_logs(self):
        """Load existing logs from file"""
        try:
            if os.path.exists(self.accounts_log_file):
                with open(self.accounts_log_file, 'r') as f:
                    self.existing_logs = json.load(f)
            else:
                self.existing_logs = []
        except Exception as e:
            print(f"❌ Error loading existing logs: {e}")
            self.existing_logs = []

    def log_account_activity(self, username, stats):
        """Log activity for a specific account"""
        # Update the current session with new account data
        self.current_session["accounts"][username] = {
            "timestamp": datetime.now().isoformat(),
            "stats": stats
        }

    def save_session(self):
        """Save the current session to file"""
        try:
            # Add current session to logs
            self.existing_logs.append(self.current_session)
            
            # Save all logs
            with open(self.accounts_log_file, 'w') as f:
                json.dump(self.existing_logs, f, indent=2)
            
            # Reset current session for next batch
            self.current_session = {
                "start_time": datetime.now().isoformat(),
                "accounts": {}
            }
            
        except Exception as e:
            log_error(f"Error saving account logs: {str(e)}")

    def get_account_stats(self, username):
        """Get statistics for a specific account"""
        if os.path.exists(self.accounts_log_file):
            with open(self.accounts_log_file, 'r') as f:
                logs = json.load(f)
                for session in logs:
                    if username in session["accounts"]:
                        return session["accounts"][username]["stats"]
        return None 