import sqlite3
import os
import sys
import json
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
OUTPUT_FILE = "data/imessage_export.jsonl"
MAC_EPOCH = datetime(2001, 1, 1)

# LOGIC: If messages are more than X hours apart, split into a new conversation object
GAP_THRESHOLD_HOURS = 6 

def get_decoded_text(attributed_body_blob):
    """
    Decodes the binary 'attributedBody' column using pytypedstream.
    """
    if not attributed_body_blob:
        return ""
    try:
        for event in TypedStreamReader.from_data(attributed_body_blob):
            if isinstance(event, bytes):
                return event.decode("utf-8")
    except Exception:
        return ""
    return ""

def mac_time_to_datetime(mac_timestamp):
    """
    Converts Mac absolute time (nanoseconds) to a python datetime object.
    Returns None if timestamp is invalid.
    """
    if mac_timestamp is None:
        return None
    try:
        seconds = mac_timestamp / 1_000_000_000
        return MAC_EPOCH + timedelta(seconds=seconds)
    except:
        return None

def write_conversation(file_handle, chat_guid, messages):
    """
    Writes a single conversation block to the JSONL file.
    """
    if not messages:
        return

    # Create the conversation object
    conversation_data = {

        "messages": messages
    }

    # Dump as a single JSON line
    file_handle.write(json.dumps(conversation_data, ensure_ascii=False) + "\n")

def main():
    if not os.path.exists(DB_PATH):
        print(f"Could not find chat database at {DB_PATH}")
        return

    print(f"Reading from: {DB_PATH}")
    print(f"Writing to:   {os.path.abspath(OUTPUT_FILE)}")
    print(f"Splitting conversations after {GAP_THRESHOLD_HOURS} hours of inactivity.")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 1. Get all chat GUIDs
    cursor.execute("SELECT distinct guid FROM chat")
    chats = cursor.fetchall()
    
    total_convos = 0

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        
        for i, row in enumerate(chats):
            guid = row[0]
            
            # Progress indicator
            print(f"[{i+1}/{len(chats)}] Processing {guid}...", end='\r')

            # 2. Get messages for this specific chat
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
            raw_messages = cursor.fetchall()

            current_conversation_msgs = []
            last_msg_datetime = None

            for is_from_me, text, attributed_body, date_val in raw_messages:
                
                # --- DATA CLEANING ---
                msg_datetime = mac_time_to_datetime(date_val)
                if not msg_datetime:
                    continue # Skip messages with bad dates

                final_text = text
                if final_text is None:
                    final_text = get_decoded_text(attributed_body)
                
                if final_text is None:
                    final_text = ""

                # Format for JSON
                message_obj = {
                    "role": "me" if is_from_me == 1 else "other",
                    "text": final_text.strip(),
                }

                # --- SPLIT LOGIC ---
                # If this is the first message, or the gap is too large, 
                # we consider the PREVIOUS buffer finished.
                if last_msg_datetime:
                    time_diff = msg_datetime - last_msg_datetime
                    if time_diff > timedelta(hours=GAP_THRESHOLD_HOURS):
                        # Flush the previous buffer to file
                        write_conversation(f, guid, current_conversation_msgs)
                        total_convos += 1
                        current_conversation_msgs = [] # Reset

                current_conversation_msgs.append(message_obj)
                last_msg_datetime = msg_datetime

            # Flush any remaining messages after the loop finishes
            if current_conversation_msgs:
                write_conversation(f, guid, current_conversation_msgs)
                total_convos += 1

    conn.close()
    print(f"\n\nDone! Extracted {total_convos} conversations to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()