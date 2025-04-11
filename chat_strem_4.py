import streamlit as st
import requests
import json
import os

CHAT_HISTORY_FILE = "chat_history.json"

# Function to communicate with LLaMA
def get_llama_response(prompt):
    url = 'http://localhost:11434/api/generate'
    data = {"model": "llama3.2", "prompt": prompt, "stream": False}
    headers = {'Content-Type': 'application/json'}

    try:
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()
        return response.json().get('response', 'Sorry, I could not generate a response.')
    except requests.exceptions.RequestException as e:
        return f"Error: {e}"
    except json.JSONDecodeError:
        return "Error: Unable to parse response."

# Function to load chat history from file
def load_chat_history():
    if os.path.exists(CHAT_HISTORY_FILE):
        with open(CHAT_HISTORY_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    return []

# Function to save chat history to file
def save_chat_history(history):
    with open(CHAT_HISTORY_FILE, "w", encoding="utf-8") as file:
        json.dump(history, file, indent=4)

# Load chat history into session state
if "messages" not in st.session_state:
    st.session_state.messages = load_chat_history()

st.title("💪 Gym AI Assistant")

# Sidebar for user details
st.sidebar.header("User Information")
age = st.sidebar.number_input("Age", min_value=10, max_value=100, value=25)
weight = st.sidebar.number_input("Weight (kg)", min_value=30, max_value=200, value=70)
height = st.sidebar.number_input("Height (cm)", min_value=100, max_value=250, value=175)
gender = st.sidebar.selectbox("Gender", ["Male", "Female", "Other"])
goal = st.sidebar.selectbox("Fitness Goal", ["Muscle Gain", "Weight Loss", "General Fitness"])

if st.sidebar.button("Get Diet Advice"):
    prompt = f"Give a diet plan including fruits and vegetables for a {age}-year-old {gender} weighing {weight}kg and {height}cm tall with a goal of {goal}."
    response = get_llama_response(prompt)
    st.subheader("🥗 Personalized Diet Plan")
    st.write(response)

st.subheader("💬 Chat with AI")

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Input field for new message
query = st.chat_input("Type your gym-related question here...")

if query:
    # Append user message
    st.session_state.messages.append({"role": "user", "content": query})

    # Display user message
    with st.chat_message("user"):
        st.markdown(query)

    # Create a gym-specific prompt
    gym_prompt = f"""
    You are a Bot that answers only gym-related questions.
    Don't give any advice about medicines.
    Keep responses short (1-2 lines).
    If the user asks for a longer response, then follow their request.
    User's prompt: {query}
    """

    response = get_llama_response(gym_prompt)

    # Append AI response
    st.session_state.messages.append({"role": "assistant", "content": response})

    # Save updated chat history to file
    save_chat_history(st.session_state.messages)

    # Display AI response
    with st.chat_message("assistant"):
        st.markdown(response)
