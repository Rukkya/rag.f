from flask import Flask, request, jsonify, url_for
from flask_cors import CORS
from flask_restx import Api, Resource, fields
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy
import os


app = Flask(__name__)
CORS(app)


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chats.db'  
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
@ns.route('/chats/')
class ChatList(Resource):
    @ns.doc('get_all_chats')
    def get(self):
        """Get all existing chats."""
        chats = Chat.query.all()  # Fetch all chats from the database
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

        # Create a new chat entry in the database
        new_chat = Chat(name=name, model=model)
        db.session.add(new_chat)
        db.session.commit()

        return {
            'id': new_chat.id,
            'name': new_chat.name,
            'model': new_chat.model,
            'url': request.host_url.strip('/') + f"/api/chats/{new_chat.id}"
        }, 201


@ns.route('/chats/<int:chat_id>/')
class ChatDetails(Resource):
    @ns.doc('get_chat_details')
    def get(self, chat_id):
        """Get details of a specific chat."""
        chat = Chat.query.get(chat_id)  # Query the chat by chat_id
        if not chat:
            return {'error': 'Chat not found'}, 404
        return {
            'id': chat.id,
            'name': chat.name,
            'model': chat.model
        }, 200

    @ns.doc('delete_chat')
    def delete(self, chat_id):
        """Delete a chat."""
        chat = Chat.query.get(chat_id)
        if not chat:
            return {'error': 'Chat not found'}, 404
        db.session.delete(chat)
        db.session.commit()
        return {'message': f'Chat {chat_id} deleted successfully'}, 200


@ns.route('/chats/<int:chat_id>/messages')
class ChatMessages(Resource):
    @ns.doc('send_message')
    @ns.expect(message_model)
    def post(self, chat_id):
        """Send a message to a chat."""
        chat = Chat.query.get(chat_id)  # Query the chat by chat_id
        if not chat:
            return {'error': 'Chat not found'}, 404

        data = request.json
        user_input = data.get('user_input')
        chat_model = data.get('chat_model')

        if not user_input or not chat_model:
            return {'error': 'User input and chat model are required'}, 400

        # Add the user's message to the chat
        new_message = Message(user_input=user_input, chat_id=chat_id)
        db.session.add(new_message)
        db.session.commit()

        # Mock a response message
        response_message = {'user': 'assistant', 'message': f"Processed message: {user_input}"}
        
        return {'response': response_message}, 200


@ns.route('/chats/<int:chat_id>/documents')
class DocumentUpload(Resource):
    @ns.doc('upload_document')
    def post(self, chat_id):
        """Upload a document for a specific chat."""
        chat = Chat.query.get(chat_id)  # Query the chat by chat_id
        if not chat:
            return {'error': 'Chat not found'}, 404

        file = request.files.get('file')
        if not file:
            return {'error': 'No file uploaded'}, 400

        filename = secure_filename(file.filename)
        file.save(os.path.join('uploads', filename))  # Save file in 'uploads/' directory

        
        new_document = Document(filename=filename, chat_id=chat_id)
        db.session.add(new_document)
        db.session.commit()

        return {'message': f'Document {filename} uploaded successfully'}, 200


@ns.route('/chats/<int:chat_id>/url')
class ShareChatURL(Resource):
    @ns.doc('get_chat_url')
    def get(self, chat_id):
        """Share the chat URL."""
        chat = Chat.query.get(chat_id)  
        if not chat:
            return {'error': 'Chat not found'}, 404

        return {'chat_url': request.host_url.strip('/') + f"/api/chats/{chat.id}"}, 200


if __name__ == '__main__':
    
    with app.app_context():
        db.create_all()
    
    os.makedirs('uploads', exist_ok=True)  
    app.run(debug=True)

