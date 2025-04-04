from flask import Flask, request, jsonify, session
from flask_cors import CORS
import asyncio
import time
from datetime import datetime
import json
import jwt
from functools import wraps
import os
from collections import defaultdict

from src.crawlgpt.core.LLMBasedCrawler import Model
from src.crawlgpt.core.database import save_chat_message, get_chat_history, delete_user_chat_history, restore_chat_history
from src.crawlgpt.utils.monitoring import MetricsCollector, Metrics
from src.crawlgpt.utils.data_manager import DataManager
from src.crawlgpt.utils.content_validator import ContentValidator
from src.crawlgpt.ui.login import authenticate_user, create_user  # Assuming this function exists or can be adapted

app = Flask(__name__)
CORS(app)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key')  # For JWT token generation
TOKEN_EXPIRATION = 24 * 60 * 60  # 24 hours

# Initialize global components
model = Model()
data_manager = DataManager()
content_validator = ContentValidator()
metrics_collector = MetricsCollector()

# User sessions storage (in production, use Redis or a database)
user_sessions = {}


# Rate limiting configuration
RATE_LIMIT = 10  # requests per minute
rate_limit_data = defaultdict(list)  # stores timestamps of requests by user_id

# Rate limiter decorator for AI-intensive endpoints
def rate_limit(f):
    @wraps(f)
    def decorated(current_user_id, *args, **kwargs):
        # Get current time
        current_time = time.time()
        
        # Clean up old timestamps (older than 1 minute)
        rate_limit_data[current_user_id] = [
            t for t in rate_limit_data[current_user_id] 
            if current_time - t < 60
        ]
        
        # Check if user has exceeded rate limit
        if len(rate_limit_data[current_user_id]) >= RATE_LIMIT:
            response = jsonify({
                'success': False, 
                'message': 'Rate limit exceeded. Please try again later.'
            }), 429
            response[0].headers['X-RateLimit-Limit'] = str(RATE_LIMIT)
            response[0].headers['X-RateLimit-Remaining'] = '0'
            response[0].headers['X-RateLimit-Reset'] = str(int(min(rate_limit_data[current_user_id]) + 60))
            return response
        
        # Add current timestamp to user's requests
        rate_limit_data[current_user_id].append(current_time)
        
        # Process the request
        response = f(current_user_id, *args, **kwargs)
        
        # Add rate limit headers if response is a tuple (response, status_code)
        if isinstance(response, tuple) and len(response) >= 1:
            response[0].headers['X-RateLimit-Limit'] = str(RATE_LIMIT)
            response[0].headers['X-RateLimit-Remaining'] = str(RATE_LIMIT - len(rate_limit_data[current_user_id]))
            response[0].headers['X-RateLimit-Reset'] = str(int(current_time + 60))
        # If response is just a response object
        elif hasattr(response, 'headers'):
            response.headers['X-RateLimit-Limit'] = str(RATE_LIMIT)
            response.headers['X-RateLimit-Remaining'] = str(RATE_LIMIT - len(rate_limit_data[current_user_id]))
            response.headers['X-RateLimit-Reset'] = str(int(current_time + 60))
            
        return response
    
    return decorated

# Authentication decorator
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[1]
        
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        
        try:
            data = jwt.decode(token, app.secret_key, algorithms=["HS256"])
            current_user_id = data['user_id']
            
            # Initialize user session if not exists
            if current_user_id not in user_sessions:
                user_sessions[current_user_id] = {
                    'model': Model(),
                    'metrics': MetricsCollector(),
                    'url_processed': False
                }
        except:
            return jsonify({'message': 'Token is invalid!'}), 401
            
        return f(current_user_id, *args, **kwargs)
    return decorated

# Welcome endpoint
@app.route('/', methods=['GET'])
def welcome():
    return jsonify({'message': 'Welcome to the Crawlgpt API!'})

# USER REGISTRATION
@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')
    if not username or not password or not email:
        return jsonify({'message': 'Username, password and email are required!'}), 400
    # Check if user already exists
    existing_user = authenticate_user(username, password)
    if existing_user:
        return jsonify({'message': 'User already exists!'}), 400
    # Create user (adapt from your login.py)
    create_user(username, password, email)
    
    return jsonify({'message': 'User created successfully!'})
    

