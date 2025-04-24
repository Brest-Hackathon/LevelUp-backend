from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import sqlite3
import uuid
from datetime import datetime, timedelta
import bcrypt
from xata.client import XataClient
from dotenv import load_dotenv
import os
import json

load_dotenv()

XATA_API_KEY = os.getenv("XATA_API_KEY")
XATA_DB_URL = os.getenv("XATA_DB_URL")

app = FastAPI()

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
    """Verify password using bcrypt [[8]]"""
    return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())

def get_user(login: str) -> dict:
    """Fetch user from Xata by login [[6]]"""
    try:
        result = xata.data().query("users", {"filter": {"login": login}})
        return result.get("records", [{}])[0] if result else {}
    except:
        return {}

@app.post("/register")
async def register(login: str, password: str):
    """User registration endpoint [[7]]"""
    user = get_user(login)
    if user:
        raise HTTPException(status_code=400, detail="Login already exists")
    
    hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    
    print(xata.records().insert("users", {"login": login,"password": hashed_pw, "statistics": '{"achievements": [], "courses": []}', "account_info": '{"level": 0, "decorations": null, "points": 0}'}))
    
    return {"message": "Registration successful"}

@app.post("/login")
async def login(login: str, password: str):
    """Login endpoint with session management [[9]]"""
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

@app.get("/verify")
async def verify_session(session_key: str = Depends(oauth2_scheme)):
    """Session verification endpoint [[7]]"""
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
    """Session termination endpoint [[9]]"""
    cursor.execute("DELETE FROM sessions WHERE session_id = ?", (session_key,))
    conn.commit()
    return {"message": "Logout successful"}

@app.get("/leaderboard")
async def leaderboard(session_key: str = Depends(oauth2_scheme)):
    """Get user leaderboard sorted by points [[7]][[9]]"""
    cursor.execute("""
        SELECT * FROM sessions 
        WHERE session_id = ? AND expires_at > ?
    """, (session_key, datetime.utcnow()))
    session = cursor.fetchone()
    if not session:
        raise HTTPException(status_code=401, detail="Invalid session")
    
    try:
        result = xata.data().query("users")
        users = result.get("records", [])
    except Exception as e:
        raise HTTPException(status_code=500, detail="Database query failed")
    
    leaderboard = []
    for user in users:
        try:
            account_info = user.get("account_info", [])
            account_info = json.loads(account_info)
            points = account_info.get("points", 0)
            leaderboard.append({
                "rank": 0,
                "user_id": user["id"],
                "login": user["login"],
                "points": points
            })
        except (KeyError, json.JSONDecodeError):
            continue
    
    leaderboard.sort(key=lambda x: x["points"], reverse=True)
    for idx, entry in enumerate(leaderboard, 1):
        entry["rank"] = idx
    
    return {"leaderboard": leaderboard}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
