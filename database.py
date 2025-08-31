import sqlite3
import datetime

def init_db():
    conn = sqlite3.connect('chatbot.db')
    c = conn.cursor()
    
    # Create table for conversation logs
    c.execute('''CREATE TABLE IF NOT EXISTS conversations
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  session_id TEXT,
                  user_input TEXT,
                  bot_response TEXT,
                  timestamp DATETIME)''')
    
    # Create table for FAQ knowledge base
    c.execute('''CREATE TABLE IF NOT EXISTS faqs
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  question TEXT,
                  answer TEXT)''')
    
    # Insert some sample FAQs
    sample_faqs = [
        ("What are your operating hours?", "We're open from 9 AM to 6 PM, Monday to Friday."),
        ("Where are you located?", "Our main office is at 123 Tech Street, Innovation City."),
        ("How can I contact support?", "You can reach our support team at support@company.com or call 555-0123."),
        ("What products do you offer?", "We offer a range of AI solutions including chatbots, predictive analytics, and computer vision systems."),
        ("Do you offer refunds?", "Yes, we offer a 30-day money-back guarantee on all our products.")
    ]
    
    c.execute("SELECT COUNT(*) FROM faqs")
    if c.fetchone()[0] == 0:
        c.executemany("INSERT INTO faqs (question, answer) VALUES (?, ?)", sample_faqs)
    
    conn.commit()
    conn.close()

def log_conversation(session_id, user_input, bot_response):
    conn = sqlite3.connect('chatbot.db')
    c = conn.cursor()
    timestamp = datetime.datetime.now()
    
    c.execute("INSERT INTO conversations (session_id, user_input, bot_response, timestamp) VALUES (?, ?, ?, ?)",
              (session_id, user_input, bot_response, timestamp))
    
    conn.commit()
    conn.close()

def get_conversation_history(session_id, limit=5):
    conn = sqlite3.connect('chatbot.db')
    c = conn.cursor()
    
    c.execute("SELECT user_input, bot_response FROM conversations WHERE session_id = ? ORDER BY timestamp DESC LIMIT ?",
              (session_id, limit))
    
    history = c.fetchall()
    conn.close()
    
    # Return in chronological order
    return [(row[0], row[1]) for row in reversed(history)]
