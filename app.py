import os
import pandas as pd
import sqlite3
from datetime import datetime
import streamlit as st
from srs import CardState, schedule

DB = "flashcards.db"
def init_db():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS cards(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        front TEXT NOT NULL,
        back TEXT NOT NULL,
        hint TEXT,
        interval INT DEFAULT 0,
        repetition INT DEFAULT 0,
        ease REAL DEFAULT 2.5,
        next_review TEXT DEFAULT (datetime('now'))
    )""")
    conn.commit()
    return conn

def add_card(conn, front, back, hint):
    cur = conn.cursor()
    cur.execute("INSERT INTO cards(front, back, hint, next_review) VALUES(?,?,?,datetime('now'))", (front, back, hint))
    conn.commit()

def load_due(conn):
    cur = conn.cursor()
    cur.execute("SELECT id, front, back, hint, interval, repetition, ease, next_review FROM cards WHERE datetime(next_review) <= datetime('now') ORDER BY next_review LIMIT 1")
    return cur.fetchone()

def update_card(conn, id, state, next_review):
    cur = conn.cursor()
    cur.execute("UPDATE cards SET interval=?, repetition=?, ease=?, next_review=? WHERE id=?",
                (state.interval, state.repetition, state.ease, next_review.isoformat(), id))
    conn.commit()

def import_csv(conn, path='data/flashcards.csv'):
    if not os.path.exists(path): return
    df = pd.read_csv(path)
    for _, r in df.iterrows():
        add_card(conn, r['front'], r['back'], r.get('hint', ''))

def ai_hint(front, default_hint):
    key = os.getenv('OPENAI_API_KEY')
    if not key:
        return default_hint or "Try recalling key terms and definitions related to this prompt."
    try:
        from openai import OpenAI
        client = OpenAI(api_key=key)
        msg = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role":"system","content":"Give a terse study hint (not the answer)."},
                {"role":"user","content":front}
            ],
            max_tokens=60,
            temperature=0.4
        )
        return msg.choices[0].message.content.strip()
    except Exception:
        return default_hint or "Focus on the core concept and any formulas."

st.set_page_config(page_title="AI Smart Flashcards", page_icon="🧠", layout="centered")
st.title("🧠 AI Smart Flashcards")
conn = init_db()

with st.sidebar:
    st.header("Manage")
    if st.button("Import starter CSV"):
        import_csv(conn)
        st.success("Imported starter cards.")
    with st.form("add_card"):
        f = st.text_input("Front")
        b = st.text_area("Back")
        h = st.text_input("Hint (optional)")
        submitted = st.form_submit_button("Add card")
        if submitted and f and b:
            add_card(conn, f, b, h)
            st.success("Added card.")

row = load_due(conn)
if not row:
    st.info("No cards due. Add some or check back later!")
else:
    id, front, back, hint, interval, rep, ease, next_review = row
    st.subheader("Review")
    st.markdown(f"**Front:** {front}")
    if st.button("AI Hint"):
        st.session_state["hint"] = ai_hint(front, hint)
    if "hint" in st.session_state:
        st.caption("Hint: " + st.session_state["hint"])

    with st.form("grade"):
        show_answer = st.form_submit_button("Show Answer")
    if show_answer:
        st.success("Answer: " + back)

    score = st.slider("How well did you recall? (1=Hard .. 5=Easy)", 1, 5, 3)
    if st.button("Submit score & schedule next"):
        state, next_dt = schedule(score, CardState(interval=interval, repetition=rep, ease=ease))
        update_card(conn, id, state, next_dt)
        st.success(f"Scheduled next review in {state.interval} day(s). Ease={state.ease:.2f}")
