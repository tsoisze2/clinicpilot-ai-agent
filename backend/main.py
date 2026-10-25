import sqlite3
import os
import uuid
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

from langchain_ollama import ChatOllama
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_classic.agents import AgentExecutor, create_tool_calling_agent

app = FastAPI(title="ClinicPilot AI API")

# Allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_NAME = "clinicpilot.db"

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

# --- AI Tools ---

@tool
def search_clinic_info(query: str) -> str:
    """Use this tool to search for doctors, treatments, and clinic operations."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    results = []
    
    # Added clinics table query
    cursor.execute("SELECT * FROM clinics")
    clinics = cursor.fetchall()
    results.append("Clinics: " + str([dict(c) for c in clinics]))
    
    cursor.execute("SELECT * FROM doctors")
    doctors = cursor.fetchall()
    results.append("Doctors: " + str([dict(d) for d in doctors]))
    
    cursor.execute("SELECT * FROM treatments")
    treatments = cursor.fetchall()
    results.append("Treatments: " + str([dict(t) for t in treatments]))
    
    conn.close()
    return " ".join(results)

@tool
def get_existing_bookings(patient_id: str) -> str:
    """Retrieve existing medical appointments and bookings for a specific patient."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM patient_bookings WHERE patient_id = ?", (patient_id,))
    bookings = cursor.fetchall()
    conn.close()
    
    if not bookings:
        return "No existing bookings found."
    return str([dict(b) for b in bookings])

@tool
def create_new_booking(patient_id: str, doctor_id: str, treatment_id: str, booking_date: str, booking_time: str) -> str:
    """
    Create a new medical appointment. 
    Requires patient_id, doctor_id, treatment_id, booking_date (YYYY-MM-DD), and booking_time (HH:MM).
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    booking_id = f"B{str(uuid.uuid4())[:6].upper()}"
    
    try:
        cursor.execute('''
            INSERT INTO patient_bookings (booking_id, patient_id, doctor_id, treatment_id, booking_date, booking_time, status, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (booking_id, patient_id, doctor_id, treatment_id, booking_date, booking_time, 'Confirmed', 'Created via AI Agent'))
        conn.commit()
        result = f"Successfully created booking {booking_id} for {booking_date} at {booking_time}."
    except Exception as e:
        result = f"Failed to create booking: {str(e)}"
    finally:
        conn.close()
        
    return result

tools = [search_clinic_info, get_existing_bookings, create_new_booking]

# Using local Ollama model instead of OpenAI
llm = ChatOllama(model="qwen2.5:7b", temperature=0)

# Injecting the single-patient context assumption
system_prompt = """You are ClinicPilot AI, a helpful medical clinic assistant.
You are currently talking to patient John Doe (Patient ID: P001). 
Medical Context: John has a severe peanut allergy.

Your capabilities:
1. Answer questions about the clinic, doctors, and treatments using the search_clinic_info tool.
2. Check existing bookings for the user using the get_existing_bookings tool.
3. Book new appointments using the create_new_booking tool.

When booking an appointment, you MUST extract the doctor_id, treatment_id, booking_date, and booking_time. 
If any of these are missing, politely ask the user for them. Assume John Doe's patient_id is always 'P001'.
Never invent doctor IDs or treatment IDs; look them up if the user provides a name or symptom.
"""

prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad"),
])

agent = create_tool_calling_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

# --- API Models & Endpoints ---

class MessageItem(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[MessageItem]

@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest):
    chat_history = []
    for msg in request.messages[:-1]:
        if msg.role == "user":
            chat_history.append(HumanMessage(content=msg.content))
        elif msg.role == "assistant":
            chat_history.append(AIMessage(content=msg.content))
            
    latest_input = request.messages[-1].content
    
    try:
        response = agent_executor.invoke({
            "input": latest_input,
            "chat_history": chat_history
        })
        return {"response": response["output"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/bookings")
async def get_bookings():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM patient_bookings WHERE patient_id = 'P001' ORDER BY booking_date DESC, booking_time DESC")
    bookings = cursor.fetchall()
    conn.close()
    return {"bookings": [dict(b) for b in bookings]}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)