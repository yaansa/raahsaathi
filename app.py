
import sqlite3
import random
import requests
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.responses import FileResponse

app = FastAPI()

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "gemma3:1b"
DB = "raahsaathi.db"

FALLBACK = {
    "walk": [
        "Find something red, then listen for three different sounds while you walk.",
        "Walk slowly and count how many different shades of green you can spot.",
        "Find the quietest spot nearby and notice two sounds you hadn't heard before.",
    ],
    "nature": [
        "Find a leaf with a texture different from the others. Describe how it feels.",
        "Look for the tree with the most shade. Who is resting under it?",
        "Spot three different leaf shapes within 100 metres. Do not pluck them.",
    ],
    "garden": [
        "Touch the soil of one plant. Decide if it needs water and why.",
        "Find the newest leaf or bud on any plant and notice its colour.",
        "Sit near plants for two minutes and count every insect you see.",
    ],
}

class MissionReq(BaseModel):
    mode: str = "walk"
    minutes: int = 10

class NoteReq(BaseModel):
    mode: str
    minutes: int
    mission: str
    reflection: str

def build_prompt(mode, minutes):
    return f"""You are an outdoor activity designer.
Create 3 different safe, screen-light activities for a person outside.
Duration: {minutes} minutes
Mode: {mode}
Rules:
- No special equipment.
- Do not ask the user to photograph strangers.
- Do not direct the user into roads, private property, or unsafe areas.
- Each activity under 40 words, sensory and achievable.
- Every activity must start with an action verb (Find, Count, Listen, Touch, Spot).
Output exactly 3 lines, one activity per line, no numbering, no intro, no extra text."""

def note_prompt(req):
    return f"""Write a short field note (3 sentences max) in first person, warm and simple.
Mission: {req.mission}
What I observed: {req.reflection}
Only use what I observed. Do not invent details.
Do not add plans or future intentions. Only describe what happened.
Output just the note."""

def ask_model(prompt):
    r = requests.post(
        OLLAMA_URL,
        json={"model": MODEL, "prompt": prompt, "stream": False},
        timeout=60,
    )
    r.raise_for_status()
    return r.json()["response"]

def init_db():
    con = sqlite3.connect(DB)
    con.execute("""CREATE TABLE IF NOT EXISTS notes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        mode TEXT, minutes INTEGER, mission TEXT,
        reflection TEXT, field_note TEXT,
        created TEXT DEFAULT CURRENT_TIMESTAMP)""")
    con.commit()
    con.close()

init_db()

@app.post("/api/missions")
def missions(req: MissionReq):
    source = "model"
    try:
        text = ask_model(build_prompt(req.mode, req.minutes))
        lines = [l.strip("-•* 0123456789.").strip() for l in text.splitlines() if l.strip()]
        lines = [l for l in lines if len(l.split()) <= 60
                 and not l.endswith(":")
                 and not l.lower().startswith(("absolutely", "sure", "okay", "here"))]
        if len(lines) < 3:
            raise ValueError("model output bad")
        result = lines[:3]
    except Exception:
        source = "fallback"
        result = random.sample(FALLBACK.get(req.mode, FALLBACK["walk"]), 3)
    return {"source": source, "missions": result}

@app.post("/api/note")
def make_note(req: NoteReq):
    source = "model"
    try:
        note = ask_model(note_prompt(req)).strip()
        if not note:
            raise ValueError("empty")
    except Exception:
        source = "fallback"
        note = f"Today's mission: {req.mission} I noticed: {req.reflection}"
    con = sqlite3.connect(DB)
    con.execute(
        "INSERT INTO notes (mode, minutes, mission, reflection, field_note) VALUES (?,?,?,?,?)",
        (req.mode, req.minutes, req.mission, req.reflection, note),
    )
    con.commit()
    con.close()
    return {"source": source, "field_note": note}

@app.get("/api/history")
def history():
    con = sqlite3.connect(DB)
    rows = con.execute(
        "SELECT mode, minutes, mission, field_note, created FROM notes ORDER BY id DESC"
    ).fetchall()
    con.close()
    return [
        {"mode": r[0], "minutes": r[1], "mission": r[2], "field_note": r[3], "created": r[4]}
        for r in rows
    ]

@app.get("/")
def home():
    return FileResponse("static/index.html")