# Login endpoint
@app.route('/api/login', methods=['POST'])
def login():
    auth = request.json
    
    if not auth or not auth.get('username') or not auth.get('password'):
        return jsonify({'message': 'Could not verify'}), 401
    
    # Authenticate user (adapt from your login.py)
    user = authenticate_user(auth.get('username'), auth.get('password'))
    
    if not user:
        return jsonify({'message': 'Invalid credentials'}), 401
    
    # Generate JWT token
    token = jwt.encode({
        'user_id': user.id,
        'username': user.username,
        'exp': datetime.utcnow().timestamp() + TOKEN_EXPIRATION
    }, app.secret_key, algorithm="HS256")
    
    return jsonify({'token': token, 'user': {'id': user.id, 'username': user.username}})

# URL processing endpoint
@app.route('/api/process-url', methods=['POST'])
@token_required
@rate_limit
def process_url(current_user_id):
    data = request.json
    url = data.get('url')
    
    if not url or not url.strip():
        return jsonify({'success': False, 'message': 'Please enter a valid URL.'}), 400
    
    user_session = user_sessions[current_user_id]
    model = user_session['model']
    
    try:
        if not content_validator.is_valid_url(url):
            return jsonify({'success': False, 'message': 'Invalid URL format'}), 400
        
        # Create async task for extraction
        async def extract_content():
            start_time = time.time()
            
            try:
                success, msg = await model.extract_content_from_url(url)
                
                if success:
                    user_session['url_processed'] = True
                    user_session['metrics'].record_request(
                        success=True,
                        response_time=time.time() - start_time,
                        tokens_used=len(model.context.split())
                    )
                    
                    # Save system message about URL processing
                    save_chat_message(
                        current_user_id,
                        f"Content from {url} processed",
                        "system",
                        model.context
                    )
                    
                    return {'success': True, 'message': 'URL processed successfully'}
                else:
                    return {'success': False, 'message': msg}
                    
            except Exception as e:
                user_session['metrics'].record_request(
                    success=False,
                    response_time=time.time() - start_time,
                    tokens_used=0
                )
                return {'success': False, 'message': str(e)}
        
        # Using a more explicit approach to run the async function
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(extract_content())
        finally:
            loop.close()
        
        # Return the result
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'success': False, 'message': f"Error processing URL: {str(e)}"}), 500

# Chat endpoint
@app.route('/api/chat', methods=['POST'])
@token_required
@rate_limit
def chat_endpoint(current_user_id):
    data = request.json
    user_message = data.get('message')
    temperature = data.get('temperature', 0.7)
    max_tokens = data.get('max_tokens', 5000)
    model_id = data.get('model_id', 'llama-3.1-8b-instant')
    use_summary = data.get('use_summary', False)
    
    user_session = user_sessions[current_user_id]
    model = user_session['model']
    
    if not user_session['url_processed']:
        return jsonify({'success': False, 'message': 'Please process a URL first'}), 400
    
    try:
        start_time = time.time()
        
        # Save user message to database
        save_chat_message(
            current_user_id,
            user_message,
            "user",
            model.context
        )
        
        # Generate response
        response = model.generate_response(
            user_message,
            temperature,
            max_tokens,
            model_id,
            use_summary=use_summary
        )
        
        # Save assistant response to database
        save_chat_message(
            current_user_id,
            response,
            "assistant",
            model.context
        )
        
        # Record metrics
        user_session['metrics'].record_request(
            success=True,
            response_time=time.time() - start_time,
            tokens_used=len(response.split())
        )
        
        return jsonify({
            'success': True, 
            'response': response,
        })
        
    except Exception as e:
        user_session['metrics'].record_request(
            success=False,
            response_time=time.time() - start_time,
            tokens_used=0
        )
        return jsonify({'success': False, 'message': f"Error generating response: {str(e)}"}), 500

# Get chat history
@app.route('/api/chat/history', methods=['GET'])
@token_required
def get_history(current_user_id):
    try:
        # Load chat history from database
        history = get_chat_history(current_user_id)
        messages = [{
            "role": msg.role,
            "content": msg.message,
            "timestamp": msg.timestamp
        } for msg in history]
        
        return jsonify({'success': True, 'messages': messages})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f"Error fetching history: {str(e)}"}), 500

# Clear chat history
@app.route('/api/chat/clear', methods=['POST'])
@token_required
def clear_history(current_user_id):
    try:
        delete_user_chat_history(current_user_id)
        user_sessions[current_user_id]['url_processed'] = False
        return jsonify({'success': True, 'message': 'Chat history cleared'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f"Error clearing history: {str(e)}"}), 500

