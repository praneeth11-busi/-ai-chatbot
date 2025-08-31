import nltk
import random
import string
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import sqlite3

# Download required NLTK data
nltk.download('punkt', quiet=True)
nltk.download('wordnet', quiet=True)

class ChatBot:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(tokenizer=self.lem_tokens, stop_words='english')
        self.sent_tokens = []
        self.setup_knowledge_base()
        
    def setup_knowledge_base(self):
        # Get FAQs from database
        conn = sqlite3.connect('chatbot.db')
        c = conn.cursor()
        c.execute("SELECT question, answer FROM faqs")
        faqs = c.fetchall()
        conn.close()
        
        # Prepare knowledge base
        self.question_answer = {}
        for question, answer in faqs:
            self.sent_tokens.append(question)
            self.question_answer[question] = answer
        
        # Add some general responses
        self.general_responses = {
            'greeting': [
                "Hello! How can I help you today?",
                "Hi there! What can I assist you with?",
                "Greetings! How may I be of service?"
            ],
            'thanks': [
                "You're welcome!",
                "Happy to help!",
                "Anytime! Let me know if you need anything else."
            ],
            'goodbye': [
                "Goodbye! Have a great day!",
                "See you later!",
                "Bye! Come back if you have more questions."
            ],
            'default': [
                "I'm not sure I understand. Could you rephrase that?",
                "Interesting question. Could you provide more details?",
                "I'm still learning. Could you ask in a different way?"
            ]
        }
        
        # Train the vectorizer
        if self.sent_tokens:
            self.vectorizer.fit_transform(self.sent_tokens)
    
    def lem_tokens(self, tokens):
        lemmer = nltk.stem.WordNetLemmatizer()
        return [lemmer.lemmatize(token) for token in tokens]
    
    def normalize_text(self, text):
        remove_punct_dict = dict((ord(punct), None) for punct in string.punctuation)
        return nltk.word_tokenize(text.lower().translate(remove_punct_dict))
    
    def response(self, user_input, session_id):
        # Check for general phrases first
        lowered = user_input.lower()
        
        if any(word in lowered for word in ['hello', 'hi', 'hey', 'hola']):
            return random.choice(self.general_responses['greeting'])
        
        if any(word in lowered for word in ['thank', 'thanks', 'appreciate']):
            return random.choice(self.general_responses['thanks'])
        
        if any(word in lowered for word in ['bye', 'goodbye', 'see you', 'farewell']):
            return random.choice(self.general_responses['goodbye'])
        
        # Process for FAQ matching
        if self.sent_tokens:
            user_input_processed = self.vectorizer.transform([user_input])
            knowledge_vectors = self.vectorizer.transform(self.sent_tokens)
            
            similarities = cosine_similarity(user_input_processed, knowledge_vectors)
            idx = similarities.argsort()[0][-1]
            
            if similarities[0][idx] > 0.3:  # Similarity threshold
                matched_question = self.sent_tokens[idx]
                return self.question_answer[matched_question]
        
        # Fallback response
        return random.choice(self.general_responses['default'])
