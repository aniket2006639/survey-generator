from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import openai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)  # Allow cross-origin requests for frontend access

# Configure OpenAI
api_key = os.getenv('OPENAI_API_KEY')
DEMO_MODE = True  # Set to True to use demo mode without API key

if not api_key and not DEMO_MODE:
    print("Warning: OPENAI_API_KEY not found in environment variables!")
elif not DEMO_MODE:
    print(f"API key loaded successfully (starts with: {api_key[:7]}...)")
else:
    print("Running in DEMO MODE - no API key required")

# Set the API key for the openai package if not in demo mode
if not DEMO_MODE:
    openai.api_key = api_key

@app.route('/')
def home():
    return send_file('index.html')

@app.route('/generate_questions', methods=['POST'])
def generate_questions():
    data = request.get_json()
    topic = data.get('topic', '')
    
    if not topic:
        return jsonify({"error": "No topic provided"}), 400
    
    if DEMO_MODE:
        # Generate demo questions without using OpenAI
        demo_questions = [
            f"What are the most significant developments in {topic} technology in recent years?",
            f"How do you think {topic} will evolve in the next decade?",
            f"What are the biggest challenges facing the {topic} industry today?",
            f"How has {topic} impacted society and daily life?"
        ]
        return jsonify({"questions": demo_questions})
    
    try:
        print(f"Attempting to generate questions about: {topic}")
        # Using OpenAI to generate questions
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that generates engaging questions about a given topic."},
                {"role": "user", "content": f"Generate 4 thought-provoking questions about {topic}. Return only the questions, one per line."}
            ],
            temperature=0.7
        )
        
        # Extract questions from the response
        questions = response.choices[0].message.content.strip().split('\n')
        print(f"Successfully generated {len(questions)} questions")
        return jsonify({"questions": questions})
    
    except openai.error.AuthenticationError as e:
        print(f"Authentication Error: {str(e)}")
        return jsonify({"error": "Invalid API key. Please check your OpenAI API key."}), 500
    except Exception as e:
        print(f"Error generating questions: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
