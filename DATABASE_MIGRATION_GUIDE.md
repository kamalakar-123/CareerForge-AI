# Database Migration Guide

## Overview
This guide explains the database architecture refactoring from a single monolithic database to three modular databases for better separation of concerns and scalability.

## Architecture Changes

### Before Refactoring
- **Single Database**: `database.db`
- All tables (Users, Questions, Assignments, Interviews, Results, etc.) in one database
- Single connection function: `get_db_connection()`

### After Refactoring
- **Three Separate Databases**:
  1. **users.db** - Authentication, interviews, results, progress
  2. **questions.db** - Interview question bank
  3. **assignments.db** - Coding assignments

## Database Structure

### 1. users.db (Authentication & Interview Data)
```
databases/users.db
├── Users (id, username, email, password, created_at)
├── Resumes (id, user_id, file_path, uploaded_at)
├── Interviews (id, user_id, role, difficulty, interview_date, status)
├── Results (id, user_id, interview_id, technical_score, communication_score, overall_score, feedback)
├── ChatHistory (id, user_id, interview_id, sender, message, timestamp)
└── Progress (id, user_id, interview_count, average_score, last_score, updated_at)
```

### 2. questions.db (Question Bank)
```
databases/questions.db
└── Questions (id, role, difficulty, question_text, expected_keywords, category, source, created_at)
```
- Pre-loaded with 100+ questions
- Supports AI-generated questions (automatically saved)
- Indexed on: role, difficulty, category

### 3. assignments.db (Coding Assignments)
```
databases/assignments.db
└── Assignments (id, role, difficulty, assignment_text, solution_hint, created_at)
```
- Pre-loaded with 30+ assignments
- Read-only for students
- Indexed on: role, difficulty

## Database Connection Functions

### New Functions in app.py
```python
# Three separate database connection functions
def get_users_db():
    """Connect to users database (authentication, interviews, results)"""
    conn = sqlite3.connect('databases/users.db')
    conn.row_factory = sqlite3.Row
    return conn

def get_questions_db():
    """Connect to questions database (question bank)"""
    conn = sqlite3.connect('databases/questions.db')
    conn.row_factory = sqlite3.Row
    return conn

def get_assignments_db():
    """Connect to assignments database (coding assignments)"""
    conn = sqlite3.connect('databases/assignments.db')
    conn.row_factory = sqlite3.Row
    return conn
```

## Helper Functions

### fetch_questions(role, difficulty, n=5)
- **Purpose**: Fetch questions from questions.db
- **Behavior**: 
  - Fetches questions from database first
  - If insufficient, generates new questions using Gemini AI
  - Automatically saves AI-generated questions back to database
- **Usage**: 
  ```python
  questions = fetch_questions('Python Developer', 'medium', 5)
  ```

### fetch_assignments(role=None, difficulty=None, limit=10)
- **Purpose**: Fetch assignments from assignments.db
- **Behavior**: Always retrieves from database (no AI generation)
- **Usage**:
  ```python
  # Get all Python assignments
  assignments = fetch_assignments(role='Python Developer')
  
  # Get all medium difficulty assignments
  assignments = fetch_assignments(difficulty='medium')
  
  # Get Python medium assignments
  assignments = fetch_assignments('Python Developer', 'medium')
  ```

## Route Updates

Each route now uses the appropriate database connection:

### Routes Using get_users_db()
- `/register` - User registration
- `/login` - User authentication
- `/dashboard` - User statistics and progress
- `/upload_resume` - Resume file uploads
- `/interview_setup` - Create new interview
- `/interview_chat` - Chat interface
- `/get_chat_history` - Retrieve chat messages
- `/send_message` - Save chat messages
- `/end_interview` - Save results and update progress
- `/results` - Display interview results
- `/progress` - Display analytics

### Routes Using get_questions_db()
- Via `fetch_questions()` helper function
- AI-generated questions automatically saved here

### Routes Using get_assignments_db()
- `/assignments` - Display coding assignments
- Via `fetch_assignments()` helper function

## Initialization

### Method 1: Using init_databases.py (Recommended)
```bash
python init_databases.py
```
This script:
- Creates all three databases
- Executes schema files (users_schema.sql, questions_schema.sql, assignments_schema.sql)
- Populates questions.db with 100+ questions
- Populates assignments.db with 30+ assignments

