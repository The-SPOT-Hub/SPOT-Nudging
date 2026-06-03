from datetime import datetime, timezone
from pymongo import MongoClient
from pymongo.errors import PyMongoError
import scripts.config as config

client = MongoClient(config.mongodb_uri)
database = client.get_default_database()
collection = database.get_collection('slack_events')

class DatabaseError(Exception):
    """Custom error for database insertion / updates"""
    def __init__(self, message):
        super().__init__(message)

def insert_new_event(payload):
    """Insert a new document with payload of Slack POST request"""
    current_dt = datetime.now(timezone.utc)

    try:
        result = collection.insert_one({
            'payload': payload,
            'received_at': current_dt,
            'status': 'not_processed',
            'updated_at': current_dt,
            'channel_post_sent': False
        })
    except PyMongoError as e:
        raise DatabaseError(f'Error inserting event document: {str(e)}')

    return result.inserted_id

def update_event(event_id, fields):
    """Updates document for fields passed in"""
    fields['updated_at'] = datetime.now(timezone.utc)

    try:
        result = collection.update_one(
            {'_id': event_id},
            {'$set': fields}
        )
    except PyMongoError as e:
        raise DatabaseError(f'Error updating event document: {str(e)}')
    
    if result.modified_count != 1:
        raise DatabaseError('Event not updated - modified count is 0')