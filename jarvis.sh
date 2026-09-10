#!/bin/bash

SERVER_URL="https://jarvis-backend-cx62.onrender.com"
AUDIO_FILE="input.wav"
HISTORY_FILE="history.json"

# Initialize history file if it doesn't exist
if [ ! -f "$HISTORY_FILE" ]; then
    echo "[]" > "$HISTORY_FILE"
fi

echo "=========================================="
echo "         JARVIS VOICE CLIENT ONLINE       "
echo "=========================================="

while true; do
    echo ""
    echo "Listening... (Press ENTER when done speaking)"
    
    # Record audio until user presses Enter
    termux-microphone-record -f $AUDIO_FILE -r 16000 -c 1 &
    REC_PID=$!
    read -r
    termux-microphone-record -q
    
    echo "Transcribing audio..."
    
    # Send audio to /transcribe endpoint
    STT_RESPONSE=$(curl -s -X POST "$SERVER_URL/transcribe" \
      -F "file=@$AUDIO_FILE;type=audio/wav")
    
    USER_TEXT=$(echo "$STT_RESPONSE" | jq -r '.text // empty')
    
    if [ -z "$USER_TEXT" ]; then
        echo "Could not catch that. Try speaking again."
        rm -f $AUDIO_FILE
        continue
    fi
    
    echo "You: $USER_TEXT"
    
    # Check for exit command
    if [[ "$USER_TEXT" =~ "exit" || "$USER_TEXT" =~ "quit" || "$USER_TEXT" =~ "goodbye" ]]; then
        termux-tts-speak "Goodbye!"
        break
    fi
    
    echo "JARVIS thinking..."
    
    # Build payload with conversation history
    HISTORY=$(cat "$HISTORY_FILE")
    PAYLOAD=$(jq -n --arg msg "$USER_TEXT" --argjson hist "$HISTORY" \
      '{message: $msg, history: $hist}')
    
    # Send request to /chat endpoint
    CHAT_RESPONSE=$(curl -s -X POST "$SERVER_URL/chat" \
      -H "Content-Type: application/json" \
      -d "$PAYLOAD")
    
    JARVIS_REPLY=$(echo "$CHAT_RESPONSE" | jq -r '.reply // empty')
    
    if [ -n "$JARVIS_REPLY" ]; then
        echo "JARVIS: $JARVIS_REPLY"
        
        # Speak response using Android TTS
        termux-tts-speak "$JARVIS_REPLY"
        
        # Update short-term memory (keep last 6 turns)
        NEW_HISTORY=$(echo "$HISTORY" | jq --arg u "$USER_TEXT" --arg a "$JARVIS_REPLY" \
          '. + [{"role": "user", "content": $u}, {"role": "assistant", "content": $a}] | .[-6:]')
        echo "$NEW_HISTORY" > "$HISTORY_FILE"
    else
        echo "Error getting response from JARVIS server."
    fi
    
    rm -f $AUDIO_FILE
done
