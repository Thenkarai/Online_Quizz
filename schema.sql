-- Schema for Professional Online Quiz Competition System (PostgreSQL)

CREATE TABLE IF NOT EXISTS admins (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    password TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS quizzes (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    duration INTEGER NOT NULL,
    num_questions INTEGER NOT NULL,
    quiz_code VARCHAR(20) UNIQUE NOT NULL,
    time_per_question INTEGER DEFAULT 30,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    admin_id INTEGER,
    FOREIGN KEY (admin_id) REFERENCES admins (id)
);

CREATE TABLE IF NOT EXISTS questions (
    id SERIAL PRIMARY KEY,
    quiz_id INTEGER,
    question_text TEXT NOT NULL,
    question_type VARCHAR(50) NOT NULL,
    options TEXT,
    correct_answer TEXT NOT NULL,
    image_path TEXT,
    FOREIGN KEY (quiz_id) REFERENCES quizzes (id)
);

CREATE TABLE IF NOT EXISTS participants (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    register_number TEXT,
    quiz_id INTEGER,
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50) DEFAULT 'pending',
    FOREIGN KEY (quiz_id) REFERENCES quizzes (id)
);

CREATE TABLE IF NOT EXISTS answers (
    id SERIAL PRIMARY KEY,
    participant_id INTEGER,
    question_id INTEGER,
    submitted_answer TEXT,
    is_correct BOOLEAN,
    FOREIGN KEY (participant_id) REFERENCES participants (id),
    FOREIGN KEY (question_id) REFERENCES questions (id)
);

CREATE TABLE IF NOT EXISTS results (
    id SERIAL PRIMARY KEY,
    participant_id INTEGER,
    score INTEGER,
    total_questions INTEGER,
    time_taken INTEGER,
    cheating_warnings INTEGER DEFAULT 0,
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (participant_id) REFERENCES participants (id)
);

CREATE TABLE IF NOT EXISTS cheating_logs (
    id SERIAL PRIMARY KEY,
    participant_id INTEGER,
    event_type VARCHAR(100),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (participant_id) REFERENCES participants (id)
);
