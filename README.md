# AI Interview Preparation Platform

A comprehensive AI-powered interview preparation platform built with Flask, featuring mock interviews, voice input, resume analysis, and progress tracking.

## 🎯 Features

- **User Authentication**: Secure registration and login system
- **AI Mock Interviews**: Practice with intelligent AI interviewer using Gemini API
- **Voice Input Support**: Answer questions using Web Speech API
- **Resume Upload**: Upload and analyze resumes for personalized questions
- **Real-time Chat Interface**: ChatGPT-style interview experience
- **Answer Evaluation**: AI-powered scoring and feedback
- **Coding Assignments**: Practice problems for various roles
- **Progress Analytics**: Track improvement with Chart.js visualizations
- **Responsive Design**: Modern, mobile-friendly interface

## 🛠️ Technology Stack

- **Backend**: Python Flask 3.0
- **Frontend**: HTML5, CSS3, JavaScript
- **Database**: SQLite3 (Three separate databases for modularity)
  - `users.db` - Authentication, interviews, results
  - `questions.db` - Question bank (100+ questions)
  - `assignments.db` - Coding assignments (30+ problems)
- **AI Engine**: Google Gemini API
- **Charts**: Chart.js
- **Voice Input**: Web Speech API

## 📁 Project Structure

```
ai_inetrview/
│
├── app.py                      # Main Flask application (refactored)
├── init_databases.py           # Database initialization script
├── verify_databases.py         # Database verification script
├── .env                        # Environment variables
├── requirements.txt            # Python dependencies
├── README.md                   # This file
├── DATABASE_MIGRATION_GUIDE.md # Database architecture documentation
│
├── databases/                  # Database files (auto-created)
│   ├── users.db               # User authentication & interviews
│   ├── questions.db           # Question bank (100+ questions)
│   └── assignments.db         # Coding assignments (30+ problems)
│
├── databases/                  # SQL schema files
│   ├── users_schema.sql       # Users database schema
│   ├── questions_schema.sql   # Questions database schema
│   └── assignments_schema.sql # Assignments database schema
│
├── templates/                  # HTML templates
│   ├── index.html
│   ├── register.html
│   ├── login.html
│   ├── dashboard.html
│   ├── upload_resume.html
│   ├── interview_setup.html
│   ├── interview_chat.html
│   ├── results.html
│   ├── assignments.html
│   └── progress.html
│
├── static/                     # Static files
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── script.js
│
└── uploads/                    # Resume uploads (auto-created)
```

## 🚀 Installation & Setup

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Modern web browser (Chrome, Firefox, Edge)

### Step 1: Install Dependencies

```bash
pip install flask
pip install python-dotenv
pip install requests
pip install werkzeug
```

Or use the requirements file:

```bash
pip install -r requirements.txt
```

### Step 2: Initialize Databases

Run the database initialization script to create all three databases with sample data:

```bash
python init_databases.py
```

This will:
- Create `databases/` folder
- Initialize `users.db` with 6 tables
- Populate `questions.db` with 115 questions
- Populate `assignments.db` with 32 assignments

To verify the databases:
```bash
python verify_databases.py
```

### Step 3: Configure Environment Variables

1. Open `.env` file
2. Set your `SECRET_KEY` (change default for production)
3. Get Gemini API key from: https://makersuite.google.com/app/apikey
4. Replace `your_gemini_api_key_here` with your actual API key

Example:
```
SECRET_KEY=my-super-secret-key-12345
GEMINI_API_KEY=AIzaSyA...your_actual_key_here
```

### Step 4: Run the Application

```bash
python app.py
```

The application will:
- Initialize the database automatically
- Create sample questions and assignments
- Start the Flask development server

### Step 4: Access the Platform

Open your browser and navigate to:
```
http://127.0.0.1:5000
```

## 📖 Usage Guide

### For Students

1. **Register**: Create an account with username, email, and password
2. **Login**: Access your personalized dashboard
3. **Upload Resume** (Optional): Get personalized interview questions
4. **Start Interview**:
   - Select your target role (Python Developer, Full Stack, etc.)
   - Choose difficulty level (Easy, Medium, Hard)
   - Begin the AI mock interview
5. **Answer Questions**: 
   - Type your answers or use voice input (🎤 button)
   - AI asks follow-up questions based on your responses
6. **End Interview**: Click "End Interview" to get evaluated
7. **View Results**: See your scores and feedback
8. **Practice Assignments**: Complete coding problems
9. **Track Progress**: Monitor improvement over time

### Voice Input

The platform supports voice input for hands-free interviewing:

1. Click the 🎤 microphone button
2. Allow microphone permissions when prompted
3. Speak your answer clearly
4. The speech will be converted to text automatically

