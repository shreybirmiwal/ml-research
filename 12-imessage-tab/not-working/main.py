import sqlite3
import os
import sys

def fetch_sent_imessages():
    db_path = os.path.expanduser("~/Library/Messages/chat.db")

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # is_from_me = 1             -> Only messages sent by you
        # text IS NOT NULL           -> Exclude empty messages (like purely image attachments)
        # associated_message_type = 0 -> Exclude reactions/tapbacks (which have types > 0)
        query = """
        SELECT text 
        FROM message 
        WHERE is_from_me = 1 
          AND text IS NOT NULL 
          AND associated_message_type = 0
        ORDER BY date DESC
        """

        cursor.execute(query)
        messages = cursor.fetchall()

        if not messages:
            print("No messages found (or permission denied).")
        
        print(f"--- Found {len(messages)} sent messages ---")
        for msg in messages:
            # msg is a tuple, so we access the first element
            print(msg[0])

    except sqlite3.OperationalError as e:
        print("Error: Unable to access the database.")
        print(f"Details: {e}")
        print("\nFix: Ensure your Terminal app has 'Full Disk Access' in System Settings.")
    
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    fetch_sent_imessages()