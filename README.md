# 🏥 ClinicPilot AI - Local Setup & Demo Guide

ClinicPilot AI is an intelligent medical clinic assistant that allows patients to inquire about services, check existing appointments, and book new visits via a conversational AI interface.

## Prerequisites
*   **Python 3.10+**
*   **Node.js & npm** (v16+)
*   **Ollama** (Installed and running locally for the LLM engine)

## Step 1: Initialize the Local AI Model (Ollama)
We use Ollama to run the agent completely locally and free of charge.
1. Download and install Ollama from [ollama.com](https://ollama.com).
2. Open your terminal and pull the designated model (we recommend `qwen2.5:7b` for fast, local tool-calling):
   ```bash
   ollama run qwen2.5:7b
   ```
*(You can exit the interactive prompt by typing `/exit`. The Ollama background service must remain running).*

## Step 2: Backend Setup & Database Seeding
1. Open a new terminal and navigate to the backend folder:
   ```bash
   cd backend
   ```
2. Create and activate a Python virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   ```
3. Install required dependencies:
   ```bash
   pip install fastapi uvicorn pydantic langchain-ollama langchain-classic python-dotenv
   ```
4. **Seed the Database:** Ensure the `data/` folder exists inside `backend/` and contains the 6 required mock CSV files. Run the seeding script:
   ```bash
   python database.py
   ```
   *You should see a success message indicating `clinicpilot.db` was created.*
5. **Start the API Server:**
   ```bash
   python main.py
   ```
   *The FastAPI server is now running on http://localhost:8000.*

## Step 3: Frontend Setup
1. Open a *third* terminal window and navigate to the frontend folder:
   ```bash
   cd frontend
   ```
2. Install Node dependencies:
   ```bash
   npm install
   ```
3. Start the Vite development server:
   ```bash
   npm run dev
   ```
4. Open your browser to `http://localhost:5173`.

## 🧪 How to run the Live Demo
To test the complete workflow during evaluation, try the following conversational steps in the chat interface:

1. **RAG/Knowledge Q&A:** *"Hi, what are your operating hours? Who is your allergy specialist?"*
2. **Context & Existing Bookings:** *"Can you check when my next appointment is?"* (The AI knows you are P001/John Doe).
3. **Multi-turn Booking:** *"I'd like to book an appointment for my peanut allergy."* (The AI will extract the doctor and treatment, and prompt you for a date and time).
4. **Verification:** Supply a date and time (e.g., *"Next Monday at 10 AM"*). Watch the AI confirm the booking and observe the new record instantly appear on the right-hand **Live Bookings Dashboard**.