**Note**: Voice input requires HTTPS in production or localhost in development.

## 🗄️ Database Schema

### Users
- id, username, email, password (hashed), created_at

### Resumes
- id, user_id, file_path, uploaded_at

### Questions
- id, role, difficulty, question_text, expected_keywords, source, created_at

### Answers
- id, user_id, question_id, answer_text, submitted_at

### Interviews
- id, user_id, role, difficulty, interview_date, status

### Results
- id, user_id, interview_id, technical_score, communication_score, overall_score, feedback

### Assignments
- id, role, assignment_text, difficulty

### Progress
- id, user_id, interview_count, average_score, last_score, updated_at

### ChatHistory
- id, user_id, interview_id, sender, message, timestamp

## 🎨 Features in Detail

### AI Interview System

The AI interviewer:
- Asks role-specific questions
- Adapts to your skill level
- Provides follow-up questions
- Maintains conversation context
- Evaluates answers with feedback

### Evaluation System

Two-tier evaluation:
1. **Keyword-based**: Matches expected keywords
2. **AI-powered**: Uses Gemini to assess quality

Scores include:
- Technical Knowledge (1-10)
- Communication Skills (1-10)
- Overall Performance (1-10)

### Progress Tracking

Visual analytics showing:
- Total interviews completed
- Average score over time
- Latest performance
- Improvement trends
- Interactive Chart.js graphs

## 🔒 Security Features

- Password hashing with werkzeug.security
- Session-based authentication
- CSRF protection via Flask sessions
- File upload validation
- SQL injection prevention via parameterized queries

## 🛠️ Configuration Options

### Upload Settings

Modify in `app.py`:
```python
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'doc'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
```

### AI Model

Change Gemini model:
```python
model = genai.GenerativeModel('gemini-pro')
```

### Session Timeout

Modify in `.env`:
```
PERMANENT_SESSION_LIFETIME=3600  # 1 hour
```

## 📊 Sample Data

The platform includes:
- 12 sample interview questions
- 8 coding assignments
- Multiple difficulty levels
- Various role categories

## 🐛 Troubleshooting

### Issue: Database not found
**Solution**: Delete `database.db` and restart `python app.py`

### Issue: Gemini API error
**Solution**: 
1. Check your API key in `.env`
2. Verify internet connection
3. Check API quota at Google AI Studio

### Issue: Voice input not working
**Solution**: 
1. Use Chrome, Edge, or Safari
2. Allow microphone permissions
3. Use HTTPS or localhost

### Issue: File upload fails
**Solution**: 
1. Check file size (max 16MB)
2. Use PDF or DOCX format
3. Ensure `uploads/` folder exists

## 🚀 Production Deployment

### Security Checklist

- [ ] Change `SECRET_KEY` to strong random value
- [ ] Set `FLASK_ENV=production`
- [ ] Set `FLASK_DEBUG=False`
- [ ] Enable HTTPS
- [ ] Set `SESSION_COOKIE_SECURE=True`
- [ ] Use environment variables, not `.env` file
- [ ] Add `.env` to `.gitignore`
- [ ] Set up proper database backups
- [ ] Configure firewall rules
- [ ] Use production WSGI server (Gunicorn, uWSGI)

### Example Production Setup

```bash
# Install Gunicorn
pip install gunicorn

# Run with Gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

## 📝 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Home page |
| `/register` | GET, POST | User registration |
| `/login` | GET, POST | User login |
| `/logout` | GET | User logout |
| `/dashboard` | GET | Student dashboard |
| `/upload_resume` | GET, POST | Resume upload |
| `/interview_setup` | GET, POST | Interview configuration |
| `/interview_chat` | GET | Chat interface |
| `/send_message` | POST | Send answer (API) |
| `/end_interview` | POST | End interview (API) |
| `/results` | GET | View results |
| `/assignments` | GET | View assignments |
| `/progress` | GET | Progress analytics |

## 🤝 Contributing

This is an educational project. Feel free to:
- Add new features
- Improve UI/UX
- Add more question banks
- Enhance AI evaluation
- Add new roles and assignments

## 📄 License

This project is created for educational purposes.

## 👥 Authors

Senior Full-Stack Development Team

## 🙏 Acknowledgments

- Google Gemini API for AI capabilities
- Chart.js for beautiful visualizations
- Flask community for excellent documentation
- Web Speech API for voice input support

## 📞 Support

For issues or questions:
1. Check the troubleshooting section
2. Review the code comments
3. Test with sample data first

## 🔄 Version History

- **v1.0** (2026-03-05)
  - Initial release
  - Complete AI interview system
  - Voice input support
  - Progress analytics
  - Responsive design

---

**Happy Interviewing! 🎯🚀**

Made with ❤️ for students preparing for their dream jobs.
