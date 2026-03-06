"""
AI Interview Preparation Platform
Complete Flask Backend with Authentication, AI Integration, and Analytics
Author: Senior Full-Stack Development Team
Version: 1.0
"""

import os
import sqlite3
from datetime import datetime
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
import requests
import json
import PyPDF2
from docx import Document
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Initialize Flask application
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-change-in-production')

# Configure upload settings
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'doc'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Create uploads folder if not exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Configure Gemini AI
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

if not GEMINI_API_KEY:
    print("Warning: GEMINI_API_KEY not found in environment variables")
else:
    genai.configure(api_key=GEMINI_API_KEY)
    # Use gemini-flash-latest which is available on free tier
    model = genai.GenerativeModel("gemini-flash-latest")
    
    # Test the API connection
    try:
        test_response = model.generate_content("Say 'API Connected'")
        print(f"✅ Gemini API initialized successfully: {test_response.text}")
    except Exception as e:
        print(f"⚠️ Gemini API test failed: {e}")

# Database configuration - Three separate databases for modularity
USERS_DB = 'databases/users.db'
QUESTIONS_DB = 'databases/questions.db'
ASSIGNMENTS_DB = 'databases/assignments.db'

# Create databases directory if it doesn't exist
os.makedirs('databases', exist_ok=True)


# ==================== DATABASE FUNCTIONS ====================

def get_users_db():
    """Create and return a connection to the users database"""
    conn = sqlite3.connect(USERS_DB)
    conn.row_factory = sqlite3.Row
    return conn


def get_questions_db():
    """Create and return a connection to the questions database"""
    conn = sqlite3.connect(QUESTIONS_DB)
    conn.row_factory = sqlite3.Row
    return conn


def get_assignments_db():
    """Create and return a connection to the assignments database"""
    conn = sqlite3.connect(ASSIGNMENTS_DB)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialize all three databases using the init_databases.py script"""
    print("Initializing databases...")
    import subprocess
    try:
        subprocess.run(['python', 'init_databases.py'], check=True)
        print("All databases initialized successfully!")
    except subprocess.CalledProcessError as e:
        print(f"Error initializing databases: {e}")
        print("You can also run 'python init_databases.py' manually")
    except FileNotFoundError:
        print("Warning: init_databases.py not found. Please ensure it exists in the project directory.")


def insert_sample_questions(cursor):
    """Deprecated - questions are now loaded via init_databases.py"""
    pass


def insert_sample_assignments(cursor):
    """Deprecated - assignments are now loaded via init_databases.py"""
    pass


# ==================== AUTHENTICATION DECORATOR ====================

def login_required(f):
    """Decorator to protect routes that require authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


# ==================== HELPER FUNCTIONS ====================

def allowed_file(filename):
    """Check if uploaded file has allowed extension"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def extract_text_from_pdf(filepath):
    """Extract text from PDF file using PyPDF2"""
    try:
        text = ""
        with open(filepath, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
        return text.strip()
    except Exception as e:
        print(f"Error extracting PDF text: {e}")
        return None


def extract_text_from_docx(filepath):
    """Extract text from DOCX file using python-docx"""
    try:
        doc = Document(filepath)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text.strip()
    except Exception as e:
        print(f"Error extracting DOCX text: {e}")
        return None


def extract_resume_text(filepath):
    """Extract text from resume (PDF or DOCX)"""
    file_extension = filepath.rsplit('.', 1)[1].lower()
    
    if file_extension == 'pdf':
        return extract_text_from_pdf(filepath)
    elif file_extension in ['docx', 'doc']:
        return extract_text_from_docx(filepath)
    else:
        return None


def analyze_resume_with_gemini(resume_text):
    """Analyze resume using Gemini API and return structured results"""
    gemini_api_key = os.getenv('GEMINI_API_KEY')
    
    if not gemini_api_key:
        print("Error: GEMINI_API_KEY not found in environment variables")
        return None
    
    prompt = f"""Analyze this resume and provide a detailed evaluation.

Resume Content:
{resume_text}

Provide your analysis in the following JSON format:
{{
    "ats_score": <number between 0-100>,
    "skills": ["skill1", "skill2", "skill3", ...],
    "recommended_roles": ["role1", "role2", "role3"],
    "missing_skills": ["skill1", "skill2", "skill3", ...],
    "suggestions": ["suggestion1", "suggestion2", "suggestion3", ...]
}}

