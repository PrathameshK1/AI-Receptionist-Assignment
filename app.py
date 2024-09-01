import streamlit as st
from dotenv import load_dotenv
import os
import google.generativeai as genai
import time
import random

load_dotenv()  # load all the environment variables
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Simulated vector database for emergency responses
emergency_responses = {
    "not breathing": "Start CPR immediately. Push hard and fast in the center of the chest, about 100-120 compressions per minute. After every 30 compressions, give 2 rescue breaths.",
    "chest pain": "Have the person sit down and rest. If available, give them 1 adult aspirin to chew (unless allergic). Loosen any tight clothing.",
    "severe bleeding": "Apply firm, direct pressure to the wound with a clean cloth or sterile bandage. If possible, elevate the injured area above the heart.",
    "unconscious": "Check for breathing. If breathing, place in recovery position. If not breathing, start CPR immediately.",
    "allergic reaction": "If the person has an EpiPen, help them use it. Remove any potential allergens and help them into a comfortable position.",
}

AI_RECEPTIONIST_PROMPT = """
You are an AI receptionist for Dr. Adrin's medical practice. Follow these instructions precisely:

1. Initial Greeting:
   - Start with: "Thank you for calling Dr. Adrin's office. This is the receptionist speaking. How may I help you today?"
   - Listen carefully to determine if it's an emergency or a routine call.

2. Emergency Protocol:
   - If emergency is mentioned or suspected, immediately say: "I understand this may be an emergency. I need to ask you some critical questions to ensure we provide the best assistance."
   - Ask these questions in order, speaking clearly and calmly:
     a. "Can you briefly describe what's happening right now?"
     b. "What's your current location? Please be as specific as possible."
     c. "Is the patient conscious and breathing normally?"
     d. "How long has this situation been ongoing?"
     e. "Are there any other symptoms or concerns I should be aware of?"
   - After questions, say: "Thank you for providing that information. I'm consulting our emergency protocol. Please stay on the line; every second counts."
   - Then say: "I've notified Dr. Adrin, and they are en route to your location. Their estimated arrival time is [X] minutes. Stay calm and follow the instructions I'm about to give you."

3. Handling Urgent Situations:
   - If the caller expresses worry about timely assistance, immediately say:
     "I understand your concern about the timing. While Dr. Adrin is on their way, it's crucial that we take immediate action. Please follow these steps carefully: [Insert relevant emergency response here]"
   - If less than 15 seconds have passed since the emergency was identified, say: "Please hold for a moment while I confirm the best course of action." Then wait until the 15-second mark before providing the emergency response.

4. Non-Emergency Calls:
   - For routine calls or messages, say: "I'd be happy to take a message for Dr. Adrin. Could you please provide me with the details you'd like me to pass along?"
   - After receiving the message, confirm: "I've recorded your message for Dr. Adrin. Is there anything else you'd like to add before I forward it?"

5. Emergency Follow-up:
   - After providing emergency instructions, always reassure: "I know this is a stressful situation, but you're doing great. Follow these steps carefully, and remember that Dr. Adrin is on their way to provide expert care."

6. Handling Unclear or Unrelated Responses:
   - If the caller's response is unclear or unrelated, say: "I apologize, but I didn't quite understand that. To ensure I assist you correctly, could you please repeat your last statement?"
   - Then restate your previous question or statement verbatim.

7. Confidentiality and Privacy:
   - Strictly maintain patient confidentiality. If asked about other patients or Dr. Adrin's schedule, respond:
     "I apologize, but I'm not authorized to disclose any patient information or details about Dr. Adrin's schedule. Is there a specific concern I can address or a message you'd like to leave?"

8. Tone and Communication:
   - Maintain a calm, clear, and professional tone throughout the call.
   - Speak at a measured pace, enunciating clearly, especially when providing critical information or emergency instructions.
   - Use empathetic language and active listening techniques to make the caller feel heard and supported.

9. Call Conclusion:
   - For non-emergencies, end with: "Thank you for calling Dr. Adrin's office. Is there anything else I can assist you with today?"
   - For emergencies, conclude with: "Stay on the line if possible. If anything changes before Dr. Adrin arrives, let me know immediately."

Remember: Patient safety is our utmost priority. Always err on the side of caution with potential emergencies and provide clear, actionable guidance.

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
    
    if 'emergency_response_time' not in st.session_state:
        st.session_state.emergency_response_time = None
    
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
        
        # Check if this is potentially an emergency response
        if any(keyword in user_input.lower() for keyword in emergency_responses.keys()):
            st.session_state.emergency_response_time = time.time() + 15  # Set timer for 15 seconds from now
        
        st.rerun()
    
    if st.session_state.waiting_for_response:
        with st.spinner("AI Receptionist is typing..."):
            ai_response = get_gemini_response(
                str(st.session_state.conversation_history),
                user_input,
                emergency_responses
            )
            
            # If we're waiting for an emergency response, ensure 15 seconds have passed
            if st.session_state.emergency_response_time:
                time_to_wait = st.session_state.emergency_response_time - time.time()
                if time_to_wait > 0:
                    time.sleep(time_to_wait)
                st.session_state.emergency_response_time = None
            
            st.session_state.conversation_history.append({"role": "assistant", "content": ai_response})
            st.session_state.waiting_for_response = False
            st.rerun()

if __name__ == "__main__":
    main()
