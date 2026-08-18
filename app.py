import os
import streamlit as st
from srs import CardState, schedule
from storage import add_card, import_csv, init_db, load_due, update_card

DB = "flashcards.db"

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
conn = init_db(DB)

with st.sidebar:
    st.header("Manage")
    if st.button("Import starter CSV"):
        inserted, skipped = import_csv(conn)
        st.success(f"Imported {inserted} card(s); skipped {skipped} duplicate(s).")
    with st.form("add_card"):
        f = st.text_input("Front")
        b = st.text_area("Back")
        h = st.text_input("Hint (optional)")
        submitted = st.form_submit_button("Add card")
        if submitted and f and b:
            if add_card(conn, f, b, h):
                st.success("Added card.")
            else:
                st.info("That card is already in the deck.")

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