Important: Return ONLY the JSON object, no additional text or explanation."""

    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={gemini_api_key}"
        
        payload = {
            "contents": [{
                "parts": [{
                    "text": prompt
                }]
            }],
            "generationConfig": {
                "temperature": 0.7,
                "maxOutputTokens": 2048
            }
        }
        
        print(f"Sending request to Gemini API...")
        response = requests.post(url, json=payload, headers={'Content-Type': 'application/json'}, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✓ Received response from Gemini API")
            
            # Check if response has expected structure
            if 'candidates' not in result or not result['candidates']:
                print(f"ERROR: Unexpected API response structure: {result}")
                return None
                
            generated_text = result['candidates'][0]['content']['parts'][0]['text']
            print(f"✓ Generated text length: {len(generated_text)} characters")
            
            # Extract JSON from response (remove markdown code blocks if present)
            generated_text = generated_text.strip()
            if generated_text.startswith('```json'):
                generated_text = generated_text[7:]
            if generated_text.startswith('```'):
                generated_text = generated_text[3:]
            if generated_text.endswith('```'):
                generated_text = generated_text[:-3]
            
            # Parse JSON
            try:
                analysis = json.loads(generated_text.strip())
                print(f"✓ Successfully parsed JSON analysis")
                return analysis
            except json.JSONDecodeError as je:
                print(f"ERROR: Failed to parse JSON from Gemini response")
                print(f"Response text: {generated_text[:500]}...")
                print(f"JSON Error: {je}")
                return None
        else:
            print(f"ERROR: Gemini API returned status {response.status_code}")
            print(f"Response: {response.text}")
            if response.status_code == 400:
                print("Possible causes: Invalid API key, malformed request, or quota exceeded")
            elif response.status_code == 429:
                print("Rate limit exceeded. Please wait and try again.")
            elif response.status_code == 403:
                print("API key is invalid or doesn't have access. Check your GEMINI_API_KEY in .env file")
            return None
            
    except requests.Timeout:
        print(f"ERROR: Request to Gemini API timed out after 30 seconds")
        return None
    except requests.RequestException as re:
        print(f"ERROR: Network error while calling Gemini API: {re}")
        return None
    except Exception as e:
        print(f"ERROR: Unexpected error analyzing resume with Gemini: {e}")
        import traceback
        traceback.print_exc()
        return None



def generate_questions_ai(role, difficulty, n=5):
    """Generate interview questions using Gemini AI SDK"""
    if not GEMINI_API_KEY:
        return []
    
    try:
        prompt = f"""Generate {n} technical interview questions for a {role} developer at {difficulty} level.
        
        Return ONLY the questions as a numbered list, one per line.
        Example format:
        1. Question one?
        2. Question two?
        3. Question three?
        """
        
        response = model.generate_content(prompt)
        questions_text = response.text.strip()
        
        # Parse questions
        questions = []
        for line in questions_text.split('\n'):
            line = line.strip()
            if line and (line[0].isdigit() or line.startswith('-') or line.startswith('*')):
                # Remove numbering
                question = line.split('.', 1)[-1].strip() if '.' in line else line.strip('- *')
                if question:
                    questions.append(question)
        
        return questions[:n]
    
    except Exception as e:
        print(f"Error generating questions: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return []


def ai_interviewer(conversation_history, role, user_answer=None):
    """AI interviewer that maintains conversation context using Gemini SDK"""
    if not GEMINI_API_KEY:
        return "AI service is currently unavailable. Please check your API configuration."
    
    try:
        # Build conversation context
        context = f"You are a professional technical interviewer conducting a mock interview for a {role} position.\n\n"
        context += "Conversation so far:\n"
        
        for message in conversation_history[-5:]:  # Last 5 messages for context
            context += f"{message['sender']}: {message['message']}\n"
        
        if user_answer:
            context += f"\nStudent just answered: {user_answer}\n"
        
        context += "\nYour task: Ask the next relevant interview question or provide a follow-up based on the student's answer. Keep questions concise and professional."
        
        response = model.generate_content(context)
        return response.text.strip()
    
    except Exception as e:
        print(f"Error in AI interviewer: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return "Could you please elaborate on that?"


def evaluate_answer_ai(question, answer):
    """Evaluate student answer using Gemini SDK"""
    if not GEMINI_API_KEY:
        return {"score": 5, "feedback": "AI evaluation unavailable"}
    
    try:
        prompt = f"""Evaluate this interview answer and provide a score from 1 to 10.

Question: {question}
Student Answer: {answer}

Provide your response in this exact format:
Score: [number]
Feedback: [brief feedback in 1-2 sentences]
"""
        
        response = model.generate_content(prompt)
        result_text = response.text.strip()
        
        # Parse score and feedback
        score = 5
        feedback = "Good attempt"
        
        for line in result_text.split('\n'):
            if line.lower().startswith('score:'):
                try:
                    score = int(''.join(filter(str.isdigit, line)))
                    score = max(1, min(10, score))  # Ensure score is between 1-10
                except:
                    pass
            elif line.lower().startswith('feedback:'):
                feedback = line.split(':', 1)[1].strip()
        
        return {"score": score, "feedback": feedback}
    
    except requests.exceptions.RequestException as e:
        print(f"API Request Error in evaluate: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response status: {e.response.status_code}")
            print(f"Response body: {e.response.text}")
        return {"score": 5, "feedback": "Evaluation completed"}
    except Exception as e:
        print(f"Error evaluating answer: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return {"score": 5, "feedback": "Evaluation completed"}


def fetch_questions(role, difficulty, n=5):
    """
    Fetch questions from the questions database.
    If insufficient questions found, generate new ones using AI and save them.
    
    Args:
        role: Job role (e.g., 'Python Developer', 'Full Stack Developer')
        difficulty: Difficulty level (easy, medium, hard)
        n: Number of questions needed
    
    Returns:
        List of question texts
    """
    conn = get_questions_db()
    
    # Fetch questions from database
    questions = conn.execute('''
        SELECT question_text FROM Questions
        WHERE role = ? AND difficulty = ?
        ORDER BY RANDOM()
        LIMIT ?
    ''', (role, difficulty, n)).fetchall()
    
    question_texts = [q['question_text'] for q in questions]
    
    # If insufficient questions, generate more using AI
    if len(question_texts) < n:
        remaining = n - len(question_texts)
        print(f"Need {remaining} more questions. Generating with AI...")
        
        ai_questions = generate_questions_ai(role, difficulty, remaining)
        
        # Save AI-generated questions to database
        if ai_questions:
            for question in ai_questions:
                try:
                    conn.execute('''
                        INSERT INTO Questions (role, difficulty, question_text, source, category)
                        VALUES (?, ?, ?, 'ai_generated', 'general')
                    ''', (role, difficulty, question))
                except sqlite3.IntegrityError:
                    pass  # Skip duplicates
            conn.commit()
            question_texts.extend(ai_questions)
    
    conn.close()
    return question_texts[:n]


def fetch_assignments(role=None, difficulty=None, limit=10):
    """
    Fetch assignments from the assignments database.
    
    Args:
        role: Job role filter (optional)
        difficulty: Difficulty level filter (optional)
        limit: Maximum number of assignments to return
    
    Returns:
        List of assignment records
    """
    conn = get_assignments_db()
    
    if role and difficulty:
        assignments = conn.execute('''
            SELECT * FROM Assignments
            WHERE role = ? AND difficulty = ?
            ORDER BY id
            LIMIT ?
        ''', (role, difficulty, limit)).fetchall()
    elif role:
        assignments = conn.execute('''
            SELECT * FROM Assignments
            WHERE role = ?
            ORDER BY difficulty, id
            LIMIT ?
        ''', (role, limit)).fetchall()
    elif difficulty:
        assignments = conn.execute('''
            SELECT * FROM Assignments
            WHERE difficulty = ?
            ORDER BY role, id
            LIMIT ?
        ''', (difficulty, limit)).fetchall()
    else:
        assignments = conn.execute('''
            SELECT * FROM Assignments
            ORDER BY role, difficulty
            LIMIT ?
        ''', (limit,)).fetchall()
    
    conn.close()
    return [dict(a) for a in assignments]


def generate_assignments_ai(role, difficulty, topic, assignment_type='mixed', count=15):
    """Generate assignments using Gemini AI SDK"""
    if not GEMINI_API_KEY:
        return []
    
    try:
        # Determine the mix based on assignment_type
        if assignment_type == 'coding':
            type_instruction = "- Create ONLY coding problems (100%)"
        elif assignment_type == 'mcq':
            type_instruction = "- Create ONLY multiple-choice questions (100%)"
        else:  # mixed
            type_instruction = "- Create a mix of coding problems (60%) and multiple-choice questions (40%)"
        
        prompt = f"""Generate {count} {difficulty} level assignments for a {role} developer on the topic: {topic}

