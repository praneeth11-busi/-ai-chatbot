from flask import Flask, render_template, request, jsonify, session
import uuid
from chatbot import ChatBot
from database import init_db, log_conversation, get_conversation_history

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Change this in production

# Initialize database and chatbot
init_db()
chatbot = ChatBot()

@app.before_request
def make_session_permanent():
    # Generate a unique session ID if it doesn't exist
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/get_response', methods=['POST'])
def get_response():
    user_input = request.json['user_input']
    session_id = session['session_id']
    
    # Get response from chatbot
    bot_response = chatbot.response(user_input, session_id)
    
    # Log the conversation
    log_conversation(session_id, user_input, bot_response)
    
    return jsonify({'response': bot_response})

@app.route('/get_history', methods=['GET'])
def get_history():
    session_id = session['session_id']
    history = get_conversation_history(session_id)
    return jsonify({'history': history})

if __name__ == '__main__':
    app.run(debug=True)
