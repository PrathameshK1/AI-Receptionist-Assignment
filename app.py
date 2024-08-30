import streamlit as st
from dotenv import load_dotenv
import os
import google.generativeai as genai
import time

load_dotenv()  # load all the environment variables
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Simulated vector database for emergency responses
emergency_responses = {
    "not breathing": "Perform CPR immediately. Place your hands on the center of the chest and push hard and fast at a rate of 100-120 compressions per minute. After every 30 compressions, give 2 rescue breaths.",
    "chest pain": "Have the person sit down and rest. If available, give them an aspirin to chew. Loosen any tight clothing.",
    "severe bleeding": "Apply direct pressure to the wound with a clean cloth or bandage. Elevate the injured area above the heart if possible.",
    "unconscious": "Check for breathing. If they are breathing, place them in the recovery position. If not breathing, start CPR immediately.",
    "allergic reaction": "If the person has an EpiPen, help them use it. Remove any potential allergens and help them into a comfortable position.",
}

AI_RECEPTIONIST_PROMPT = """
You are an AI receptionist for Dr. Adrin. Your task is to handle emergency calls and messages. Follow these instructions:

1. First, confirm if the user has an emergency or wants to leave a message.
2. If it's a message, ask for the message. If it's an emergency, ask for details about the emergency.
3. For emergencies, provide immediate next steps based on the emergency type. Use the emergency_responses dictionary for this information.
4. While checking the emergency response, ask for the user's location.
5. Provide a random estimated time of arrival for Dr. Adrin (between 5 and 20 minutes).
6. If the user says the arrival will be too late, provide the emergency response again and encourage them to follow the steps.
7. For messages, confirm that it will be forwarded to Dr. Adrin.
8. If the user says something unrelated, express that you don't understand and repeat the last question or statement.

Always maintain a caring and professional tone. Your primary goal is to assist in emergencies and ensure messages are properly handled.

Emergency responses available:
{emergency_responses}

Current conversation:
{conversation_history}

User: {user_input}
AI Receptionist:"""

def get_gemini_response(conversation_history, user_input, emergency_responses):
    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(
        AI_RECEPTIONIST_PROMPT.format(
            emergency_responses=emergency_responses,
            conversation_history=conversation_history,
            user_input=user_input
        )
    )
    return response.text

def main():
    st.title("Dr. Adrin's AI Receptionist")
    
    if 'conversation_history' not in st.session_state:
        st.session_state.conversation_history = []
    
    if 'waiting_for_response' not in st.session_state:
        st.session_state.waiting_for_response = False
    
    # Display conversation history
    for message in st.session_state.conversation_history:
        if message['role'] == 'user':
            st.write("You: " + message['content'])
        else:
            st.write("AI Receptionist: " + message['content'])
    
    # User input
    user_input = st.text_input("You:", key="user_input")
    
    if st.button("Send") and user_input:
        st.session_state.conversation_history.append({"role": "user", "content": user_input})
        st.session_state.waiting_for_response = True
        st.rerun()
    
    if st.session_state.waiting_for_response:
        with st.spinner("AI Receptionist is typing..."):
            # Simulate delay for emergency response lookup
            if any(keyword in user_input.lower() for keyword in emergency_responses.keys()):
                time.sleep(15)
            #Aritificial delay of 15 seconds for emergency response 
            ai_response = get_gemini_response(
                str(st.session_state.conversation_history),
                user_input,
                emergency_responses
            )
            st.session_state.conversation_history.append({"role": "assistant", "content": ai_response})
            st.session_state.waiting_for_response = False
            st.rerun()

if __name__ == "__main__":
    main()