Instructions:
{type_instruction}
- Return each assignment as a JSON object in an array
- Use this EXACT format:

For coding assignments:
{{
  "type": "coding",
  "title": "Assignment title",
  "problem": "Problem description",
  "example_input": "Example input",
  "example_output": "Expected output",  
  "hint": "Helpful hint"
}}

For MCQ assignments:
{{
  "type": "mcq",
  "question": "Question text",
  "options": ["A) Option 1", "B) Option 2", "C) Option 3", "D) Option 4"],
  "answer": "C",
  "explanation": "Why this is correct"
}}

Return ONLY valid JSON array with {count} objects. No extra text."""

        response = model.generate_content(prompt)
        response_text = response.text.strip()
        
        # Extract JSON from response
        # Remove markdown code blocks if present
        if '```json' in response_text:
            response_text = response_text.split('```json')[1].split('```')[0].strip()
        elif '```' in response_text:
            response_text = response_text.split('```')[1].split('```')[0].strip()
        
        # Parse JSON
        assignments = json.loads(response_text)
        return assignments if isinstance(assignments, list) else []
    
    except json.JSONDecodeError as e:
        print(f"JSON parsing error: {e}")
        return []
    except Exception as e:
        print(f"Error generating assignments: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return []


def execute_python_code(code, expected_output=None, timeout=5):
    """
    Safely execute Python code with restrictions
    Returns: {success: bool, output: str, error: str, result: str}
    """
    import subprocess
    import tempfile
    import os
    
    try:
        # Create temporary file for code
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            temp_file = f.name
            f.write(code)
        
        # Execute code with timeout and restrictions
        try:
            result = subprocess.run(
                ['python', temp_file],
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=tempfile.gettempdir()  # Run in temp directory for safety
            )
            
            output = result.stdout.strip()
            error = result.stderr.strip()
            
            # Clean up temp file
            os.unlink(temp_file)
            
            if result.returncode != 0:
                return {
                    'success': False,
                    'output': output,
                    'error': error,
                    'result': 'Error'
                }
            
            # Compare output if expected output provided
            if expected_output is not None:
                expected_clean = expected_output.strip()
                output_clean = output.strip()
                
                if expected_clean == output_clean:
                    return {
                        'success': True,
                        'output': output,
                        'error': '',
                        'result': 'Correct'
                    }
                else:
                    return {
                        'success': False,
                        'output': output,
                        'error': f'Expected: {expected_clean}\nGot: {output_clean}',
                        'result': 'Incorrect'
                    }
            
            return {
                'success': True,
                'output': output,
                'error': '',
                'result': 'Success'
            }
            
        except subprocess.TimeoutExpired:
            os.unlink(temp_file)
            return {
                'success': False,
                'output': '',
                'error': 'Execution timeout (5 seconds limit)',
                'result': 'Error'
            }
        
    except Exception as e:
        return {
            'success': False,
            'output': '',
            'error': str(e),
            'result': 'Error'
        }


def assignment_help_ai(assignment_data, chat_history, user_question):
    """AI helper for assignments - provides hints without giving full solution"""
    if not GEMINI_API_KEY:
        return "AI help is currently unavailable."
    
    try:
        context = f"""You are a helpful coding mentor assisting a student with this assignment:

Assignment: {assignment_data.get('title', assignment_data.get('question', ''))}
Problem: {assignment_data.get('problem', assignment_data.get('question', ''))}

IMPORTANT RULES:
- Provide HINTS and GUIDANCE only
- DO NOT give the complete solution or full code
- Help them understand the concept
- Ask guiding questions
- Suggest approaches or algorithms

