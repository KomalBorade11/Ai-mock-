# AI Mock Interview - Real-Time Voice System

A full-stack AI-powered mock interview system with real-time voice input using Web Speech API, FastAPI backend, and intelligent conversation flow.

## Features

✅ **Real-Time Voice Input**: Uses Web Speech API for live speech-to-text (no file uploads)
✅ **Continuous Conversation**: AI dynamically decides follow-ups, topic changes, or completion
✅ **30-Minute Interview Timer**: Automatic completion with final feedback
✅ **Chat-Based Interface**: Beautiful web UI showing conversation history
✅ **Resume Analysis**: AI analyzes uploaded resume for personalized questions
✅ **Intelligent AI Flow**: Follow-up questions, topic transitions, natural conversation
✅ **Cross-Platform**: Works on desktop and mobile browsers
✅ **No Audio Storage**: Everything processed in real-time, no files stored

## System Architecture

```
Frontend: HTML + JavaScript (Web Speech API)
├── index.html (Real-time voice interface)
└── Web Speech API integration

Backend: Python FastAPI + LangGraph
├── main.py (API endpoints for real-time processing)
├── utils.py (LLM integration, AI decision logic)
├── graph.py (Interview workflow nodes)
└── data/ (CSV datasets)
```

## Technical Implementation

### Frontend (JavaScript)
- **Web Speech API**: `SpeechRecognition` with `continuous=true` and `interimResults=true`
- **Real-Time Display**: Live transcript updates as user speaks
- **Automatic Processing**: Sends transcript to backend on speech completion
- **Responsive UI**: Modern design with status indicators and chat interface

### Backend (Python)
- **Real-Time Processing**: `/process_transcript` endpoint for live text input
- **AI Decision Engine**: Analyzes responses and decides next action
- **Conversation Memory**: Maintains full chat history
- **Intelligent Flow**: Follow-ups, topic changes, or completion based on context

## Installation & Setup

### Step 1: Install Dependencies

```bash
cd "c:\Users\Patangrao Bhosale\Desktop\AI PROJECT\ai-mock-interview"
pip install -r requirements.txt
```

### Step 2: Get Hugging Face Token

1. Go to https://huggingface.co/settings/tokens
2. Create a new token with **Read** permissions
3. Copy the token

### Step 3: Set Environment Variable

**In PowerShell:**
```powershell
$env:HF_TOKEN = "your_hugging_face_token_here"
```

### Step 4: Run Backend

```bash
cd backend
python main.py
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8001
```

### Step 5: Open Frontend

Simply open the `frontend/index.html` file in your web browser:

**Windows:**
- Double-click `frontend/index.html` or
- Right-click → Open with → Your browser

**Or serve locally:**
```bash
cd frontend
python -m http.server 3000
```
Then go to http://localhost:3000

## Browser Requirements

**Supported Browsers:**
- ✅ Chrome/Chromium (recommended)
- ✅ Microsoft Edge
- ✅ Safari (limited support)
- ❌ Firefox (no Web Speech API support)

**Permissions Required:**
- Microphone access (grant when prompted)
- HTTPS recommended for production (HTTP works for localhost)

## Usage

### Step 1: Setup
1. **Upload Resume**: Select your PDF resume
2. **Choose Role**: Select from dropdown or specify custom role
3. **Start Interview**: Click "Start Interview" button

### Step 2: Voice Interview
1. **Click "Start Microphone"**: Grant microphone permission when prompted
2. **Speak Naturally**: Talk as you would in a real interview
3. **See Live Transcript**: Your words appear in real-time
4. **AI Responds**: Interviewer asks follow-up questions automatically
5. **Continue Conversation**: AI decides flow based on your responses

### Step 3: Interview Flow
- **Follow-up Questions**: AI asks deeper questions on your answers
- **Topic Changes**: Moves to new areas based on conversation
- **Natural Flow**: Conversation continues until completion
- **Time Management**: 30-minute limit with automatic completion
- **Early Exit**: "End Interview" button available anytime

### Step 4: Completion
- **Final Feedback**: Comprehensive evaluation provided
- **Performance Analysis**: Based on entire conversation
- **Improvement Suggestions**: Specific recommendations

## API Endpoints

### POST `/upload_resume`
Upload PDF resume for analysis.
```json
FormData: { "file": PDF file }
Response: { "session_id": "string", "resume_text": "string" }
```

### POST `/start_interview`
Initialize interview with role.
```json
{
  "session_id": "string",
  "role": "string"
}
Response: { "success": true, "chat_history": [...], "current_question": "string" }
```

### POST `/process_transcript`
Process real-time speech transcript.
```json
{
  "session_id": "string",
  "transcript": "user speech text"
}
Response: { "next_question": "string" } or { "completed": true, "final_feedback": "string" }
```

### POST `/end_interview_early`
End interview before completion.
```json
{ "session_id": "string" }
Response: { "completed": true, "feedback": "string" }
```

## AI Decision Logic

The system uses intelligent AI to create natural interview flow:

1. **Follow-up**: Asks deeper questions about specific answers
2. **Topic Change**: Moves to new interview areas when appropriate
3. **Continue**: Asks related questions on same topic
4. **Complete**: Ends interview when sufficient coverage achieved
5. **Feedback**: Provides final evaluation in last 5 minutes

## Troubleshooting

### Microphone Issues
- **Permission Denied**: Refresh page and allow microphone access
- **Not Supported**: Use Chrome or Edge browser
- **No Sound**: Check system microphone settings