### Method 2: Automatic on First Run
When you run `python app.py`, it calls `init_db()` which automatically runs `init_databases.py`.

## Migration from Old Database

If you have an existing `database.db`, you can migrate data:

### Option 1: Manual Migration Script
```python
import sqlite3

# Connect to old database
old_conn = sqlite3.connect('database.db')
old_conn.row_factory = sqlite3.Row

# Connect to new databases
users_conn = sqlite3.connect('databases/users.db')
questions_conn = sqlite3.connect('databases/questions.db')
assignments_conn = sqlite3.connect('databases/assignments.db')

# Migrate Users, Resumes, Interviews, Results, ChatHistory, Progress
for table in ['Users', 'Resumes', 'Interviews', 'Results', 'ChatHistory', 'Progress']:
    rows = old_conn.execute(f'SELECT * FROM {table}').fetchall()
    # Insert into users_conn...

# Migrate Questions
rows = old_conn.execute('SELECT * FROM Questions').fetchall()
# Insert into questions_conn...

# Migrate Assignments
rows = old_conn.execute('SELECT * FROM Assignments').fetchall()
# Insert into assignments_conn...

# Close connections
old_conn.close()
users_conn.close()
questions_conn.close()
assignments_conn.close()
```

### Option 2: Fresh Start (Recommended)
- Backup old database: `mv database.db database.db.backup`
- Run initialization: `python init_databases.py`
- Users will need to re-register (clean slate)

## Benefits of New Architecture

### 1. **Separation of Concerns**
- User data isolated from question bank
- Assignments can be updated independently
- Better security (can apply different permissions per database)

### 2. **Scalability**
- Each database can be scaled independently
- Questions database can be shared across multiple instances
- Easier to migrate to different database systems later

### 3. **Maintainability**
- Clearer code structure
- Easier to debug (know which database to check)
- Better organized schema files

### 4. **Performance**
- Indexes optimized per database purpose
- Reduced lock contention
- Faster queries (smaller databases)

### 5. **Backup & Recovery**
- Can backup/restore databases independently
- Question bank can be version-controlled
- User data can be backed up more frequently

## Testing the Refactoring

1. **Initialize Databases**:
   ```bash
   python init_databases.py
   ```

2. **Verify Database Creation**:
   ```bash
   ls databases/
   # Should see: users.db, questions.db, assignments.db
   ```

3. **Check Question Count**:
   ```bash
   sqlite3 databases/questions.db "SELECT COUNT(*) FROM Questions;"
   # Should show: 100+
   ```

4. **Check Assignment Count**:
   ```bash
   sqlite3 databases/assignments.db "SELECT COUNT(*) FROM Assignments;"
   # Should show: 30+
   ```

5. **Run the Application**:
   ```bash
   python app.py
   ```

6. **Test Functionality**:
   - Register a new user ✓
   - Login ✓
   - Start an interview ✓
   - View assignments ✓
   - Check progress ✓

## Troubleshooting

### Issue: Databases not found
**Solution**: Ensure you're in the project root directory and run `python init_databases.py`

### Issue: Empty question bank
**Solution**: Run `python init_databases.py` again - it uses INSERT OR IGNORE

### Issue: "No such table" errors
**Solution**: Delete `databases/` folder and reinitialize

### Issue: Still using old database.db
**Solution**: Check app.py for any remaining `get_db_connection()` calls (should be none)

## Future Enhancements

1. **PostgreSQL Migration**: Easy to migrate each SQLite database to PostgreSQL separately
2. **Redis Cache**: Add caching layer for frequently accessed questions
3. **Read Replicas**: Set up read replicas for questions.db (read-heavy)
4. **Microservices**: Each database can become its own microservice
5. **API Gateway**: Add REST API layer over each database

## Summary

The refactoring successfully splits a monolithic database into three modular databases:
- ✅ **users.db** - 6 tables for user management and interviews
- ✅ **questions.db** - Question bank with 100+ pre-loaded questions
- ✅ **assignments.db** - 30+ coding assignments
- ✅ Helper functions for intelligent question fetching
- ✅ All routes updated to use correct database
- ✅ Backward-compatible initialization process
- ✅ Production-ready architecture

The new architecture provides better scalability, maintainability, and separation of concerns while maintaining all original functionality.
