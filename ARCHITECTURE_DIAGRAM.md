# Database Architecture Diagram

## System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          AI INTERVIEW PLATFORM                           │
│                              (Flask App)                                 │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    │               │               │
                    ▼               ▼               ▼
        ┌───────────────────┐  ┌──────────────┐  ┌──────────────────┐
        │   users.db (64KB) │  │ questions.db │  │ assignments.db   │
        │                   │  │   (44KB)     │  │    (32KB)        │
        └───────────────────┘  └──────────────┘  └──────────────────┘
                │                     │                    │
                │                     │                    │
                ▼                     ▼                    ▼
    ┌──────────────────────┐  ┌──────────────┐  ┌─────────────────┐
    │ Authentication &     │  │ Question     │  │ Coding          │
    │ Interview Data       │  │ Bank         │  │ Assignments     │
    │                      │  │              │  │                 │
    │ • Users              │  │ • Questions  │  │ • Assignments   │
    │ • Resumes            │  │              │  │                 │
    │ • Interviews         │  │ 115 Q's      │  │ 32 Problems     │
    │ • Results            │  │ 6 Categories │  │ 4 Roles         │
    │ • ChatHistory        │  │              │  │                 │
    │ • Progress           │  │              │  │                 │
    └──────────────────────┘  └──────────────┘  └─────────────────┘
```

---

## Connection Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                          Flask Routes                            │
└─────────────────────────────────────────────────────────────────┘
                               │
         ┌─────────────────────┼─────────────────────┐
         │                     │                     │
         ▼                     ▼                     ▼
┌─────────────────┐    ┌──────────────┐    ┌──────────────────┐
│ get_users_db()  │    │ get_         │    │ get_             │
│                 │    │ questions_   │    │ assignments_     │
│ Used by:        │    │ db()         │    │ db()             │
│ • /register     │    │              │    │                  │
│ • /login        │    │ Used by:     │    │ Used by:         │
│ • /dashboard    │    │ • fetch_     │    │ • /assignments   │
│ • /interview_   │    │   questions()│    │ • fetch_         │
│   setup         │    │              │    │   assignments()  │
│ • /interview_   │    │              │    │                  │
│   chat          │    │              │    │                  │
│ • /results      │    │              │    │                  │
│ • /progress     │    │              │    │                  │
│ • /upload_      │    │              │    │                  │
│   resume        │    │              │    │                  │
└─────────────────┘    └──────────────┘    └──────────────────┘
```

---

## Data Flow: Interview Session

```
1. User Login
   └─> get_users_db() → Users table → Session created

2. Start Interview
   └─> get_users_db() → Interviews table → interview_id
   └─> get_users_db() → ChatHistory table → Initial greeting

3. Fetch Questions (Dynamic)
   └─> fetch_questions(role, difficulty, n)
       ├─> get_questions_db() → Questions table
       │   └─> If < n questions: Generate with AI
       │       └─> Save to Questions table
       └─> Return questions

4. Chat Interaction
   └─> get_users_db() → ChatHistory table
       ├─> Save student message
       └─> Save AI response

5. End Interview
   └─> get_users_db()
       ├─> Calculate scores
       ├─> Results table → Save scores
       ├─> Interviews table → Update status
       └─> Progress table → Update statistics

6. View Progress
   └─> get_users_db()
       ├─> Progress table → Get stats
       └─> Results + Interviews → Get history
```

---

## Question Fetching Strategy

```
fetch_questions(role='Python Developer', difficulty='medium', n=5)
                           │
                           ▼
         ┌─────────────────────────────────┐
         │  Query questions.db             │
         │  SELECT * FROM Questions        │
         │  WHERE role = ? AND difficulty =?│
         │  LIMIT 5                        │
         └─────────────────────────────────┘
                           │
                  ┌────────┴────────┐
                  │                 │
            Found 5?           Found < 5?
                  │                 │
                  ▼                 ▼
         ┌────────────┐    ┌──────────────────┐
         │ Return     │    │ Generate with AI │
         │ questions  │    │ (Gemini API)     │
         └────────────┘    └──────────────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │ Save AI questions   │
                         │ to questions.db     │
                         └─────────────────────┘
                                    │
                                    ▼
                           ┌────────────────┐
                           │ Return all     │
                           │ (DB + AI)      │
                           └────────────────┘
```

---

## Assignment Fetching Strategy

```
fetch_assignments(role='Python Developer', difficulty=None, limit=10)
                           │
                           ▼
         ┌─────────────────────────────────┐
         │  Query assignments.db           │
         │  SELECT * FROM Assignments      │
         │  WHERE role = ?                 │
         │  LIMIT 10                       │
         └─────────────────────────────────┘
                           │
                           ▼
                  ┌────────────────┐
                  │ Return         │
                  │ assignments    │
                  └────────────────┘

Note: Assignments are NEVER generated by AI.
      They are pre-populated and read-only.
```

---

## Database Tables Reference

