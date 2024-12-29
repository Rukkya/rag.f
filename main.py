import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_restx import Api, Resource, fields
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO, emit
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from database import db_manager

# Load environment variables from the .env file
load_dotenv()

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")  # Enable WebSocket support

# Ensure the database and uploads directory exist
db_directory = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'data')
uploads_dir = os.path.join(os.path.dirname(__file__), 'uploads')

if not os.path.exists(db_directory):
    os.makedirs(db_directory)

os.makedirs(uploads_dir, exist_ok=True)  # Ensure 'uploads' folder exists

# PostgreSQL database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://rokia:123@localhost/rag'  
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

api = Api(app, version='1.0', title='Chat API', description='API for managing chats and documents')
ns = api.namespace('api', description='Chat-related operations')

# Define the Chat model
class Chat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    model = db.Column(db.String(100), nullable=False)
    messages = db.relationship('Message', backref='chat', lazy=True)
    documents = db.relationship('Document', backref='chat', lazy=True)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_input = db.Column(db.String(255), nullable=False)
    chat_id = db.Column(db.Integer, db.ForeignKey('chat.id'), nullable=False)

class Document(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(100), nullable=False)
    chat_id = db.Column(db.Integer, db.ForeignKey('chat.id'), nullable=False)

# Swagger Models
chat_model = ns.model('Chat', {
    'name': fields.String(required=True, description='Name of the chat'),
    'model': fields.String(required=True, description='Model used for the chat'),
})

message_model = ns.model('Message', {
    'user_input': fields.String(required=True, description='User input message'),
    'chat_model': fields.String(required=True, description='Chat model name'),
})

# Endpoint to create and manage chats
@ns.route('/chats/<int:chat_id>')
class ChatDetail(Resource):
    @ns.doc('get_chat_by_id')
    def get(self, chat_id):
        """Get a specific chat by ID."""
        chat = Chat.query.get(chat_id)
        if not chat:
            return {'error': 'Chat not found'}, 404
        return {'id': chat.id, 'name': chat.name, 'model': chat.model}, 200
        
    @ns.doc('delete_chat')
    def delete(self, chat_id):
        """Delete a specific chat by ID."""
        chat = Chat.query.get(chat_id)
        if not chat:
            return {'error': 'Chat not found'}, 404
        
        # Delete related messages and documents
        Message.query.filter_by(chat_id=chat_id).delete()
        Document.query.filter_by(chat_id=chat_id).delete()
        
        # Commit the changes to delete related records
        db.session.commit()

        # Now delete the chat itself
        db.session.delete(chat)
        db.session.commit()

        return {'message': f'Chat {chat_id} and its associated messages and documents deleted successfully'}, 200


@ns.route('/chats/<int:chat_id>/messages')
class ChatMessages(Resource):
    @ns.doc('send_message')
    @ns.expect(message_model)
    def post(self, chat_id):
        """Send a message to a chat."""
        chat = Chat.query.get(chat_id)
        if not chat:
            return {'error': 'Chat not found'}, 404

        data = request.json
        user_input = data.get('user_input')
        chat_model = data.get('chat_model')

        if not user_input or not chat_model:
            return {'error': 'User input and chat model are required'}, 400

        new_message = Message(user_input=user_input, chat_id=chat_id)
        db.session.add(new_message)
        db.session.commit()

        # Mock a response message
        response_message = f"Processed message: {user_input}"

        # Emit the response to the WebSocket for real-time updates
        socketio.emit('new_message', {'chat_id': chat_id, 'user_input': user_input, 'response': response_message}, namespace='/ws')

        return {'response': response_message}, 200

    @ns.doc('get_messages')
    def get(self, chat_id):
        """Get all messages for a specific chat."""
        chat = Chat.query.get(chat_id)
        if not chat:
            return {'error': 'Chat not found'}, 404

        # Fetch all messages for the chat
        messages = Message.query.filter_by(chat_id=chat_id).all()
        return [
            {'user_input': msg.user_input, 'response': f"Processed: {msg.user_input}"}
            for msg in messages
        ], 200


# WebSocket namespace
@socketio.on('connect', namespace='/ws')
def handle_connect():
    """Handle a WebSocket connection."""
    print("Client connected to WebSocket")

@socketio.on('disconnect', namespace='/ws')
def handle_disconnect():
    """Handle a WebSocket disconnection."""
    print("Client disconnected from WebSocket")

@ns.route('/chats/<int:chat_id>/documents')
class DocumentUpload(Resource):
    @ns.doc('upload_document')
    def post(self, chat_id):
        """Upload a document for a specific chat."""
        chat = Chat.query.get(chat_id)
        if not chat:
            return {'error': 'Chat not found'}, 404

        file = request.files.get('file')
        if not file:
            return {'error': 'No file uploaded'}, 400

        # Check file extension (basic validation for PDF, DOCX, TXT)
        allowed_extensions = ['pdf', 'docx', 'txt']
        file_extension = file.filename.split('.')[-1].lower()

        if file_extension not in allowed_extensions:
            return {'error': 'Invalid file type. Only PDF, DOCX, and TXT are allowed.'}, 400

        filename = secure_filename(file.filename)
        file_path = os.path.join(uploads_dir, filename)
        file.save(file_path)

        new_document = Document(filename=filename, chat_id=chat_id)
        db.session.add(new_document)
        db.session.commit()

        return {'message': f'Document {filename} uploaded successfully'}, 200

@ns.route('/chats/')
class ChatList(Resource):
    @ns.doc('get_all_chats')
    def get(self):
        """Get all existing chats."""
        chats = Chat.query.all()
        return [{'id': chat.id, 'name': chat.name, 'model': chat.model} for chat in chats], 200

    @ns.expect(chat_model)
    @ns.doc('create_chat')
    def post(self):
        """Create a new chat."""
        data = request.json
        name = data.get('name')
        model = data.get('model')

        if not name or not model:
            return {'error': 'Chat name and model are required'}, 400

        new_chat = Chat(name=name, model=model)
        db.session.add(new_chat)
        db.session.commit()

        # Return the created chat with its unique chat_id
        return {
            'id': new_chat.id,  # The unique chat ID generated by PostgreSQL
            'name': new_chat.name,
            'model': new_chat.model,
            'url': request.host_url.strip('/') + f"/api/chats/{new_chat.id}"  # URL to access this chat
        }, 201


if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Ensure the RAGAPP database tables are created
    socketio.run(app, debug=True)

