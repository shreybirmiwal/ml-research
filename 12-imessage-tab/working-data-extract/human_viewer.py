import json
import os

# --- CONFIGURATION ---
INPUT_FILE = "data/imessage_export.jsonl"
OUTPUT_FILE = "data/readable_chat.txt"

def main():
    if not os.path.exists(INPUT_FILE):
        print(f"Error: Could not find '{INPUT_FILE}'. Make sure you ran the previous script first.")
        return

    print(f"Converting {INPUT_FILE} to {OUTPUT_FILE}...")

    with open(INPUT_FILE, 'r', encoding='utf-8') as infile, \
         open(OUTPUT_FILE, 'w', encoding='utf-8') as outfile:
        
        conversation_count = 0
        
        for line in infile:
            if not line.strip():
                continue

            conversation_count += 1
            try:
                data = json.loads(line)
                messages = data.get("messages", [])
                
                # Write a nice header for each conversation
                header = f"\n{'='*30} CONVERSATION {conversation_count} {'='*30}\n"
                outfile.write(header)
                
                # Write the messages
                for msg in messages:
                    role = msg.get("role", "unknown")
                    text = msg.get("text", "")
                    
                    # Formatting: "Me" aligns left, "Other" indented slightly for readability
                    if role == "me":
                        outfile.write(f"[Me]:    {text}\n")
                    else:
                        outfile.write(f"[Other]: {text}\n")
                
                # Add some spacing before the next one
                outfile.write("\n")

            except json.JSONDecodeError:
                print(f"Skipping invalid line: {line[:50]}...")

    print(f"Done! Saved {conversation_count} conversations to '{OUTPUT_FILE}'.")

if __name__ == "__main__":
    main()