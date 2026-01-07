import sqlite3
import os
import sys
from datetime import datetime, timedelta

# Try to import the decoder library
try:
    from typedstream.stream import TypedStreamReader
except ImportError:
    print("Error: 'pytypedstream' not found.")
    print("Please run: pip3 install pytypedstream")
    sys.exit(1)

# --- CONFIGURATION ---
DB_PATH = os.path.expanduser("~/Library/Messages/chat.db")
BACKUP_DIR = "./backup"
MAC_EPOCH = datetime(2001, 1, 1)

def get_decoded_text(attributed_body_blob):
    """
    Decodes the binary 'attributedBody' column using pytypedstream.
    Returns the first text string found in the stream.
    """
    if not attributed_body_blob:
        return ""
    
    try:
        # Iterate through the stream events to find the text content
        for event in TypedStreamReader.from_data(attributed_body_blob):
            if isinstance(event, bytes):
                return event.decode("utf-8")
    except Exception as e:
        return f"[Error decoding message: {e}]"
    
    return "[Unable to decode message body]"

def format_date(mac_timestamp):
    """
    Converts Mac absolute time (nanoseconds since 2001-01-01) to readable string.
    """
    try:
        # Convert nanoseconds to seconds
        seconds = mac_timestamp / 1_000_000_000
        dt = MAC_EPOCH + timedelta(seconds=seconds)
        # Convert to local time (simplified logic)
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    except:
        return "Unknown Date"

def main():
    if not os.path.exists(DB_PATH):
        print(f"Could not find chat database at {DB_PATH}")
        return

    # Ensure backup directory exists
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("Fetching chat list...")
    
    # 1. Get all distinct chat GUIDs
    cursor.execute("SELECT distinct guid FROM chat")
    chats = cursor.fetchall()

    for row in chats:
        guid = row[0]
        
        # Parse the phone number/ID from the GUID (matches logic: arrIN=(${contact//;/ }))
        # Format usually: service;id;phone_number
        parts = guid.split(';')
        if len(parts) >= 3:
            contact_number = parts[2]
        else:
            contact_number = guid # Fallback if format is different

        # Create contact folder
        contact_dir = os.path.join(BACKUP_DIR, contact_number)
        if not os.path.exists(contact_dir):
            os.makedirs(contact_dir)

        output_file = os.path.join(contact_dir, f"{guid}.txt")
        print(f"Processing: {guid} -> {output_file}")

        # 2. Get messages for this specific chat
        # We join chat -> chat_handle_join -> message
        query = """
        SELECT 
            message.is_from_me,
            message.text,
            message.attributedBody,
            message.date
        FROM message 
        JOIN chat_message_join ON message.ROWID = chat_message_join.message_id 
        JOIN chat ON chat_message_join.chat_id = chat.ROWID 
        WHERE chat.guid = ?
        ORDER BY message.date ASC
        """
        
        cursor.execute(query, (guid,))
        messages = cursor.fetchall()

        with open(output_file, 'w', encoding='utf-8') as f:
            for is_from_me, text, attributed_body, date_val in messages:
                
                # SENDER LOGIC
                sender = "Me: " if is_from_me == 1 else "Friend: "
                
                # DATE LOGIC
                date_str = format_date(date_val)
                
                # TEXT RECOVERY LOGIC
                final_text = text
                if final_text is None:
                    # If text column is null, try decoding the blob
                    final_text = get_decoded_text(attributed_body)
                
                # Cleanup: Ensure text is a string and handle None edge cases
                if final_text is None: 
                    final_text = "<Empty Message>"

                # Remove newlines for cleaner one-line output (optional, matches sed logic)
                final_text = final_text.replace('\n', ' ')

                # Write to file
                f.write(f"{sender}{final_text} | {date_str}\n")

    conn.close()
    print("Backup complete.")

if __name__ == "__main__":
    main()