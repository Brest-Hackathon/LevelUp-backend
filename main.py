from fastapi import FastAPI, Depends, HTTPException, status, Header, Body
from fastapi.security import OAuth2PasswordBearer
import sqlite3
import uuid
from datetime import datetime, timedelta
import bcrypt
from xata.client import XataClient
from dotenv import load_dotenv
import os
import json
import base64
import uvicorn
from typing import List
from moodtest import generate_mood_test, analyze_mood
from pydantic import BaseModel

load_dotenv()

XATA_API_KEY = os.getenv("XATA_API_KEY")
XATA_DB_URL = os.getenv("XATA_DB_URL")
API_SECRET_KEY = os.getenv("API_SECRET_KEY")

app = FastAPI()

class Answer(BaseModel):
    question: str
    chosen_option: str

xata = XataClient(api_key=XATA_API_KEY, db_url=XATA_DB_URL)

conn = sqlite3.connect("sessions.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS sessions (
    session_id TEXT PRIMARY KEY,
    user_id TEXT,
    expires_at TIMESTAMP
)
""")
conn.commit()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())

def get_user(login: str) -> dict:
    try:
        result = xata.data().query("users", {"filter": {"login": login}})
        return result.get("records", [{}])[0] if result else {}
    except:
        return {}

def verify_api_key(api_key: str = Header(..., description="Base64 encoded API key")):
    try:
        decoded_key = base64.b64decode(api_key).decode('utf-8')
        if decoded_key != API_SECRET_KEY:
            raise HTTPException(status_code=401, detail="Invalid API key")
    except:
        raise HTTPException(status_code=401, detail="Invalid API key format")

@app.post("/register")
async def register(login: str, password: str):
    """User registration endpoint"""
    user = get_user(login)
    if user:
        raise HTTPException(status_code=400, detail="Login already exists")
    
    hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    
    xata.records().insert("users", {
        "login": login,
        "password": hashed_pw,
        "statistics": '{"achievements": [], "courses": []}',
        "account_info": '{"level": 0, "decorations": null, "points": 0, "premium": null, "days": 0, "restart_streak": 3, "leaderboard": false, "picture": null, "status": null, "mood_status": null}'
    })
    
    return {"message": "Registration successful"}

@app.post("/login")
async def login(login: str, password: str):
    """Login endpoint with session management"""
    user = get_user(login)
    if not user or not verify_password(password, user.get("password", "")):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    session_id = str(uuid.uuid4())
    expires_at = datetime.utcnow() + timedelta(days=30)
    cursor.execute("""
        INSERT INTO sessions (session_id, user_id, expires_at)
        VALUES (?, ?, ?)
    """, (session_id, user["id"], expires_at))
    conn.commit()
    return {
        "session_key": session_id,
        "expires_in": 30*24*3600,
        "user_id": user["id"]
    }

@app.post("/account/statistics")
async def update_statistics(
    stats_data: dict = Body(...),
    session_key: str = Depends(oauth2_scheme),
    api_key: str = Depends(verify_api_key)
):
    cursor.execute("""
        SELECT user_id FROM sessions 
        WHERE session_id = ? AND expires_at > ?
    """, (session_key, datetime.utcnow()))
    session = cursor.fetchone()
    
    if not session:
        raise HTTPException(status_code=401, detail="Invalid session")
    
    user_id = session[0]
    user = xata.records().get("users", user_id)
    
    current_stats = json.loads(user["statistics"])
    current_stats.update(stats_data)
    
    xata.records().update("users", user_id, {"statistics": json.dumps(current_stats)})
    return {"message": "Statistics updated successfully"}

@app.post("/account/info")
async def update_account_info(
    info_data: dict = Body(...),
    session_key: str = Depends(oauth2_scheme),
    api_key: str = Depends(verify_api_key)
):
    cursor.execute("""
        SELECT user_id FROM sessions 
        WHERE session_id = ? AND expires_at > ?
    """, (session_key, datetime.utcnow()))
    session = cursor.fetchone()
    
    if not session:
        raise HTTPException(status_code=401, detail="Invalid session")
    
    user_id = session[0]
    user = xata.records().get("users", user_id)
    
    allowed_fields = {"level", "decorations", "points", "premium", "days", "restart_streak", "leaderboard"}
    filtered_data = {k: v for k, v in info_data.items() if k in allowed_fields}
    
    current_info = json.loads(user["account_info"])
    current_info.update(filtered_data)
    
    xata.records().update("users", user_id, {"account_info": json.dumps(current_info)})
    return {"message": "Account info updated successfully"}

@app.get("/account/info")
async def get_account_info(
    session_key: str = Depends(oauth2_scheme),
    api_key: str = Depends(verify_api_key)
):
    cursor.execute("""
        SELECT user_id FROM sessions 
        WHERE session_id = ? AND expires_at > ?
    """, (session_key, datetime.utcnow()))
    session = cursor.fetchone()
    
    if not session:
        raise HTTPException(status_code=401, detail="Invalid session")
    
    user_id = session[0]
    user = xata.records().get("users", user_id)
    
    return {
        "statistics": json.loads(user["statistics"]),
        "account_info": json.loads(user["account_info"])
    }

@app.get("/verify")
async def verify_session(session_key: str = Depends(oauth2_scheme)):
    """Session verification endpoint"""
    cursor.execute("""
        SELECT * FROM sessions 
        WHERE session_id = ? AND expires_at > ?
    """, (session_key, datetime.utcnow()))
    session = cursor.fetchone()
    
    if not session:
        raise HTTPException(status_code=401, detail="Invalid session")
    
    return {"valid": True, "user_id": session[1]}

@app.post("/logout")
async def logout(session_key: str = Depends(oauth2_scheme)):
    """Session termination endpoint"""
    cursor.execute("DELETE FROM sessions WHERE session_id = ?", (session_key,))
    conn.commit()
    return {"message": "Logout successful"}

@app.get("/leaderboard")
async def leaderboard(
    filter: str = "rank",
    session_key: str = Depends(oauth2_scheme)
):
    """Get user leaderboard filtered by rank (points) or days"""
    cursor.execute("""
        SELECT * FROM sessions 
        WHERE session_id = ? AND expires_at > ?
    """, (session_key, datetime.utcnow()))
    session = cursor.fetchone()
    if not session:
        raise HTTPException(status_code=401, detail="Invalid session")
    
    if filter not in {"rank", "days"}:
        raise HTTPException(status_code=400, detail="Invalid filter. Use 'rank' or 'days'")
    
    try:
        result = xata.data().query("users")
        users = result.get("records", [])
    except Exception as e:
        raise HTTPException(status_code=500, detail="Database query failed")
    
    leaderboard = []
    for user in users:
        try:
            account_info = json.loads(user.get("account_info", "{}"))
            points = account_info.get("points", 0)
            days = account_info.get("days", 0)
            
            leaderboard.append({
                "user_id": user["id"],
                "login": user["login"],
                "points": points,
                "days": days
            })
        except (json.JSONDecodeError, KeyError):
            continue

    sort_key = "points" if filter == "rank" else "days"
    leaderboard.sort(key=lambda x: x[sort_key], reverse=True)
    
    for idx, entry in enumerate(leaderboard, 1):
        entry["rank"] = idx
    
    return {"leaderboard": leaderboard}

@app.get("/flashcards/database")
async def get_flashcards(session_key: str = Depends(oauth2_scheme)):
    """Retrieve flashcards with ID and name from JSON data"""
    cursor.execute("""
        SELECT user_id FROM sessions 
        WHERE session_id = ? AND expires_at > ?
    """, (session_key, datetime.utcnow()))
    session = cursor.fetchone()
    if not session:
        raise HTTPException(status_code=401, detail="Invalid session")
    
    try:
        result = xata.data().query("flash_cards")
        flashcards = result.get("records", [])
    except Exception as e:
        raise HTTPException(status_code=500, detail="Database query failed")
    
    formatted = []
    for fc in flashcards:
        name = fc.get("title", {})
        formatted.append({
            "id": fc["id"],
            "name": name
        })
    
    return formatted


@app.get("/flashcards/{flashcard_id}")
async def get_flashcard_by_id(
    flashcard_id: str, 
    session_key: str = Depends(oauth2_scheme)
):
    """Retrieve specific flashcard with title and content by ID"""
    cursor.execute("""
        SELECT user_id FROM sessions 
        WHERE session_id = ? AND expires_at > ?
    """, (session_key, datetime.utcnow()))
    session = cursor.fetchone()
    if not session:
        raise HTTPException(status_code=401, detail="Invalid session")
    
    try:
        flashcard = xata.records().get("flash_cards", flashcard_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail="Flashcard not found")
    
    if not flashcard:
        raise HTTPException(status_code=404, detail="Flashcard not found")
    
    return {
        "id": flashcard["id"],
        "content": flashcard.get("flash_card",{})
    }
@app.get("/mood/test")
async def mood_test_gen(session_key: str = Depends(oauth2_scheme)):
    """Generate a new mood test"""
    cursor.execute("""
        SELECT user_id FROM sessions 
        WHERE session_id = ? AND expires_at > ?
    """, (session_key, datetime.utcnow()))
    session = cursor.fetchone()
    if not session:
        raise HTTPException(status_code=401, detail="Invalid session")
    test = generate_mood_test()
    if not test:
        raise HTTPException(status_code=500, detail="Failed to generate mood test")
    return test

@app.post("/mood/test")
async def mood_test_analyse(
    answers: List[Answer],
    session_key: str = Depends(oauth2_scheme)
):
    """Analyze mood test answers and update user's mood status"""
    cursor.execute("""
        SELECT user_id FROM sessions 
        WHERE session_id = ? AND expires_at > ?
    """, (session_key, datetime.utcnow()))
    session = cursor.fetchone()
    if not session:
        raise HTTPException(status_code=401, detail="Invalid session")
    user_id = session[0]

    answers_list = [{"question": ans.question, "chosen_option": ans.chosen_option} for ans in answers]
    mood_score = analyze_mood(answers_list) 

    user = xata.records().get("users", user_id)
    current_info = json.loads(user["account_info"])
    current_info["mood_status"] = mood_score

    xata.records().update("users", user_id, {"account_info": json.dumps(current_info)})

    return {"mood_score": mood_score, "status": "Mood status updated successfully"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
