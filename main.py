from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from schemas import DailyContext, PlanResponse, ConfusionDump, ConfusionResponse
from firebase_auth import verify_token
from gemini_planner import generate_plan, handle_confusion_dump
from firestore_service import FirestoreService
import uuid
from datetime import datetime

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "AI College Planner API", "status": "running"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/test")
def test():
    return {"message": "Backend is working!", "timestamp": datetime.now().isoformat()}

@app.post("/generate-plan", response_model=PlanResponse)
def create_plan(context: DailyContext, uid: str = Depends(verify_token)):
    return generate_plan(context)

@app.post("/confusion-dump", response_model=ConfusionResponse)
def process_confusion(confusion: ConfusionDump, uid: str = Depends(verify_token)):
    response = handle_confusion_dump(confusion)
    
    # Save to Firestore
    dump_data = {
        "id": str(uuid.uuid4()),
        "original_text": confusion.confusion,
        "response": response.dict(),
        "timestamp": datetime.now().isoformat(),
        "age_group": confusion.age_group
    }
    FirestoreService.save_brain_dump(uid, dump_data["id"], dump_data)
    
    return response

@app.get("/user-profile")
def get_profile(uid: str = Depends(verify_token)):
    return FirestoreService.get_user_profile(uid)

@app.post("/user-profile")
def save_profile(profile: dict, uid: str = Depends(verify_token)):
    FirestoreService.save_user_profile(uid, profile)
    return {"status": "saved"}

@app.get("/brain-dumps")
def get_brain_dumps(uid: str = Depends(verify_token)):
    return FirestoreService.get_brain_dumps(uid)

@app.get("/subjects")
def get_subjects(uid: str = Depends(verify_token)):
    return FirestoreService.get_user_subjects(uid)

@app.post("/daily-checkin")
def save_checkin(checkin: dict, uid: str = Depends(verify_token)):
    checkin["timestamp"] = datetime.now().isoformat()
    FirestoreService.save_daily_checkin(uid, checkin)
    return {"status": "saved"}
