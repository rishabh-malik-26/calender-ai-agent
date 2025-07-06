import streamlit as st
import logging
logging.basicConfig(level=logging.INFO,format= '%(asctime)s - %(levelname)s - %(message)s')
import requests


st.set_page_config(page_title="AI Calendar Agent", page_icon="📅")
st.title("📅 AI Calendar Assistant")

# Backend FastAPI URL
FASTAPI_URL = "https://calender-ai-agent-2uqh.onrender.com/ask"

st.markdown("""
Type a message to the AI assistant. Try examples like:
- "Book a meeting with Riya tomorrow at 3 PM"
- "Cancel my meeting with Rahul on 10th July"
- "Reschedule the event with ID xyz to 6 PM tomorrow"
- "Check details for event ID abc"
""")

user_input = st.text_input("🗣️ Your message:", key="user_input")
logging.info(f"User Input the query:{user_input}")

if st.button("Send") and user_input:
    with st.spinner("Processing..."):
        try:
            res = requests.post(FASTAPI_URL, json={"message": user_input})
            logging.info(f"Query shared to API:{user_input}")

            res.raise_for_status()
            result = res.json()
            logging.info(f'Got response from API:{result}')

            if  "result" in result:
                st.success(f"{result['result']}")
                # logging.info()
            elif "response" in result:
                st.info(result["response"])
            else:
                st.warning("Unexpected response from backend.")
        except requests.exceptions.RequestException as e:
            st.error(f"Error: {e}")



