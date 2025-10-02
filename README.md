# Intelligent Resume Enhancement System

This project is an AI-powered system designed to optimize resumes for Applicant Tracking Systems (ATS). Users upload their resumes in PDF format, and the system initiates an asynchronous process to analyze, score, and enhance the content using AI. The user can track the progress in real-time and receive the improved resume text along with a before-and-after ATS score comparison.

## Key Features

* **Asynchronous Processing:** Handles resume enhancement as a background task, providing a smooth user experience without long waits or request timeouts.
* **Real-time Status Tracking:** The frontend polls the server to show the user the live status of their enhancement task (e.g., "Parsing Resume," "AI is Enhancing...").
* **AI-Powered Enhancement:** Utilizes the Groq API with Llama 3 for fast and high-quality resume rewriting.
* **ATS Scoring Simulation:** Provides an estimated ATS score before and after enhancement to demonstrate the value of the optimization.
* **Client-Side PDF Generation:** The final enhanced text can be downloaded as a clean PDF directly from the browser.

## Tech Stack

* **Backend:**
    * **Framework:** FastAPI
    * **AI Orchestration:** LangGraph
    * **Language Model:** Groq (Llama 3 70b)
    * **Server:** Uvicorn
* **Frontend:**
    * **Structure:** HTML5
    * **Styling:** Tailwind CSS
    * **Interactivity:** Vanilla JavaScript
    * **PDF Generation:** jsPDF
* **Deployment:** Render

## Project Structure
```
.
├── backend/
│   ├── init.py
│   ├── main.py       # FastAPI app, routes, and async task logic
│   ├── graph.py      # LangGraph workflow definition
│   └── utils.py      # Helper functions (PDF parsing, scoring)
├── frontend/
│   └── index.html    # Single-page frontend application
├── .env              # Local environment variables (not committed)
├── .gitignore
├── README.md
├── requirements.txt
└── vercel.json       # (Can be removed if only using Render)

```
## Local Development Setup

Follow these steps to run the project on your local machine.

### 1. Clone the Repository

```
git clone <your-repository-url>
cd <your-repository-name>
```
2. Set Up a Python Virtual Environment
Bash
```
# Create the environment
python -m venv venv

# Activate the environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
.\venv\Scripts\activate
```
3. Install Dependencies
Bash
```
pip install -r requirements.txt

```
4. Create an Environment File
Create a file named .env in the project's root directory and add your Groq API key:
```
GROQ_API_KEY="gsk_YourSecretKeyHere"
```
5. Run the Backend Server
Bash
```
uvicorn backend.main:app --reload
The server will be running at http://12.0.0.1:8000.
```
6. Access the Application
Open your web browser and navigate to https://enhance-resume-1.onrender.com/ . The backend now serves the frontend file directly.
```
Deployment on Render
This application is configured for easy deployment on Render.

1. Push Your Code to GitHub
Make sure your latest code is pushed to a GitHub repository.

2. Create a New Web Service on Render
Go to your Render Dashboard and click New + > Web Service.

Connect your GitHub account and select your project repository.

Give your service a unique name.

3. Configure the Service
Use the following settings for your web service:

Environment: Python

Region: Choose a region close to you.

Branch: main (or your primary branch)

Build Command: pip install -r requirements.txt

Start Command: uvicorn backend.main:app --host 0.0.0.0 --port $PORT

4. Add Environment Variables
Go to the Environment tab for your new service.

Click Add Environment Variable.

Key: GROQ_API_KEY

Value: Paste your actual Groq API key here.

5. Deploy
Click Create Web Service. Render will automatically pull your code, build the project, and deploy it. Once the deployment is live, you can access your application at the URL provided by Render.