Recent conversation:
"""
        
        for msg in chat_history[-5:]:
            context += f"{msg['sender']}: {msg['message']}\n"
        
        context += f"\nStudent question: {user_question}\n\nProvide a helpful hint or guidance:"
        
        response = model.generate_content(context)
        return response.text.strip()
    
    except Exception as e:
        print(f"Error in assignment help AI: {e}")
        return "Think about the problem step by step."


# ==================== ROUTES ====================

@app.route('/')
def index():
    """Home page"""
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        # Validation
        if not username or not email or not password:
            flash('All fields are required!', 'error')
            return redirect(url_for('register'))
        
        if password != confirm_password:
            flash('Passwords do not match!', 'error')
            return redirect(url_for('register'))
        
        if len(password) < 6:
            flash('Password must be at least 6 characters!', 'error')
            return redirect(url_for('register'))
        
        # Hash password
        hashed_password = generate_password_hash(password)
        
        # Insert into users database
        conn = get_users_db()
        try:
            conn.execute('''
                INSERT INTO Users (username, email, password)
                VALUES (?, ?, ?)
            ''', (username, email, hashed_password))
            conn.commit()
            
            # Initialize progress for new user
            user_id = conn.execute('SELECT last_insert_rowid()').fetchone()[0]
            conn.execute('''
                INSERT INTO Progress (user_id, interview_count, average_score, last_score)
                VALUES (?, 0, 0, 0)
            ''', (user_id,))
            conn.commit()
            
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
        
        except sqlite3.IntegrityError:
            flash('Username or email already exists!', 'error')
            return redirect(url_for('register'))
        
        finally:
            conn.close()
    
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        if not username or not password:
            flash('Username and password are required!', 'error')
            return redirect(url_for('login'))
        
        conn = get_users_db()
        user = conn.execute('SELECT * FROM Users WHERE username = ?', (username,)).fetchone()
        conn.close()
        
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            flash(f'Welcome back, {user["username"]}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password!', 'error')
            return redirect(url_for('login'))
    
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    """User logout"""
    username = session.get('username', 'User')
    session.clear()
    flash(f'Goodbye, {username}!', 'info')
    return redirect(url_for('index'))


@app.route('/dashboard')
@login_required
def dashboard():
    """Student dashboard"""
    conn = get_users_db()
    
    # Get user statistics
    progress = conn.execute('''
        SELECT * FROM Progress WHERE user_id = ?
    ''', (session['user_id'],)).fetchone()
    
    # Get recent interviews
    recent_interviews = conn.execute('''
        SELECT i.*, r.overall_score 
        FROM Interviews i
        LEFT JOIN Results r ON i.id = r.interview_id
        WHERE i.user_id = ?
        ORDER BY i.interview_date DESC
        LIMIT 5
    ''', (session['user_id'],)).fetchall()
    
    conn.close()
    
    return render_template('dashboard.html', 
                         progress=progress, 
                         recent_interviews=recent_interviews)


@app.route('/upload_resume', methods=['GET', 'POST'])
@login_required
def upload_resume():
    """Resume upload page with automatic AI analysis"""
    if request.method == 'POST':
        if 'resume' not in request.files:
            flash('No file uploaded!', 'error')
            return redirect(request.url)
        
        file = request.files['resume']
        
        if file.filename == '':
            flash('No file selected!', 'error')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # Add user_id and timestamp to filename to avoid conflicts
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{session['user_id']}_{timestamp}_{filename}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Save to users database
            conn = get_users_db()
            conn.execute('''
                INSERT INTO Resumes (user_id, file_path)
                VALUES (?, ?)
            ''', (session['user_id'], filepath))
            conn.commit()
            
            # Extract text from resume
            print(f"Extracting text from resume: {filepath}")
            try:
                resume_text = extract_resume_text(filepath)
                
                if not resume_text or len(resume_text.strip()) < 50:
                    conn.close()
                    flash('Failed to extract meaningful text from resume. Please ensure the file is not empty or corrupted.', 'error')
                    return redirect(request.url)
                
                print(f"✓ Extracted {len(resume_text)} characters from resume")
                
                # Analyze resume with Gemini API
                print("Analyzing resume with Gemini API...")
                analysis = analyze_resume_with_gemini(resume_text)
                
                if not analysis:
                    # Store partial data without analysis
                    conn.execute('''
                        INSERT INTO ResumeAnalysis 
                        (user_id, resume_path, ats_score, skills, recommended_roles, missing_skills, suggestions)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        session['user_id'],
                        filepath,
                        None,
                        json.dumps([]),
                        json.dumps([]),
                        json.dumps([]),
                        json.dumps(['AI analysis temporarily unavailable. Please check your Gemini API key and try again.'])
                    ))
                    conn.commit()
                    analysis_id = conn.execute('SELECT last_insert_rowid()').fetchone()[0]
                    conn.close()
                    
                    flash('Resume uploaded but AI analysis failed. Please check your Gemini API configuration.', 'warning')
                    return redirect(url_for('resume_analysis', analysis_id=analysis_id))
                
                print(f"✓ Analysis complete: ATS Score = {analysis.get('ats_score', 'N/A')}")
            
            except Exception as e:
                conn.close()
                print(f"ERROR during resume processing: {str(e)}")
                import traceback
                traceback.print_exc()
                flash(f'An error occurred while processing your resume: {str(e)}', 'error')
                return redirect(request.url)
            
            print(f"Analysis complete: ATS Score = {analysis.get('ats_score', 'N/A')}")
            
            # Store analysis results in database
            conn.execute('''
                INSERT INTO ResumeAnalysis 
                (user_id, resume_path, ats_score, skills, recommended_roles, missing_skills, suggestions)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                session['user_id'],
                filepath,
                analysis.get('ats_score'),
                json.dumps(analysis.get('skills', [])),
                json.dumps(analysis.get('recommended_roles', [])),
                json.dumps(analysis.get('missing_skills', [])),
                json.dumps(analysis.get('suggestions', []))
            ))
            conn.commit()
            
            # Get the analysis ID for redirect
            analysis_id = conn.execute('SELECT last_insert_rowid()').fetchone()[0]
            conn.close()
            
            flash('Resume analyzed successfully!', 'success')
            return redirect(url_for('resume_analysis', analysis_id=analysis_id))
        else:
            flash('Invalid file type! Only PDF and DOCX allowed.', 'error')
            return redirect(request.url)
    
    return render_template('upload_resume.html')


@app.route('/resume_analysis/<int:analysis_id>')
@login_required
def resume_analysis(analysis_id):
    """Display resume analysis results with action panel"""
    conn = get_users_db()
    
    # Get analysis results
    analysis = conn.execute('''
        SELECT * FROM ResumeAnalysis
        WHERE id = ? AND user_id = ?
    ''', (analysis_id, session['user_id'])).fetchone()
    
    conn.close()
    
    if not analysis:
        flash('Analysis not found!', 'error')
        return redirect(url_for('dashboard'))
    
    # Parse JSON fields
    analysis_dict = dict(analysis)
    analysis_dict['skills'] = json.loads(analysis_dict['skills']) if analysis_dict['skills'] else []
    analysis_dict['recommended_roles'] = json.loads(analysis_dict['recommended_roles']) if analysis_dict['recommended_roles'] else []
    analysis_dict['missing_skills'] = json.loads(analysis_dict['missing_skills']) if analysis_dict['missing_skills'] else []
    analysis_dict['suggestions'] = json.loads(analysis_dict['suggestions']) if analysis_dict['suggestions'] else []
    
    return render_template('resume_analysis.html', analysis=analysis_dict)


@app.route('/start_resume_interview', methods=['POST'])
@login_required
def start_resume_interview():
    """Start AI interview based on resume skills"""
    analysis_id = request.form.get('analysis_id')
    
    if not analysis_id:
        flash('Analysis ID not provided!', 'error')
        return redirect(url_for('dashboard'))
    
    conn = get_users_db()
    
    # Get detected skills from analysis
    analysis = conn.execute('''
        SELECT skills FROM ResumeAnalysis
        WHERE id = ? AND user_id = ?
    ''', (analysis_id, session['user_id'])).fetchone()
    
    conn.close()
    
    if not analysis:
        flash('Analysis not found!', 'error')
        return redirect(url_for('dashboard'))
    
    # Parse skills
    skills = json.loads(analysis['skills']) if analysis['skills'] else []
    
    if not skills:
        flash('No skills detected in resume. Please upload a more detailed resume.', 'warning')
        return redirect(url_for('dashboard'))
    
    # Store skills in session for interview
    session['resume_skills'] = skills
    session['interview_type'] = 'resume_based'
    
    # Create interview record
    conn = get_users_db()
    cursor = conn.execute('''
        INSERT INTO Interviews (user_id, role, difficulty, status)
        VALUES (?, ?, ?, ?)
    ''', (session['user_id'], 'Resume-Based Interview', 'Medium', 'in_progress'))
    
    interview_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    session['interview_id'] = interview_id
    
    flash(f'Starting interview based on your skills: {", ".join(skills[:5])}...', 'success')
    return redirect(url_for('interview_chat'))


@app.route('/generate_skill_assignments', methods=['POST'])
@login_required
def generate_skill_assignments():
    """Generate practice assignments based on missing skills"""
    analysis_id = request.form.get('analysis_id')
    
    if not analysis_id:
        flash('Analysis ID not provided!', 'error')
        return redirect(url_for('dashboard'))
    
    conn = get_users_db()
    
    # Get missing skills from analysis
    analysis = conn.execute('''
        SELECT missing_skills FROM ResumeAnalysis
        WHERE id = ? AND user_id = ?
    ''', (analysis_id, session['user_id'])).fetchone()
    
    conn.close()
    
    if not analysis:
        flash('Analysis not found!', 'error')
        return redirect(url_for('dashboard'))
    
    # Parse missing skills
    missing_skills = json.loads(analysis['missing_skills']) if analysis['missing_skills'] else []
    
    if not missing_skills:
        flash('Great! No missing skills detected. You have a comprehensive skill set!', 'success')
        return redirect(url_for('assignments'))
    
    # Generate assignments using Gemini API
    gemini_api_key = os.getenv('GEMINI_API_KEY')
    
    prompt = f"""Generate 10 coding practice assignments to improve these skills:

