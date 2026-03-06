-- ========================================
-- Users Database Schema (users.db)
-- Stores authentication and interview data
-- ========================================

-- Users Table - Authentication and user profiles
CREATE TABLE IF NOT EXISTS Users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Resumes Table - Uploaded resume files
CREATE TABLE IF NOT EXISTS Resumes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    file_path TEXT NOT NULL,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES Users(id) ON DELETE CASCADE
);

-- Interviews Table - Interview session tracking
CREATE TABLE IF NOT EXISTS Interviews (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    role TEXT NOT NULL,
    difficulty TEXT NOT NULL,
    interview_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status TEXT DEFAULT 'in_progress',
    FOREIGN KEY (user_id) REFERENCES Users(id) ON DELETE CASCADE
);

-- Results Table - Interview performance results
CREATE TABLE IF NOT EXISTS Results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    interview_id INTEGER NOT NULL,
    technical_score REAL DEFAULT 0,
    communication_score REAL DEFAULT 0,
    overall_score REAL DEFAULT 0,
    feedback TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES Users(id) ON DELETE CASCADE,
    FOREIGN KEY (interview_id) REFERENCES Interviews(id) ON DELETE CASCADE
);

-- ChatHistory Table - Interview conversation logs
CREATE TABLE IF NOT EXISTS ChatHistory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    interview_id INTEGER NOT NULL,
    sender TEXT NOT NULL,
    message TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES Users(id) ON DELETE CASCADE,
    FOREIGN KEY (interview_id) REFERENCES Interviews(id) ON DELETE CASCADE
);

-- Progress Table - User progress analytics
CREATE TABLE IF NOT EXISTS Progress (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    interview_count INTEGER DEFAULT 0,
    average_score REAL DEFAULT 0,
    last_score REAL DEFAULT 0,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES Users(id) ON DELETE CASCADE
);

-- ResumeAnalysis Table - AI-powered resume analysis results
CREATE TABLE IF NOT EXISTS ResumeAnalysis (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    resume_path TEXT NOT NULL,
    ats_score INTEGER,
    skills TEXT,
    recommended_roles TEXT,
    missing_skills TEXT,
    suggestions TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES Users(id) ON DELETE CASCADE
);

-- Indexes for performance optimization
CREATE INDEX IF NOT EXISTS idx_resumes_user_id ON Resumes(user_id);
CREATE INDEX IF NOT EXISTS idx_interviews_user_id ON Interviews(user_id);
CREATE INDEX IF NOT EXISTS idx_results_user_id ON Results(user_id);
CREATE INDEX IF NOT EXISTS idx_results_interview_id ON Results(interview_id);
CREATE INDEX IF NOT EXISTS idx_chat_interview_id ON ChatHistory(interview_id);
CREATE INDEX IF NOT EXISTS idx_progress_user_id ON Progress(user_id);
