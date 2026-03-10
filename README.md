# QuizPro - Premium Online Examination Platform

QuizPro is a modern, highly secure, and elegant online quiz and examination platform. Inspired by the premium aesthetics of Apple WWDC and Stripe dashboards, it features a beautiful glassmorphism UI, smooth micro-interactions, and robust administrative capabilities built with Python Flask.

## ✨ Features

### Premium SaaS Interface
- **Modern Aesthetic**: Clean, unique design featuring frosted glass UI cards, custom hover ripples, and floating gradients.
- **Dual Themes**: Seamlessly toggle between "Daylight Glass" (Light Mode) and "Midnight Glass" (Dark Mode).
- **Smooth Animations**: Animated SVG circular timers, ambient background shapes, and floating UI elements.

### Advanced Security & Anti-Cheat
- **Tab-Switching Detection**: Monitors browser focus. Three warnings lead to an automatic session suspension.
- **Fullscreen Enforcement**: Requires full screen to take assessments; exits are flagged.
- **Suspicious Activity Log**: Admins can view real-time logs of security violations for each participant.
- **Risk Scoring**: The system calculates a weighted Risk Score automatically displayed on the live leaderboard.
- **Copy/Paste Prevention**: Disabled text selection, right-click, and copy-pasting during examinations.

### Administrator Capabilities
- **Rich Dashboard**: Track active quizzes, live leaderboards, and pending approvals.
- **Custom Quiz Creation**: Add multiple-choice, fill-in-the-blank, and image-based questions.
- **Live Polling**: Real-time updates without page reloads during active quizzes.
- **Unique Join Codes & QR**: Automatically generates alphanumeric codes and QR codes for effortless student onboarding.
- **Export Results**: Download full assessment results and security logs to Excel/CSV.

## 🛠️ Tech Stack
- **Backend**: Python, Flask
- **Database**: SQLite
- **Frontend**: HTML5, Vanilla CSS3 (Custom Variables/Glassmorphism), Vanilla JavaScript
- **Visuals**: Chart.js for analytics, Canvas Confetti for results

## 🚀 Getting Started

### Prerequisites
- Python 3.8+ 
- `pip` (Python package installer)

### Installation
1. Clone the repository:
   ```bash
   git clone <your-github-repo-url>
   cd "quizz management"
   ```

2. Install the required dependencies:
   ```bash
   pip install flask werkzeug qrcode pillow pandas openpyxl
   ```

3. Run the application:
   ```bash
   python app.py
   ```
   *(Note: Use `python3 app.py` or `py app.py` depending on your Windows/Mac setup)*

4. Open your browser and navigate to:
   `http://127.0.0.1:5000`

### Admin Login
- **Username**: `admin`
- **Password**: `admin123`
*(Change these default credentials in the `app.py` or database in a production environment)*

## 📂 Project Structure
- `/app.py`: Main Flask application handling routing, API endpoints, and database interactions.
- `/schema.sql`: Database schema definition.
- `/templates/`: Jinja2 HTML templates for all pages.
- `/static/css/`: Modular CSS (layout, animations, core styles).
- `/static/js/`: Modular JavaScript (dashboard live-polling, anti-cheat logic, theme toggling).
- `/static/uploads/` & `/static/qrcodes/`: Generated static assets.

## 📄 License
This project is open-source and available under the [MIT License](LICENSE).
