from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from my_ai import Lola 

app = Flask(__name__)

# Initialize the Brain ONCE
print(">> Initializing Lola for WhatsApp...")
bot = Lola()

@app.route('/whatsapp', methods=['POST'])
def whatsapp_reply():
    # --- FILTER 1: IGNORE STATUS UPDATES ---
    # Twilio sends "MessageStatus" updates (sent/delivered/read). 
    # We must ignore them, or the AI will reply to itself.
    if 'MessageStatus' in request.values:
        return "Status Ignored", 200

    # --- FILTER 2: GET DATA ---
    incoming_msg = request.values.get('Body', '').strip()
    sender_number = request.values.get('From', '')

    # --- FILTER 3: IGNORE EMPTY MESSAGES ---
    if not incoming_msg:
        print(f"[Skip] Empty message from {sender_number}")
        return "No Content", 200

    print(f"\n[WhatsApp] User: {sender_number} | Message: {incoming_msg}")

    # --- THE LOGIC ---
    try:
        # 1. Ask the AI
        ai_response = bot.run_cycle(incoming_msg)

        # 2. Package the response
        resp = MessagingResponse()
        msg = resp.message()
        msg.body(ai_response)
        
        return str(resp)

    except Exception as e:
        print(f"ERROR processing message: {e}")
        return str(MessagingResponse().message("My brain hurts. Try again."))

if __name__ == '__main__':
    # Threaded=True helps handle multiple requests at once
    app.run(port=5000, debug=True, threaded=True)