### Backend Issues
- **Connection Failed**: Ensure backend is running on port 8001
- **HF_TOKEN Error**: Set Hugging Face token correctly
- **Processing Error**: Check console for detailed error messages

### Performance
- **Slow Response**: First request may be slower due to model loading
- **High CPU**: AI processing requires computational resources
- **Memory Usage**: Large conversations may increase memory usage

## Development

### Adding New Features
- **Frontend**: Modify `frontend/index.html` JavaScript
- **Backend**: Add endpoints in `backend/main.py`
- **AI Logic**: Update functions in `backend/utils.py`

### Customization
- **Interview Length**: Modify timer in frontend JavaScript
- **AI Prompts**: Update prompts in `backend/utils.py`
- **UI Styling**: Modify CSS in `frontend/index.html`

## Security Notes

- **Local Development**: Only runs on localhost for security
- **No Audio Storage**: Audio processed in real-time, not stored
- **Token Security**: Never commit HF_TOKEN to version control
- **HTTPS**: Use HTTPS in production for microphone access

---

**Ready to start your AI-powered voice interview! 🎤🤖**

## Interview Flow

- **Dynamic Questions**: AI analyzes answers and decides next action
- **Follow-up Questions**: Deepens discussion on specific topics
- **Topic Changes**: Moves to new areas based on conversation flow
- **Natural Conversation**: Chat-like interface shows full conversation
- **Voice-First**: Primary input method is voice recording
- **Time Management**: 30-minute limit with progress tracking
- **Smart Completion**: AI determines when interview is complete
```cmd
set HF_TOKEN=your_hugging_face_token_here
```

Replace `your_hugging_face_token_here` with your actual token.

### Step 4: Run Backend (Terminal 1)

```bash
cd backend
python main.py
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Step 5: Run Frontend (Terminal 2)

```bash
cd frontend
streamlit run app.py
```

You should see:
```
You can now view your Streamlit app in your browser.
Local URL: http://localhost:8501
```

### Step 6: Open Application

Go to **http://localhost:8501** in your browser

## Usage

1. **Upload Resume** - Submit a PDF resume
2. **Select Role** - Choose position (Full Stack Developer, Data Scientist, etc.)
3. **Start Interview** - Begin the 30-minute AI-powered interview
4. **Voice Answers** - Record and upload voice answers for each question
5. **AI Conversation** - AI decides follow-ups, topic changes, or continuation
6. **Chat Interface** - View conversation history as interviewer-user chat
7. **Auto Completion** - Interview ends at 30 minutes or when AI decides complete
8. **Early Exit** - Option to end interview anytime with exit button
9. **Final Feedback** - Comprehensive evaluation in last 5 minutes

## File Structure

```
ai-mock-interview/
├── backend/
│   ├── main.py              # FastAPI server with endpoints
│   ├── graph.py             # LangGraph workflow nodes
│   ├── utils.py             # LLM, PDF, audio utilities
│   └── __init__.py
├── frontend/
│   ├── app.py               # Streamlit UI
│   └── __pycache__/
├── data/
│   ├── questions.csv        # Interview questions by role
│   └── answers.csv          # Reference answers
├── requirements.txt         # Python dependencies
└── README.md
```

## API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/upload_resume` | POST | Upload PDF resume |
| `/start_interview` | POST | Initialize interview with role |
| `/next_question` | POST | Get next question |
| `/submit_answer` | POST | Submit answer & get feedback |
| `/end_interview` | POST | End interview & get final results |

## Key Fixes Applied

### Backend (utils.py)
- Fixed Hugging Face API response parsing
- Error handling for LLM failures
- Default fallback values
- Improved audio transcription handling

### Backend (main.py)
- Added CORS middleware for Streamlit
- Better error handling on all endpoints
- Session validation
- 1-hour timer implementation
- Improved feedback aggregation

### Backend (graph.py)
- Error handling in all nodes
- State initialization validation
- CSV dataset loading with fallbacks
- Reference answer matching

### Frontend (app.py)
- Removed threading (Streamlit incompatible)
- Better timer implementation
- Improved UI with tabs for text/audio
- Better error messages
- Session state management
- Real-time progress tracking

## Configuration

### CSV Datasets

**questions.csv format:**
```csv
role,question
Full Stack Developer,Can you explain REST vs GraphQL?
Data Scientist,What is supervised learning?
```

**answers.csv format:**
```csv
question,answer
Can you explain REST vs GraphQL?,"REST uses HTTP methods, GraphQL queries specific data..."
```

## Troubleshooting

### Backend won't start
- Ensure HF_TOKEN environment variable is set
- Check port 8000 is available
- Run: `netstat -ano | findstr 8000`

### Frontend won't connect to backend
- Check backend is running on http://localhost:8000
- Check CORS is enabled in main.py
- Try: `curl http://localhost:8000/docs` (should show Swagger UI)

### Interview won't start
- Verify resume text extracted correctly
- Check role name matches CSV
- Check CSV files are in `data/` folder

### Timer issues
- Timer updates based on page refresh
- Manual "End Interview" available anytime

## Notes

- Session data stored in-memory (use database for production)
- Whisper runs on CPU (adjust `device=0` for GPU in utils.py)
- Sample CSV has 6 questions (expand as needed)
- LLM scores are estimates (randomized if parsing fails)
- Interview logs: Check terminal output

## Future Enhancements

- Store results in PostgreSQL database
- Multiple language support
- Advanced analytics dashboard
- Video recording integration
- Real-time performance stats