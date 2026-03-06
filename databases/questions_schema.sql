-- ========================================
-- Questions Database Schema (questions.db)
-- Stores interview questions organized by category
-- ========================================

-- Questions Table - Interview question bank
CREATE TABLE IF NOT EXISTS Questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    role TEXT NOT NULL,
    difficulty TEXT NOT NULL,
    category TEXT NOT NULL,
    question_text TEXT NOT NULL,
    expected_keywords TEXT,
    source TEXT DEFAULT 'database',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for efficient question retrieval
CREATE INDEX IF NOT EXISTS idx_questions_role ON Questions(role);
CREATE INDEX IF NOT EXISTS idx_questions_difficulty ON Questions(difficulty);
CREATE INDEX IF NOT EXISTS idx_questions_category ON Questions(category);
CREATE INDEX IF NOT EXISTS idx_questions_role_difficulty ON Questions(role, difficulty);