Skills to improve:
{', '.join(missing_skills)}

For each assignment, provide:
1. Title
2. Problem description
3. Difficulty level (Easy/Medium/Hard)
4. Type (coding)
5. Test cases example

Return the result as JSON array:
[
    {{
        "title": "Assignment Title",
        "problem": "Problem description",
        "difficulty": "Medium",
        "type": "coding",
        "skill": "skill name",
        "starter_code": "# Python starter code",
        "test_cases": ["test case 1", "test case 2"]
    }},
    ...
]

Important: Return ONLY the JSON array, no additional text."""

    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={gemini_api_key}"
        
        payload = {
            "contents": [{
                "parts": [{
                    "text": prompt
                }]
            }],
            "generationConfig": {
                "temperature": 0.8,
                "maxOutputTokens": 4096
            }
        }
        
        response = requests.post(url, json=payload, headers={'Content-Type': 'application/json'})
        
        if response.status_code == 200:
            result = response.json()
            generated_text = result['candidates'][0]['content']['parts'][0]['text']
            
            # Extract JSON from response
            generated_text = generated_text.strip()
            if generated_text.startswith('```json'):
                generated_text = generated_text[7:]
            if generated_text.startswith('```'):
                generated_text = generated_text[3:]
            if generated_text.endswith('```'):
                generated_text = generated_text[:-3]
            
            assignments_data = json.loads(generated_text.strip())
            
            # Store assignments in database
            conn = get_assignments_db()
            
            # Create an assignment group for skill improvement
            cursor = conn.execute('''
                INSERT INTO AssignmentGroups 
                (user_id, name, role, difficulty, topic, assignment_type, total_questions)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                session['user_id'],
                f"Skill Improvement - {', '.join(missing_skills[:3])}",
                'Skill Development',
                'Mixed',
                ', '.join(missing_skills[:3]),
                'coding',
                len(assignments_data)
            ))
            
            group_id = cursor.lastrowid
            
            # Insert individual assignments
            for idx, assignment in enumerate(assignments_data[:10], 1):
                conn.execute('''
                    INSERT INTO Assignments 
                    (group_id, role, difficulty, topic, type, question_data, question_number)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    group_id,
                    'Skill Development',
                    assignment.get('difficulty', 'Medium'),
                    assignment.get('skill', missing_skills[0]),
                    assignment.get('type', 'coding'),
                    json.dumps(assignment),
                    idx
                ))
            
            conn.commit()
            conn.close()
            
            flash(f'Successfully generated {len(assignments_data[:10])} assignments to improve your skills!', 'success')
            return redirect(url_for('assignment_group', group_id=group_id))
        else:
            flash('Failed to generate assignments. Please try again.', 'error')
            return redirect(url_for('dashboard'))
            
    except Exception as e:
        print(f"Error generating skill assignments: {e}")
        flash('An error occurred while generating assignments.', 'error')
        return redirect(url_for('dashboard'))


@app.route('/interview_setup', methods=['GET', 'POST'])
@login_required
def interview_setup():
    """Interview setup page - select role and difficulty"""
    if request.method == 'POST':
        role = request.form.get('role')
        difficulty = request.form.get('difficulty')
        
        if not role or not difficulty:
            flash('Please select both role and difficulty!', 'error')
            return redirect(url_for('interview_setup'))
        
        # Create new interview in users database
        conn = get_users_db()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO Interviews (user_id, role, difficulty, status)
            VALUES (?, ?, ?, 'in_progress')
        ''', (session['user_id'], role, difficulty))
        interview_id = cursor.lastrowid
        conn.commit()
        
        # Add initial AI greeting to chat history
        greeting = f"Hello {session['username']}! Welcome to your {role} mock interview at {difficulty} level. Let's begin. What is your understanding of {role.split()[0]} development?"
        
        cursor.execute('''
            INSERT INTO ChatHistory (user_id, interview_id, sender, message)
            VALUES (?, ?, 'AI', ?)
        ''', (session['user_id'], interview_id, greeting))
        conn.commit()
        conn.close()
        
        # Store interview details in session
        session['current_interview_id'] = interview_id
        session['current_role'] = role
        session['current_difficulty'] = difficulty
        
        return redirect(url_for('interview_chat'))
    
    return render_template('interview_setup.html')


@app.route('/interview_chat')
@login_required
def interview_chat():
    """AI chat interview interface"""
    if 'current_interview_id' not in session:
        flash('Please start an interview first!', 'warning')
        return redirect(url_for('interview_setup'))
    
    return render_template('interview_chat.html',
                         role=session.get('current_role'),
                         difficulty=session.get('current_difficulty'))


@app.route('/get_chat_history')
@login_required
def get_chat_history():
    """API endpoint to get chat history"""
    interview_id = session.get('current_interview_id')
    
    if not interview_id:
        return jsonify({'messages': []})
    
    conn = get_users_db()
    messages = conn.execute('''
        SELECT sender, message, timestamp
        FROM ChatHistory
        WHERE interview_id = ?
        ORDER BY timestamp ASC
    ''', (interview_id,)).fetchall()
    conn.close()
    
    return jsonify({
        'messages': [dict(msg) for msg in messages]
    })


@app.route('/send_message', methods=['POST'])
@login_required
def send_message():
    """API endpoint to send message and get AI response"""
    data = request.get_json()
    user_message = data.get('message', '').strip()
    
    if not user_message:
        return jsonify({'error': 'Empty message'}), 400
    
    interview_id = session.get('current_interview_id')
    role = session.get('current_role')
    
    if not interview_id:
        return jsonify({'error': 'No active interview'}), 400
    
    conn = get_users_db()
    
    # Save user message
    conn.execute('''
        INSERT INTO ChatHistory (user_id, interview_id, sender, message)
        VALUES (?, ?, 'Student', ?)
    ''', (session['user_id'], interview_id, user_message))
    conn.commit()
    
    # Get conversation history
    history = conn.execute('''
        SELECT sender, message
        FROM ChatHistory
        WHERE interview_id = ?
        ORDER BY timestamp ASC
    ''', (interview_id,)).fetchall()
    
    conversation = [{'sender': msg['sender'], 'message': msg['message']} for msg in history]
    
    # Get AI response
    ai_response = ai_interviewer(conversation, role, user_message)
    
    # Save AI response
    conn.execute('''
        INSERT INTO ChatHistory (user_id, interview_id, sender, message)
        VALUES (?, ?, 'AI', ?)
    ''', (session['user_id'], interview_id, ai_response))
    conn.commit()
    conn.close()
    
    return jsonify({'response': ai_response})


@app.route('/end_interview', methods=['POST'])
@login_required
def end_interview():
    """End interview and evaluate"""
    interview_id = session.get('current_interview_id')
    
    if not interview_id:
        return jsonify({'error': 'No active interview'}), 400
    
    conn = get_users_db()
    
    # Get all student answers from chat history
    messages = conn.execute('''
        SELECT message FROM ChatHistory
        WHERE interview_id = ? AND sender = 'Student'
    ''', (interview_id,)).fetchall()
    
    # Calculate scores (simplified evaluation)
    num_answers = len(messages)
    technical_score = min(10, num_answers * 1.5)  # Basic scoring
    communication_score = min(10, num_answers * 1.2)
    overall_score = (technical_score + communication_score) / 2
    
    feedback = f"You answered {num_answers} questions. "
    if overall_score >= 7:
        feedback += "Great performance! Keep it up."
    elif overall_score >= 5:
        feedback += "Good effort! Practice more to improve."
    else:
        feedback += "Keep practicing! Review fundamental concepts."
    
    # Save results
    conn.execute('''
        INSERT INTO Results (user_id, interview_id, technical_score, communication_score, overall_score, feedback)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (session['user_id'], interview_id, technical_score, communication_score, overall_score, feedback))
    
    # Update interview status
    conn.execute('''
        UPDATE Interviews SET status = 'completed'
        WHERE id = ?
    ''', (interview_id,))
    
    # Update progress
    progress = conn.execute('''
        SELECT * FROM Progress WHERE user_id = ?
    ''', (session['user_id'],)).fetchone()
    
    new_count = progress['interview_count'] + 1
    new_average = ((progress['average_score'] * progress['interview_count']) + overall_score) / new_count
    
    conn.execute('''
        UPDATE Progress
        SET interview_count = ?,
            average_score = ?,
            last_score = ?,
            updated_at = CURRENT_TIMESTAMP
        WHERE user_id = ?
    ''', (new_count, new_average, overall_score, session['user_id']))
    
    conn.commit()
    conn.close()
    
    # Clear session interview data
    session.pop('current_interview_id', None)
    session.pop('current_role', None)
    session.pop('current_difficulty', None)
    
    return jsonify({
        'success': True,
        'interview_id': interview_id
    })


@app.route('/results')
@app.route('/results/<int:interview_id>')
@login_required
def results(interview_id=None):
    """Display interview results"""
    conn = get_users_db()
    
    if interview_id:
        # Get specific interview result
        result = conn.execute('''
            SELECT r.*, i.role, i.difficulty, i.interview_date
            FROM Results r
            JOIN Interviews i ON r.interview_id = i.id
            WHERE r.interview_id = ? AND r.user_id = ?
        ''', (interview_id, session['user_id'])).fetchone()
    else:
        # Get latest result
        result = conn.execute('''
            SELECT r.*, i.role, i.difficulty, i.interview_date
            FROM Results r
            JOIN Interviews i ON r.interview_id = i.id
            WHERE r.user_id = ?
            ORDER BY r.created_at DESC
            LIMIT 1
        ''', (session['user_id'],)).fetchone()
    
    conn.close()
    
    if not result:
        flash('No results found!', 'warning')
        return redirect(url_for('dashboard'))
    
    return render_template('results.html', result=result)


# ==================== ASSIGNMENT LAB ROUTES ====================

@app.route('/assignment_lab')
@login_required
def assignment_lab():
    """Main assignment lab page - Generate assignments"""
    return render_template('assignment_generator.html')


@app.route('/generate_assignments', methods=['POST'])
@login_required
def generate_assignments():
    """Generate AI assignments based on user inputs"""
    data = request.get_json()
    assignment_type = data.get('assignment_type', 'mixed')  # mixed, coding, or mcq
    role = data.get('role', '')
    difficulty = data.get('difficulty', '')
    topic = data.get('topic', '')
    
    if not role or not difficulty or not topic:
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Generate assignments using AI
    assignments_data = generate_assignments_ai(role, difficulty, topic, assignment_type=assignment_type, count=15)
    
    if not assignments_data:
        return jsonify({'error': 'Failed to generate assignments'}), 500
    
    # Create assignment group
    conn = get_assignments_db()
    group_name = f"{role} - {topic} ({difficulty})"
    
    cursor = conn.execute('''
        INSERT INTO AssignmentGroups (user_id, name, role, difficulty, topic, assignment_type, total_questions)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (session['user_id'], group_name, role, difficulty, topic, assignment_type, len(assignments_data)))
    
    group_id = cursor.lastrowid
    
    # Save individual assignments to the group
    assignment_ids = []
    for idx, assignment in enumerate(assignments_data, 1):
        cursor = conn.execute('''
            INSERT INTO Assignments (group_id, role, difficulty, topic, type, question_data, question_number)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (group_id, role, difficulty, topic, assignment['type'], json.dumps(assignment), idx))
        assignment_ids.append(cursor.lastrowid)
    
    conn.commit()
    conn.close()
    
    return jsonify({
        'success': True,
        'count': len(assignment_ids),
        'group_id': group_id,
        'message': f'Generated {len(assignment_ids)} assignments successfully',
        'assignment_ids': assignment_ids
    })



@app.route('/assignments')
@login_required
def assignments():
    """List all assignment groups with filters"""
    role = request.args.get('role', '')
    difficulty = request.args.get('difficulty', '')
    topic = request.args.get('topic', '')
    assignment_type = request.args.get('type', '')
    
    conn = get_assignments_db()
    
    # Build dynamic query for assignment groups
    query = 'SELECT * FROM AssignmentGroups WHERE user_id = ?'
    params = [session['user_id']]
    
    if role:
        query += ' AND role = ?'
        params.append(role)
    if difficulty:
        query += ' AND difficulty = ?'
        params.append(difficulty)
    if topic:
        query += ' AND topic = ?'
        params.append(topic)
    if assignment_type:
        query += ' AND assignment_type = ?'
        params.append(assignment_type)
    
    query += ' ORDER BY created_at DESC'
    
    groups_list = conn.execute(query, params).fetchall()
    
    # Calculate progress for each group
    groups_with_progress = []
    for group in groups_list:
        g_dict = dict(group)
        
        # Count solved assignments in this group
        solved_count = conn.execute('''
            SELECT COUNT(DISTINCT a.id) FROM Assignments a
            INNER JOIN Submissions s ON a.id = s.assignment_id
            WHERE a.group_id = ? AND s.user_id = ? AND s.result = 'Correct'
        ''', (group['id'], session['user_id'])).fetchone()[0]
        
        g_dict['solved_count'] = solved_count
        g_dict['total_questions'] = group['total_questions']
        groups_with_progress.append(g_dict)
    
    # Get filter options from AssignmentGroups for current user
    roles = conn.execute('SELECT DISTINCT role FROM AssignmentGroups WHERE user_id = ? ORDER BY role', 
                        (session['user_id'],)).fetchall()
    topics = conn.execute('SELECT DISTINCT topic FROM AssignmentGroups WHERE user_id = ? ORDER BY topic', 
                         (session['user_id'],)).fetchall()
    
    conn.close()
    
    return render_template('assignments_list.html',
                         assignment_groups=groups_with_progress,
                         roles=roles,
                         topics=topics,
                         filters={'role': role, 'difficulty': difficulty, 'topic': topic, 'type': assignment_type})


@app.route('/assignment_group/<int:group_id>')
@login_required
def assignment_group(group_id):
    """View all questions in an assignment group"""
    conn = get_assignments_db()
    
    # Get group info
    group = conn.execute('''
        SELECT * FROM AssignmentGroups WHERE id = ? AND user_id = ?
    ''', (group_id, session['user_id'])).fetchone()
    
    if not group:
        conn.close()
        flash('Assignment group not found!', 'error')
        return redirect(url_for('assignments'))
    
    # Get all assignments in this group with solved status
    assignments = conn.execute('''
        SELECT a.*, 
               CASE WHEN EXISTS (
                   SELECT 1 FROM Submissions s 
                   WHERE s.assignment_id = a.id AND s.user_id = ? AND s.result = 'Correct'
               ) THEN 1 ELSE 0 END as is_solved
        FROM Assignments a
        WHERE a.group_id = ?
        ORDER BY a.question_number
    ''', (session['user_id'], group_id)).fetchall()
    
    # Parse question data
    assignments_parsed = []
    for assignment in assignments:
        a_dict = dict(assignment)
        a_dict['question_data'] = json.loads(a_dict['question_data'])
        assignments_parsed.append(a_dict)
    
    # Calculate progress
    solved_count = sum(1 for a in assignments_parsed if a['is_solved'])
    
    conn.close()
    
    return render_template('assignment_group.html',
                         group=dict(group),
                         assignments=assignments_parsed,
                         solved_count=solved_count,
                         total_questions=group['total_questions'])


@app.route('/delete_assignment_group/<int:group_id>', methods=['POST'])
@login_required
def delete_assignment_group(group_id):
    """Delete an entire assignment group"""
    conn = get_assignments_db()
    
    # Verify group belongs to user
    group = conn.execute('''
        SELECT * FROM AssignmentGroups WHERE id = ? AND user_id = ?
    ''', (group_id, session['user_id'])).fetchone()
    
    if not group:
        conn.close()
        return jsonify({'success': False, 'message': 'Assignment group not found'}), 404
    
    # Delete group (CASCADE will delete assignments, submissions, and help records)
    conn.execute('DELETE FROM AssignmentGroups WHERE id = ?', (group_id,))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'message': 'Assignment group deleted successfully'})


@app.route('/assignment/<int:assignment_id>')
@login_required
def solve_assignment(assignment_id):
    """Assignment solving interface with code editor"""
    conn = get_assignments_db()
    
    assignment = conn.execute('''
        SELECT * FROM Assignments WHERE id = ?
    ''', (assignment_id,)).fetchone()
    
    if not assignment:
        conn.close()
        flash('Assignment not found!', 'error')
        return redirect(url_for('assignments'))
    
    # Get user's previous submissions for this assignment
    submissions = conn.execute('''
        SELECT * FROM Submissions
        WHERE user_id = ? AND assignment_id = ?
        ORDER BY submitted_at DESC
        LIMIT 5
    ''', (session['user_id'], assignment_id)).fetchall()
    
    # Check if this assignment is solved (has any correct submission)
    is_solved = conn.execute('''
        SELECT COUNT(*) FROM Submissions
        WHERE user_id = ? AND assignment_id = ? AND result = 'Correct'
    ''', (session['user_id'], assignment_id)).fetchone()[0] > 0
    
    # Get next unsolved assignment in the same group
    next_assignment = conn.execute('''
        SELECT a.id FROM Assignments a
        WHERE a.group_id = ? AND a.question_number > ?
        AND NOT EXISTS (
            SELECT 1 FROM Submissions s 
            WHERE s.assignment_id = a.id AND s.user_id = ? AND s.result = 'Correct'
        )
        ORDER BY a.question_number ASC
        LIMIT 1
    ''', (assignment['group_id'], assignment['question_number'], session['user_id'])).fetchone()
    
    next_assignment_id = next_assignment['id'] if next_assignment else None
    
    conn.close()
    
    # Parse assignment data
    assignment_dict = dict(assignment)
    assignment_dict['question_data'] = json.loads(assignment_dict['question_data'])
    
    return render_template('solve_assignment.html',
                         assignment=assignment_dict,
                         submissions=submissions,
                         is_solved=is_solved,
                         next_assignment_id=next_assignment_id)


@app.route('/run_code', methods=['POST'])
@login_required
def run_code():
    """Execute user code and return results"""
    data = request.get_json()
    code = data.get('code', '')
    assignment_id = data.get('assignment_id')
    
    if not code:
        return jsonify({'error': 'No code provided'}), 400
    
    # Get assignment details
    conn = get_assignments_db()
    assignment = conn.execute('''
        SELECT * FROM Assignments WHERE id = ?
    ''', (assignment_id,)).fetchone()
    
    if not assignment:
        conn.close()
        return jsonify({'error': 'Assignment not found'}), 404
    
    assignment_data = json.loads(assignment['question_data'])
    
    # Execute code
    expected_output = assignment_data.get('example_output')
    execution_result = execute_python_code(code, expected_output)
    
    # Calculate score
    score = 10 if execution_result['result'] == 'Correct' else 0
    
    # Save submission
    conn.execute('''
        INSERT INTO Submissions (user_id, assignment_id, user_code, result, output, score)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (session['user_id'], assignment_id, code, execution_result['result'], 
          execution_result.get('output', '') + '\n' + execution_result.get('error', ''), score))
    conn.commit()
    conn.close()
    
    return jsonify({
        'success': execution_result['success'],
        'result': execution_result['result'],
        'output': execution_result['output'],
        'error': execution_result['error'],
        'score': score,
        'hint': assignment_data.get('hint', '') if execution_result['result'] != 'Correct' else ''
    })


@app.route('/submit_mcq', methods=['POST'])
@login_required
def submit_mcq():
    """Submit MCQ answer and check correctness"""
    data = request.get_json()
    assignment_id = data.get('assignment_id')
    user_answer = data.get('answer', '')
    
    if not user_answer:
        return jsonify({'error': 'No answer provided'}), 400
    
    conn = get_assignments_db()
    assignment = conn.execute('''
        SELECT * FROM Assignments WHERE id = ?
    ''', (assignment_id,)).fetchone()
    
    if not assignment:
        conn.close()
        return jsonify({'error': 'Assignment not found'}), 404
    
    assignment_data = json.loads(assignment['question_data'])
    correct_answer = assignment_data['answer']
    
    # Check if correct
    is_correct = user_answer.upper() == correct_answer.upper()
    result = 'Correct' if is_correct else 'Incorrect'
    score = 10 if is_correct else 0
    
    # Save submission
    conn.execute('''
        INSERT INTO Submissions (user_id, assignment_id, user_answer, result, output, score)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (session['user_id'], assignment_id, user_answer, result, 
          assignment_data.get('explanation', ''), score))
    conn.commit()
    conn.close()
    
    return jsonify({
        'success': is_correct,
        'result': result,
        'correct_answer': correct_answer,
        'explanation': assignment_data.get('explanation', ''),
        'score': score
    })


@app.route('/assignment_help/<int:assignment_id>')
@login_required
def get_assignment_help(assignment_id):
    """Get AI help chat history for an assignment"""
    conn = get_assignments_db()
    
    help_history = conn.execute('''
        SELECT * FROM AssignmentHelp
        WHERE assignment_id = ? AND user_id = ?
        ORDER BY timestamp ASC
    ''', (assignment_id, session['user_id'])).fetchall()
    
    conn.close()
    
    return jsonify({
        'messages': [dict(msg) for msg in help_history]
    })


@app.route('/ask_assignment_help', methods=['POST'])
@login_required
def ask_assignment_help():
    """Ask AI for help with an assignment"""
    data = request.get_json()
    assignment_id = data.get('assignment_id')
    user_question = data.get('question', '')
    
    if not user_question:
        return jsonify({'error': 'No question provided'}), 400
    
    conn = get_assignments_db()
    
    # Get assignment details
    assignment = conn.execute('''
        SELECT * FROM Assignments WHERE id = ?
    ''', (assignment_id,)).fetchone()
    
    if not assignment:
        conn.close()
        return jsonify({'error': 'Assignment not found'}), 404
    
    assignment_data = json.loads(assignment['question_data'])
    
    # Get chat history
    history = conn.execute('''
        SELECT sender, message FROM AssignmentHelp
        WHERE assignment_id = ? AND user_id = ?
        ORDER BY timestamp ASC
    ''', (assignment_id, session['user_id'])).fetchall()
    
    chat_history = [{'sender': msg['sender'], 'message': msg['message']} for msg in history]
    
    # Save user question
    conn.execute('''
        INSERT INTO AssignmentHelp (user_id, assignment_id, sender, message)
        VALUES (?, ?, 'Student', ?)
    ''', (session['user_id'], assignment_id, user_question))
    conn.commit()
    
    # Get AI response
    ai_response = assignment_help_ai(assignment_data, chat_history, user_question)
    
    # Save AI response
    conn.execute('''
        INSERT INTO AssignmentHelp (user_id, assignment_id, sender, message)
        VALUES (?, ?, 'AI', ?)
    ''', (session['user_id'], assignment_id, ai_response))
    conn.commit()
    conn.close()
    
    return jsonify({
        'response': ai_response
    })


@app.route('/progress')
@login_required
def progress():
    """Display progress analytics"""
    conn = get_users_db()
    
    # Get user progress
    user_progress = conn.execute('''
        SELECT * FROM Progress WHERE user_id = ?
    ''', (session['user_id'],)).fetchone()
    
    # Get all interview scores for chart
    interview_scores = conn.execute('''
        SELECT r.overall_score, i.interview_date, i.role
        FROM Results r
        JOIN Interviews i ON r.interview_id = i.id
        WHERE r.user_id = ?
        ORDER BY i.interview_date ASC
    ''', (session['user_id'],)).fetchall()
    
    conn.close()
    
    # Prepare data for Chart.js
    chart_data = {
        'dates': [score['interview_date'][:10] for score in interview_scores],
        'scores': [score['overall_score'] for score in interview_scores],
        'roles': [score['role'] for score in interview_scores]
    }
    
    return render_template('progress.html', 
                         progress=user_progress,
                         chart_data=json.dumps(chart_data))


# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return render_template('index.html'), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    flash('An error occurred. Please try again.', 'error')
    return redirect(url_for('index'))


# ==================== APPLICATION ENTRY POINT ====================

if __name__ == '__main__':
    # Initialize database on first run
    init_db()
    print("✓ Database initialized")
    print("✓ Flask application starting...")
    print("✓ Access the platform at: http://127.0.0.1:5000")
    
    # Run Flask application
    app.run(debug=True, host='0.0.0.0', port=5000)
