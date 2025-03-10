from flask import Flask, request
from flask_restful import Resource, Api
from pymongo import MongoClient
import secrets

app = Flask(__name__)
api = Api(app)

client = MongoClient("")
db = client.get_database('mail_db')
mailboxes = db.mailboxes


class Mailbox(Resource):
    def put(self):
        mailbox = {
            "name": secrets.token_hex(5),
            "token": secrets.token_hex(16),
            "messages": []
        }
        result = mailboxes.insert_one(mailbox)
        # Update the mailbox object with the string version of ObjectId
        mailbox["_id"] = str(result.inserted_id)
        return {'success': True, 'errors': None, 'result': mailbox}, 200

    def delete(self, name):
        result = mailboxes.delete_one({"name": name})
        if result.deleted_count == 0:
            return {'success': False, 'errors': [{'code': 404, 'message': 'Not Found', 'detail': 'Not Found'}],
                    'result': False}, 404
        return {'success': True, 'errors': None, 'result': True}, 200

    def get(self, name):
        mailbox = mailboxes.find_one({"name": name})
        if mailbox is None:
            return {'success': False, 'errors': [{'code': 404, 'message': 'Not Found', 'detail': 'Not Found'}],
                    'result': False}, 404
        return {'success': True, 'errors': None, 'result': [msg['id'] for msg in mailbox['messages']]}, 200


class Token(Resource):
    def put(self, name):
        new_token = secrets.token_hex(16)
        mailboxes.update_one({"name": name}, {"$set": {"token": new_token}})
        return {'success': True, 'errors': None, 'result': {'name': name, 'token': new_token}}, 200


class Messages(Resource):
    def post(self, name):
        # Retrieve the mailbox
        mailbox = mailboxes.find_one({"name": name})
        if mailbox is None:
            return {'success': False, 'errors': [{'code': 404, 'message': 'Not Found', 'detail': 'Not Found'}],
                    'result': False}, 404
        message_ids = request.json
        messages = [msg for msg in mailbox['messages'] if msg['id'] in message_ids]
        return {'success': True, 'errors': None, 'result': messages}, 200

    def put(self, name):
        # Create and add a new message
        mailbox = mailboxes.find_one({"name": name})
        if mailbox is None:
            return {'success': False, 'errors': [{'code': 404, 'message': 'Not Found', 'detail': 'Not Found'}],
                    'result': False}, 404
        message = request.json
        mailbox['messages'].append(message)
        mailboxes.update_one({"name": name}, {"$set": {"messages": mailbox['messages']}})
        return {'success': True, 'errors': None, 'result': True}, 200


class Message(Resource):
    def get(self, name, id):
        # Fetch the message with the given id
        mailbox = mailboxes.find_one({"name": name})
        if mailbox is None:
            return {'success': False, 'errors': [{'code': 404, 'message': 'Not Found', 'detail': 'Not Found'}],
                    'result': False}, 404
        message = [msg for msg in mailbox['messages'] if msg['id'] == id]
        if not message:
            return {'success': False, 'errors': [{'code': 404, 'message': 'Not Found', 'detail': 'Not Found'}],
                    'result': False}, 404
        return {'success': True, 'errors': None, 'result': message[0]}, 200

    def delete(self, name, id):
        # Delete the message with the given id
        mailbox = mailboxes.find_one({"name": name})
        if mailbox is None:
            return {'success': False, 'errors': [{'code': 404, 'message': 'Not Found', 'detail': 'Not Found'}],
                    'result': False}, 404
        mailbox['messages'] = [msg for msg in mailbox['messages'] if msg['id'] != id]
        mailboxes.update_one({"name": name}, {"$set": {"messages": mailbox['messages']}})
        return {'success': True, 'errors': None, 'result': True}, 200


api.add_resource(Mailbox, '/api/mailbox', '/api/mailbox/<string:name>')
api.add_resource(Token, '/api/mailbox/<string:name>/token')
api.add_resource(Messages, '/api/mailbox/<string:name>/messages')
api.add_resource(Message, '/api/mailbox/<string:name>/messages/<string:id>')

if __name__ == '__main__':
    app.run(debug=True)
