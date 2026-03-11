-- Schema for Professional Online Quiz Competition System

CREATE TABLE IF NOT EXISTS admins (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS quizzes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    duration INTEGER NOT NULL, -- in minutes
    num_questions INTEGER NOT NULL,
    quiz_code TEXT UNIQUE NOT NULL,
    time_per_question INTEGER DEFAULT 30, -- in seconds
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    admin_id INTEGER,
    FOREIGN KEY (admin_id) REFERENCES admins (id)
);

CREATE TABLE IF NOT EXISTS questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    quiz_id INTEGER,
    question_text TEXT NOT NULL,
    question_type TEXT NOT NULL, -- 'mcq', 'fib', 'image'
    options TEXT, -- JSON string for options in MCQ/Image
    correct_answer TEXT NOT NULL,
    image_path TEXT,
    FOREIGN KEY (quiz_id) REFERENCES quizzes (id)
);

CREATE TABLE IF NOT EXISTS participants (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    register_number TEXT,
    quiz_id INTEGER,
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status TEXT DEFAULT 'pending', -- 'pending', 'approved', 'started', 'submitted'
    FOREIGN KEY (quiz_id) REFERENCES quizzes (id)
);

CREATE TABLE IF NOT EXISTS answers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    participant_id INTEGER,
    question_id INTEGER,
    submitted_answer TEXT,
    is_correct BOOLEAN,
    FOREIGN KEY (participant_id) REFERENCES participants (id),
    FOREIGN KEY (question_id) REFERENCES questions (id)
);

CREATE TABLE IF NOT EXISTS results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    participant_id INTEGER,
    score INTEGER,
    total_questions INTEGER,
    time_taken INTEGER, -- in seconds
    cheating_warnings INTEGER DEFAULT 0,
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (participant_id) REFERENCES participants (id)
);

CREATE TABLE IF NOT EXISTS cheating_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    participant_id INTEGER,
    event_type TEXT, -- 'tab_switch', 'fullscreen_exit', 'ai_flag'
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (participant_id) REFERENCES participants (id)
);
