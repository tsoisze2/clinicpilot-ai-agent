# 🏥 ClinicPilot AI - Technical Design Document

## 1. Architectural Choices & Rationale

ClinicPilot AI is built as a lightweight, modular prototype designed for rapid iteration, local testing, and seamless AI integration. 

*   **Backend Engine (FastAPI):** Chosen for its asynchronous capabilities, native Pydantic validation, and excellent compatibility with Python-based AI frameworks like LangChain. It provides a robust yet lightweight API layer.
*   **AI Engine & Tool Calling (LangChain + Ollama):** LangChain's standard tool-calling agent framework was utilized to seamlessly connect natural language processing with backend executable functions. **Ollama** running locally (`qwen2.5:7b`) was selected for the LLM provider to ensure zero API costs, high privacy, and complete local execution without regional API restrictions.
*   **Database (SQLite):** An embedded SQLite database is used for local persistence. It requires zero configuration from the evaluator, making the local demo setup completely frictionless while still demonstrating standard SQL execution and relational data modeling.
*   **Frontend (React + Vite + Tailwind CSS):** Vite provides rapid hot-module replacement for development. React handles the dynamic state between the chat interface and the live bookings dashboard. Tailwind CSS was used to deliver a clean, functional UI without the overhead of external stylesheet management.

## 2. Intent Recognition & Agent Workflow

Instead of a rigid state machine, the system uses an LLM-driven Agentic Workflow powered by tool-calling. The AI dynamically classifies intent based on the conversation history and triggers the appropriate tool:

1.  **Q&A / Recommendation Intent (`search_clinic_info`):** 
    *   *Trigger:* User asks about clinic hours, specific doctors, or treatments.
    *   *Action:* Simulates a Retrieval-Augmented Generation (RAG) approach by querying the local SQLite tables (`clinics`, `doctors`, `treatments`) and injecting the context into the prompt to generate clinical advice.
2.  **Existing Booking Query (`get_existing_bookings`):**
    *   *Trigger:* User asks about past or upcoming appointments.
    *   *Action:* Queries the `patient_bookings` table filtered by the injected patient context (`P001`).
3.  **New Booking Intent (`create_new_booking`):**
    *   *Trigger:* User expresses a desire to book an appointment.
    *   *Workflow:* The System Prompt instructs the AI to extract four mandatory parameters: `doctor_id`, `treatment_id`, `booking_date`, and `booking_time`. If any are missing, the LLM naturally asks the user follow-up questions. Once all parameters are collected, the AI executes the tool to persist the record in the database.

## 3. Context Management (Single-Patient Demo)

To fulfill the demo requirements, a strict context boundary is established via the System Prompt. The agent is explicitly instructed to assume the user is **John Doe (Patient ID: P001)** with a known **peanut allergy**. This allows personalized routing (e.g., matching the allergy with a relevant treatment/doctor) without requiring a complex authentication layer for the MVP.

## 4. Database Schema Design

The application utilizes a relational schema initialized directly from the provided mock CSV datasets. 

*   **Dynamic Seeding:** Tables (`clinics`, `doctors`, `treatments`, `patients`, `patient_treatment_history`) are dynamically generated based on CSV headers to ensure all mock data is available to the AI.
*   **Transactional Table (`patient_bookings`):** An explicit schema is defined for this table to enforce data integrity when the AI agent inserts new records.
    *   `booking_id` (TEXT, Primary Key)
    *   `patient_id` (TEXT, Foreign Key simulation)
    *   `doctor_id` (TEXT)
    *   `treatment_id` (TEXT)
    *   `booking_date` (TEXT)
    *   `booking_time` (TEXT)
    *   `status` (TEXT)
    *   `notes` (TEXT)