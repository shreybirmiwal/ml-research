import sqlite3
import os
import json

def fetch_chats_separated_by_thread():
    db_path = os.path.expanduser("~/Library/Messages/chat.db")
    output_file = "imessage_threads_separated.jsonl"

    if not os.path.exists(db_path):
        print(f"Error: Could not find database at {db_path}")
        return

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # 1. Get all unique Chats (Threads)
        # This includes both DMs and Group Chats, each has a unique ROWID.
        cursor.execute("SELECT ROWID, chat_identifier, display_name FROM chat")
        chats = cursor.fetchall()
        
        print(f"Found {len(chats)} unique conversation threads. Processing...")

        with open(output_file, 'w', encoding='utf-8') as f:
            count = 0
            
            for chat_id, chat_guid, chat_name in chats:
                
                # 2. JOIN tables to get messages SPECIFIC to this chat_id
                # We join:
                # chat_message_join -> links the chat to the message
                # message -> gets the text
                # handle -> gets the sender info (so we know who sent what in a group chat)
                query = """
                SELECT 
                    message.is_from_me, 
                    message.text,
                    handle.id as sender_handle
                FROM 
                    chat_message_join
                JOIN 
                    message ON chat_message_join.message_id = message.ROWID
                LEFT JOIN 
                    handle ON message.handle_id = handle.ROWID
                WHERE 
                    chat_message_join.chat_id = ?
                    AND message.text IS NOT NULL 
                    AND message.associated_message_type = 0
                ORDER BY 
                    message.date ASC
                """
                
                cursor.execute(query, (chat_id,))
                messages = cursor.fetchall()

                if not messages:
                    continue

                # 3. Build the conversation log
                full_conversation = []
                
                # We collect participants to help you identify the chat in the JSON later
                participants = set()

                for is_from_me, text, sender_handle in messages:
                    clean_text = text.replace('\ufffc', '[Attachment]').replace('\n', ' ')
                    
                    if is_from_me == 1:
                        # You sent it
                        line = f"<|me|>: {clean_text}"
                    else:
                        # Someone else sent it. 
                        # If sender_handle is None, it might be a system message, but usually it's a friend.
                        sender_id = sender_handle if sender_handle else "Unknown"
                        participants.add(sender_id)
                        
                        # We include the sender_id so you can distinguish people in Group Chats
                        # e.g., <|friend: +1555...|>: Hello
                        line = f"<|friend: {sender_id}|>: {clean_text}"
                    
                    full_conversation.append(line)

                # 4. Construct JSON Entry
                # We determine if it's a Group Chat roughly by checking if there are multiple 'friend' senders
                # (Note: This is a loose check; 1-on-1 chats only have 1 other participant)
                is_group_chat = len(participants) > 1

                json_entry = {
                    "chat_id": chat_id,
                    "chat_guid": chat_guid, # This is the iMessage identifier (e.g., 'chat12345...')
                    "chat_name": chat_name, # Often None for DMs, but has values for named Group Chats
                    "participants": list(participants),
                    "is_group_chat": is_group_chat,
                    "message_count": len(messages),
                    "text": "\n".join(full_conversation)
                }

                f.write(json.dumps(json_entry, ensure_ascii=False) + "\n")
                count += 1
        
        print(f"\nSuccess! Exported {count} separated threads to '{output_file}'")

    except sqlite3.OperationalError as e:
        print("\nError: Unable to access the database.")
        print(f"Details: {e}")
        print("REMINDER: Ensure Terminal has Full Disk Access.")
    
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    fetch_chats_separated_by_thread()