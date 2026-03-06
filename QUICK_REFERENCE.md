# 🚀 QUICK REFERENCE - Database Refactoring

## One-Page Reference for the New Architecture

---

## 📁 Three Databases

```
databases/
├── users.db        (Authentication, Interviews, Results)
├── questions.db    (Question Bank - 115 questions)
└── assignments.db  (Coding Assignments - 32 problems)
```

---

## 🔌 Connection Functions

```python
# Use these instead of the old get_db_connection()
conn = get_users_db()        # For user operations
conn = get_questions_db()    # For question operations
conn = get_assignments_db()  # For assignment operations
```

---

## 🛠️ Helper Functions

### Fetch Questions (Smart Fetch with AI Fallback)
```python
questions = fetch_questions(
    role='Python Developer',   # Job role
    difficulty='medium',        # easy, medium, hard
    n=5                        # Number needed
)
# Returns: List of question texts
# Behavior: DB first, generates with AI if insufficient, saves AI questions
```

### Fetch Assignments (DB Only, No AI)
```python
assignments = fetch_assignments(
    role='Python Developer',   # Optional filter
    difficulty='easy',         # Optional filter
    limit=10                   # Max results
)
# Returns: List of assignment dictionaries
# Behavior: Always from DB, never generates
```

---

## 🗂️ Database Tables

### users.db (6 tables)
- **Users** - Authentication
- **Resumes** - File uploads
- **Interviews** - Session data
- **Results** - Scores and feedback
- **ChatHistory** - Conversation logs
- **Progress** - User statistics

### questions.db (1 table)
- **Questions** - 115 questions, indexed on role/difficulty/category

### assignments.db (1 table)
- **Assignments** - 32 assignments, indexed on role/difficulty

---

## 🔄 Route → Database Mapping

| Route | Database Used | Function |
|-------|---------------|----------|
| `/register` | users.db | `get_users_db()` |
| `/login` | users.db | `get_users_db()` |
| `/dashboard` | users.db | `get_users_db()` |
| `/interview_setup` | users.db | `get_users_db()` |
| `/interview_chat` | users.db | `get_users_db()` |
| `/results` | users.db | `get_users_db()` |
| `/progress` | users.db | `get_users_db()` |
| `/assignments` | assignments.db | `get_assignments_db()` |
| Question fetch | questions.db | `fetch_questions()` |

---

## ⚡ Quick Commands

### Initialize All Databases
```bash
python init_databases.py
```

### Verify Databases
```bash
python verify_databases.py
```

### Run Application
```bash
python app.py
```

### Check Database Files
```bash
# Windows PowerShell
Get-ChildItem databases\*.db

# Linux/Mac
ls -lh databases/*.db
```

---

## 📊 Data Distribution

### Questions (115 total)
- Python: 55 (Easy: 25, Medium: 20, Hard: 10)
- SQL: 20 (Easy: 10, Medium: 10)
- Coding: 20 (Easy: 10, Medium: 10)
- Backend: 10 (Medium)
- System Design: 10 (Hard)
- HR: 5 (Easy)

### Assignments (32 total)
- Python Developer: 15
- Full Stack Developer: 4
- Backend Developer: 5
- Data Scientist: 8

---

## 🐛 Common Issues

### Issue: "No such table"
**Fix**: Run `python init_databases.py`

### Issue: Empty question bank
**Fix**: Delete `databases/` and run `python init_databases.py` again

### Issue: Old get_db_connection() error
**Fix**: All replaced - shouldn't see this. Check app.py if it occurs.

---

## 📖 Documentation Files

| File | Purpose | Lines |
|------|---------|-------|
| **README.md** | Main project documentation | Updated |
| **DATABASE_MIGRATION_GUIDE.md** | Complete migration guide | 350 |
| **REFACTORING_SUMMARY.md** | Technical overview | 280 |
| **ARCHITECTURE_DIAGRAM.md** | Visual reference | 450 |
| **PROJECT_COMPLETION.md** | Completion checklist | 200 |
| **QUICK_REFERENCE.md** | This file | 1 page |

---

## ✅ Success Indicators

After running `python init_databases.py`, you should see:
- ✓ databases/users.db (64 KB, 6 tables)
- ✓ databases/questions.db (44 KB, 115 questions)
- ✓ databases/assignments.db (32 KB, 32 assignments)

After running `python verify_databases.py`, you should see:
- ✓ All table counts displayed
- ✓ Question distribution shown
- ✓ Assignment distribution shown

---

## 🚀 Ready to Use!

```bash
# 1. Initialize
python init_databases.py

# 2. Verify
python verify_databases.py

# 3. Run
python app.py

# 4. Visit
http://127.0.0.1:5000
```

---

**That's it! The refactored architecture is production-ready.** 🎉
