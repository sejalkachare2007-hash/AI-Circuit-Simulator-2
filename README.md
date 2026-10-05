# AI Prompt-Based Circuit Designer

This is the initial project setup for the AI Prompt-Based Circuit Designer, an AI-assisted system that allows users to describe their desired electronic circuit using simple natural-language prompts.

## Project Structure

- `backend/`: Flask backend application
- `frontend/`: HTML/CSS/JS frontend interface
- `tests/`: Test scripts (to be implemented)

## Prerequisites

- Python 3.10 or above
- A modern web browser

## Setup Instructions

1. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   # On Windows
   venv\Scripts\activate
   # On Linux/Mac
   source venv/bin/activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Initialize the Database:**
   ```bash
   cd backend
   python database/init_db.py
   cd ..
   ```
   This will create the SQLite database in `backend/data/` and seed it with initial electronic components.

## Running the Application

1. **Start the Flask Backend:**
   ```bash
   cd backend
   python app.py
   ```
   The backend will start at `http://127.0.0.1:5000`

2. **Open the Frontend:**
   - Simply open `frontend/index.html` in your web browser.
   - It will automatically attempt to connect to the running Flask backend on port 5000 and display the connection status.

## Current Modules Implemented

- Initial Project Architecture
- Backend Configuration and Health-Check API
- SQLite Database Setup with SQLAlchemy Models
- Component Seed Data
- Frontend Structure (HTML/CSS/JS)
- Frontend-Backend Communication Test
