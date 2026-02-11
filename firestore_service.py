import firebase_admin
from firebase_admin import credentials, firestore
from typing import Dict, List, Any
import os
import json
from dotenv import load_dotenv

load_dotenv()

# Initialize Firebase Admin
if not firebase_admin._apps:
    service_account = os.getenv("FIREBASE_SERVICE_ACCOUNT_KEY")
    if service_account:
        cred = credentials.Certificate(json.loads(service_account))
    else:
        cred = credentials.Certificate("serviceAccountKey.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()

class FirestoreService:
    @staticmethod
    def get_user_profile(uid: str) -> Dict[str, Any]:
        doc = db.collection('users').document(uid).get()
        return doc.to_dict() if doc.exists else {}
    
    @staticmethod
    def save_user_profile(uid: str, profile: Dict[str, Any]):
        db.collection('users').document(uid).set(profile, merge=True)
    
    @staticmethod
    def get_user_subjects(uid: str) -> List[Dict[str, Any]]:
        docs = db.collection('users').document(uid).collection('subjects').stream()
        return [doc.to_dict() for doc in docs]
    
    @staticmethod
    def save_subject(uid: str, subject_id: str, subject_data: Dict[str, Any]):
        db.collection('users').document(uid).collection('subjects').document(subject_id).set(subject_data)
    
    @staticmethod
    def get_user_tasks(uid: str) -> List[Dict[str, Any]]:
        docs = db.collection('users').document(uid).collection('tasks').stream()
        return [doc.to_dict() for doc in docs]
    
    @staticmethod
    def save_task(uid: str, task_id: str, task_data: Dict[str, Any]):
        db.collection('users').document(uid).collection('tasks').document(task_id).set(task_data)
    
    @staticmethod
    def save_brain_dump(uid: str, dump_id: str, dump_data: Dict[str, Any]):
        db.collection('users').document(uid).collection('brain_dumps').document(dump_id).set(dump_data)
    
    @staticmethod
    def get_brain_dumps(uid: str) -> List[Dict[str, Any]]:
        docs = db.collection('users').document(uid).collection('brain_dumps').order_by('timestamp', direction=firestore.Query.DESCENDING).limit(5).stream()
        return [doc.to_dict() for doc in docs]
    
    @staticmethod
    def save_daily_checkin(uid: str, checkin_data: Dict[str, Any]):
        db.collection('users').document(uid).collection('checkins').add(checkin_data)
