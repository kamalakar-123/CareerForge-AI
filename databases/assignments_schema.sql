-- ========================================
-- Assignments Database Schema (assignments.db)
-- Stores AI-generated coding assignments and submissions
-- ========================================

-- Drop existing tables if they exist (for clean rebuild)
DROP TABLE IF EXISTS AssignmentHelp;
DROP TABLE IF EXISTS Submissions;
DROP TABLE IF EXISTS Assignments;
DROP TABLE IF EXISTS AssignmentGroups;

-- AssignmentGroups Table - Groups of 15 assignments generated together
CREATE TABLE AssignmentGroups (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    name TEXT NOT NULL,  -- e.g., "Python Lists - Easy"
    role TEXT NOT NULL,
    difficulty TEXT NOT NULL,
    topic TEXT NOT NULL,
    assignment_type TEXT NOT NULL,  -- 'mixed', 'coding', 'mcq'
    total_questions INTEGER DEFAULT 15,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Assignments Table - Individual AI-generated assignments (coding and MCQ)
CREATE TABLE Assignments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    group_id INTEGER NOT NULL,
    role TEXT NOT NULL,
    difficulty TEXT NOT NULL,
    topic TEXT NOT NULL,
    type TEXT NOT NULL CHECK(type IN ('coding', 'mcq')),
    question_data TEXT NOT NULL,  -- JSON: {title, problem, input, output, hint} or {question, options, answer, explanation}
    question_number INTEGER NOT NULL,  -- 1 to 15
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (group_id) REFERENCES AssignmentGroups (id) ON DELETE CASCADE
);

-- Submissions Table - User code submissions and results
CREATE TABLE Submissions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    assignment_id INTEGER NOT NULL,
    user_code TEXT,  -- User's submitted code (for coding assignments)
    user_answer TEXT,  -- User's selected answer (for MCQ assignments)
    result TEXT NOT NULL,  -- 'Correct', 'Incorrect', 'Error'
    output TEXT,  -- Actual program output or error message
    score INTEGER DEFAULT 0,
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (assignment_id) REFERENCES Assignments (id) ON DELETE CASCADE
);

-- Assignment Help History - Chat history for assignment help
CREATE TABLE AssignmentHelp (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    assignment_id INTEGER NOT NULL,
    sender TEXT NOT NULL,  -- 'Student' or 'AI'
    message TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (assignment_id) REFERENCES Assignments (id) ON DELETE CASCADE
);

-- Indexes for efficient querying
CREATE INDEX IF NOT EXISTS idx_assignment_groups_user ON AssignmentGroups(user_id);
CREATE INDEX IF NOT EXISTS idx_assignment_groups_filters ON AssignmentGroups(role, difficulty, topic);
CREATE INDEX IF NOT EXISTS idx_assignments_group ON Assignments(group_id);
CREATE INDEX IF NOT EXISTS idx_assignments_role ON Assignments(role);
CREATE INDEX IF NOT EXISTS idx_assignments_difficulty ON Assignments(difficulty);
CREATE INDEX IF NOT EXISTS idx_assignments_topic ON Assignments(topic);
CREATE INDEX IF NOT EXISTS idx_assignments_type ON Assignments(type);
CREATE INDEX IF NOT EXISTS idx_submissions_user ON Submissions(user_id);
CREATE INDEX IF NOT EXISTS idx_submissions_assignment ON Submissions(assignment_id);
CREATE INDEX IF NOT EXISTS idx_help_assignment ON AssignmentHelp(assignment_id);
