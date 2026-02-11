import firebase_admin
from firebase_admin import credentials, auth
from fastapi import HTTPException, Header
import os
from dotenv import load_dotenv

load_dotenv()

if not firebase_admin._apps:
    cred = credentials.Certificate(os.getenv("FIREBASE_SERVICE_ACCOUNT_KEY", "serviceAccountKey.json"))
    firebase_admin.initialize_app(cred)

def verify_token(authorization: str = Header(None)) -> str:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid authorization header")
    
    token = authorization.split("Bearer ")[1]
    
    try:
        decoded = auth.verify_id_token(token)
        return decoded["uid"]
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid token")