# Restore chat history and context
@app.route('/api/chat/restore', methods=['POST'])
@token_required
def restore_history(current_user_id):
    try:
        user_session = user_sessions[current_user_id]
        model = user_session['model']
        
        # Clear existing model state
        model.clear()
        
        # Load messages
        messages = restore_chat_history(current_user_id)
        
        # Rebuild model context from chat history
        context_parts = [
            msg.get('context') for msg in messages 
            if msg.get('context')
        ]
        model.context = "\n".join(context_parts)
        
        # Rebuild vector database from context
        if model.context:
            chunks = model.chunk_text(model.context)
            summaries = [model.summarizer.generate_summary(chunk) for chunk in chunks]
            model.database.add_data(chunks, summaries)
            user_session['url_processed'] = True
            
        return jsonify({'success': True, 'message': 'Full conversation state restored'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f"Restoration failed: {str(e)}"}), 500

# Get metrics
@app.route('/api/metrics', methods=['GET'])
@token_required
def get_metrics(current_user_id):
    try:
        user_session = user_sessions[current_user_id]
        metrics = user_session['metrics'].metrics.to_dict()
        return jsonify({'success': True, 'metrics': metrics})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f"Error fetching metrics: {str(e)}"}), 500

# Export data
@app.route('/api/export', methods=['GET'])
@token_required
def export_data(current_user_id):
    try:
        user_session = user_sessions[current_user_id]
        model = user_session['model']
        
        history = get_chat_history(current_user_id)
        messages = [{
            "role": msg.role,
            "content": msg.message,
            "context": msg.context,
            "timestamp": msg.timestamp
        } for msg in history]
        
        export_data = {
            "metrics": user_session['metrics'].metrics.to_dict(),
            "vector_database": model.database.to_dict(),
            "messages": messages
        }
        
        return jsonify({'success': True, 'data': export_data})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f"Export failed: {str(e)}"}), 500

# Import data
@app.route('/api/import', methods=['POST'])
@token_required
def import_data(current_user_id):
    try:
        user_session = user_sessions[current_user_id]
        model = user_session['model']
        
        imported_data = request.json.get('data')
        if not imported_data:
            return jsonify({'success': False, 'message': 'No data provided'}), 400
            
        # Validate imported data structure
        required_keys = ["metrics", "vector_database", "messages"]
        if not all(key in imported_data for key in required_keys):
            return jsonify({'success': False, 'message': 'Invalid backup file structure'}), 400
            
        # Import data with proper state management
        model.import_state(imported_data)
        
        # Delete existing chat history
        delete_user_chat_history(current_user_id)
        
        # Restore chat history and context from imported data
        if "messages" in imported_data:
            for msg in imported_data["messages"]:
                save_chat_message(
                    current_user_id,
                    msg["content"],
                    msg["role"],
                    msg.get("context", "")
                )
                
        # Set URL processed state if there's context
        if model.context:
            user_session['url_processed'] = True
        else:
            user_session['url_processed'] = False
            
        # Update metrics
        if "metrics" in imported_data:
            user_session['metrics'] = MetricsCollector()
            user_session['metrics'].metrics = Metrics.from_dict(imported_data["metrics"])
            
        return jsonify({'success': True, 'message': 'Data imported successfully'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f"Import failed: {str(e)}"}), 500

# Update settings
@app.route('/api/settings', methods=['POST'])
@token_required
def update_settings(current_user_id):
    data = request.json
    user_session = user_sessions[current_user_id]
    
    try:
        # Update any settings passed in the request
        if 'use_summary' in data:
            user_session['use_summary'] = data['use_summary']
            
        return jsonify({'success': True, 'message': 'Settings updated'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f"Error updating settings: {str(e)}"}), 500

# Clear all data
@app.route('/api/clear-all', methods=['POST'])
@token_required
def clear_all_data(current_user_id):
    try:
        user_session = user_sessions[current_user_id]
        model = user_session['model']
        
        model.clear()
        delete_user_chat_history(current_user_id)
        user_session['url_processed'] = False
        user_session['metrics'] = MetricsCollector()
        
        return jsonify({'success': True, 'message': 'All data cleared successfully'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f"Error clearing data: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True)