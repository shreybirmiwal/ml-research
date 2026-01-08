import json
import random
import re
from pathlib import Path

# --- CONFIGURATION ---
INPUT_FILE = "data/imessage_export.jsonl"
OUTPUT_DIR = "data/"

# --- TOKENS ---
# These act as cues for the model. 
# When you run inference, you will feed it the history + "<|me|>:" to trigger completion.
TOKEN_ME = "<|me|>"
TOKEN_OTHER = "<|other|>"

# Regex to remove iMessage reactions (Tapbacks)
# These are noise for text prediction.
TAPBACK_PATTERNS = [
    r'^Loved “.*”$',
    r'^Liked “.*”$',
    r'^Disliked “.*”$',
    r'^Laughed at “.*”$',
    r'^Emphasized “.*”$',
    r'^Questioned “.*”$'
]

def is_tapback(text):
    """Returns True if the text is just an iMessage reaction."""
    if not text: 
        return True
    for pattern in TAPBACK_PATTERNS:
        if re.match(pattern, text.strip()):
            return True

    if text.strip() == "":
        return True

    if "reacted" in text.lower():
        return True

    return False

def format_conversation(messages):
    """
    Flattens a list of message dicts into a single string.
    
    Input: [{"role": "other", "text": "Hi"}, {"role": "me", "text": "Yo"}]
    Output: "<|other|>: Hi\n<|me|>: Yo"
    """
    conversation_string = ""
    
    for msg in messages:
        role = msg.get('role')
        text = msg.get('text', "")
        
        # Skip empty messages or tapbacks
        if is_tapback(text):
            continue
            
        prefix = TOKEN_ME if role == "me" else TOKEN_OTHER
        
        # We append a newline after every message to separate turns
        conversation_string += f"{prefix}: {text}\n"
        
    return conversation_string.strip()

def main():
    input_path = Path(INPUT_FILE)
    output_path = Path(OUTPUT_DIR)
    
    if not input_path.exists():
        print(f"Error: Could not find {INPUT_FILE}")
        return

    # Create output directory if it doesn't exist
    output_path.mkdir(parents=True, exist_ok=True)
    
    valid_samples = []
    
    print(f"Processing {input_path}...")
    
    with open(input_path, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f):
            try:
                data = json.loads(line)
                messages = data.get('messages', [])
                
                # We need at least 2 turns (context -> response) for it to be useful training data
                if len(messages) < 2:
                    continue
                
                formatted_text = format_conversation(messages)
                
                # If filtering removed everything (e.g. a convo of just likes), skip it
                if not formatted_text:
                    continue
                
                entry = {
                    "text": formatted_text
                }
                valid_samples.append(entry)
                
            except json.JSONDecodeError:
                print(f"Skipping bad JSON on line {line_num}")
                continue

    # --- SPLIT & SAVE ---
    random.shuffle(valid_samples)
    
    print(f"Total Conversations: {len(valid_samples)}")
    
    with open(output_path / "train.jsonl", 'w', encoding='utf-8') as f:
        for item in valid_samples:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")

    print(f"\nSuccess! Data ready in '{OUTPUT_DIR}'")
    
if __name__ == "__main__":
    main()