### users.db (6 tables)
```
Users
  ├─ id (PK)
  ├─ username (UNIQUE)
  ├─ email (UNIQUE)
  ├─ password (hashed)
  └─ created_at

Resumes
  ├─ id (PK)
  ├─ user_id (FK → Users)
  ├─ file_path
  └─ uploaded_at

Interviews
  ├─ id (PK)
  ├─ user_id (FK → Users)
  ├─ role
  ├─ difficulty
  ├─ interview_date
  └─ status

Results
  ├─ id (PK)
  ├─ user_id (FK → Users)
  ├─ interview_id (FK → Interviews)
  ├─ technical_score
  ├─ communication_score
  ├─ overall_score
  ├─ feedback
  └─ created_at

ChatHistory
  ├─ id (PK)
  ├─ user_id (FK → Users)
  ├─ interview_id (FK → Interviews)
  ├─ sender (AI/Student)
  ├─ message
  └─ timestamp

Progress
  ├─ id (PK)
  ├─ user_id (FK → Users)
  ├─ interview_count
  ├─ average_score
  ├─ last_score
  └─ updated_at
```

### questions.db (1 table)
```
Questions
  ├─ id (PK)
  ├─ role
  ├─ difficulty
  ├─ question_text
  ├─ expected_keywords
  ├─ category
  ├─ source (database/ai_generated)
  └─ created_at
  
Indexes:
  - idx_questions_role
  - idx_questions_difficulty
  - idx_questions_category
  - idx_questions_role_difficulty
```

### assignments.db (1 table)
```
Assignments
  ├─ id (PK)
  ├─ role
  ├─ difficulty
  ├─ assignment_text
  ├─ solution_hint
  └─ created_at
  
Indexes:
  - idx_assignments_role
  - idx_assignments_difficulty
  - idx_assignments_role_difficulty
```

---

## Security Considerations

```
┌────────────────────────────────────────┐
│  Database Isolation Benefits           │
├────────────────────────────────────────┤
│                                        │
│  ✓ User credentials in separate DB    │
│    (users.db can have different       │
│     permissions)                       │
│                                        │
│  ✓ Questions DB can be read-only      │
│    (prevent accidental modification)   │
│                                        │
│  ✓ Assignments DB is read-only        │
│    (pre-populated, no user writes)     │
│                                        │
│  ✓ Easier to backup sensitive data    │
│    (backup users.db more frequently)   │
│                                        │
│  ✓ Can encrypt databases separately   │
│    (different encryption keys)         │
│                                        │
└────────────────────────────────────────┘
```

---

## Scalability Path

```
Current: SQLite (3 databases)
         ├─ users.db
         ├─ questions.db
         └─ assignments.db

  ↓ Scale Stage 1: Add Read Replicas

PostgreSQL (3 databases)
         ├─ users_db (read/write)
         ├─ questions_db (read replica)
         └─ assignments_db (read replica)

  ↓ Scale Stage 2: Microservices

Service Architecture
         ├─ Auth Service (users_db)
         ├─ Interview Service (users_db)
         ├─ Questions Service (questions_db)
         └─ Assignments Service (assignments_db)

  ↓ Scale Stage 3: Distributed

Distributed Services
         ├─ Auth Service (PostgreSQL + Redis)
         ├─ Interview Service (PostgreSQL)
         ├─ Questions Service (PostgreSQL + CDN cache)
         └─ Assignments Service (PostgreSQL + CDN cache)
```

---

## Performance Optimizations

### Database-Level
```
users.db
  ✓ Index on user_id (all foreign keys)
  ✓ Index on interview_id
  ✓ Composite index on user_id + interview_date

questions.db
  ✓ Index on role
  ✓ Index on difficulty
  ✓ Index on category
  ✓ Composite index on (role, difficulty) for fast filtering

assignments.db
  ✓ Index on role
  ✓ Index on difficulty
  ✓ Composite index on (role, difficulty)
```

### Application-Level
```
✓ Connection pooling (can add later)
✓ Query result caching (fetch_questions() caches in memory)
✓ Lazy loading (connections created on demand)
✓ AI-generated questions saved to DB (reduce API calls)
```

---

## Backup Strategy

```
Daily Backups:
  ├─ users.db (full backup)
  │   └─ Contains user data, interviews, results
  │   └─ CRITICAL - backup before any operations
  │
  ├─ questions.db (incremental)
  │   └─ Track new AI-generated questions
  │   └─ Can be reconstructed from init_databases.py
  │
  └─ assignments.db (version control)
      └─ Rarely changes
      └─ Commit to git after updates

Recovery:
  1. Restore users.db from latest backup
  2. Reinitialize questions.db (python init_databases.py)
  3. Reinitialize assignments.db (python init_databases.py)
```

---

## Summary: Architecture Benefits

| Aspect | Before | After | Benefit |
|--------|--------|-------|---------|
| **Databases** | 1 monolithic | 3 modular | Better separation |
| **Tables/DB** | 9 tables | 6 + 1 + 1 | Focused purpose |
| **Scalability** | Limited | Independent | Scale per need |
| **Backup** | All-or-nothing | Selective | Flexible |
| **Security** | Mixed | Isolated | Better control |
| **Performance** | Single lock | Multiple | Reduced contention |
| **Maintenance** | Complex | Modular | Easier updates |
| **Testing** | Monolithic | Modular | Isolated tests |

**Result**: Production-ready architecture that's easier to maintain, scale, and secure! 🚀
