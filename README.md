# AI Study Plan Generator & Tracker

## Project Overview
The **AI Study Plan Generator & Tracker** is a web-based application that helps users create a personalized study plan based on their learning goal, available time, and study preferences.  
The system not only generates a structured plan but also allows users to **track daily progress**, visualize completion status, and adjust study behavior over time.

The project focuses on **planning, execution, and tracking**, rather than skill assessment or testing.

---

## Key Objectives
- Generate realistic, goal-oriented study plans
- Support different learning intents:
  - Exam preparation
  - Skill / topic completion
  - Certification preparation
- Track daily task completion
- Provide progress insights and weekly milestone tracking
- Ensure reliability using AI with a rule-based fallback mechanism

---

## Features

### Core Features
- **Goal Definition**
  - Subject or learning goal
  - Goal type (Exam / Skill / Certification)
- **Time & Preference Input**
  - Study duration (days)
  - Hours per week
  - Preferred study days
  - Study intensity (light / moderate / intensive)
- **AI-Based Study Plan Generation**
  - Week-wise milestones
  - Topic-specific subtopics
  - Daily tasks with estimated effort
- **Progress Tracking**
  - Mark tasks as completed
  - Automatic progress percentage calculation
- **Dashboard**
  - Completion percentage
  - Days remaining
  - Weekly milestone progress
  - Status indicator (On track / Behind / Ahead)
- **Full Plan View**
  - Complete plan visible week-wise or date-wise
  - Task titles, descriptions, and estimated time

---

## AI Integration Strategy

### Primary Planner
- Uses **Hugging Face Inference Providers (Router API)** with an instruction-tuned chat model
- Generates **topic-specific weekly milestones and subtopics**
- Suitable for both exam-oriented and skill-oriented goals

### Fallback Planner
- If AI is unavailable (API error, quota, model issue), the system automatically switches to a **rule-based planner**
- The fallback planner:
  - Adapts to goal type
  - Avoids exam-specific patterns (e.g., PYQs) for skill-based learning
  - Guarantees uninterrupted plan generation

This hybrid approach ensures **reliability, explainability, and robustness**.

---

## Plan Generation Logic
1. User provides:
   - Goal / subject
   - Goal type
   - Duration
   - Weekly availability
   - Study intensity and preferences
2. AI (or fallback) generates:
   - Weekly milestones
   - Topic-specific subtopics
3. System converts weekly structure into:
   - Daily tasks
   - Learn → Practice → Revise / Improve pattern
4. A dynamic revision window is applied:
   - ~10% of total duration
   - Minimum 2 days, maximum 14 days

---

## Progress Tracking Mechanism
- Each task has a status: `pending` or `done`
- Progress percentage: (Completed Tasks / Total Tasks) × 100
- Weekly progress is calculated independently
- Visual indicators:
- Progress bar
- Weekly completion bars
- Completion badges for fully completed weeks

---

## Tech Stack
- **Frontend:** Streamlit
- **Backend:** Python
- **AI / NLP:** Hugging Face Inference Providers (Chat Models)
- **Database:** SQLite
- **Deployment:** Streamlit Community Cloud

---

## Project Structure
study-plan-generator
├── app.py                  # Main Streamlit app
├── db.py                   # Database connection
├── models.py               # Database models & queries
├── planner_hf.py           # Hugging Face planner
├── planner_fallback.py     # Rule-based fallback planner
├── progress.py             # Progress calculations
├── requirements.txt        # Project dependencies
├── README.md               # Project documentation
└── .gitignore              # Git ignore rules


---

## How to Run Locally
1. Clone the repository
2. Create and activate a Python environment
3. Install dependencies: pip install -r requirements.txt
4. (Optional) Add Hugging Face token in `.env`
5. Run the app:

---

## Deployment
The application is deployed on **Streamlit Community Cloud**.

> Hugging Face tokens are securely stored using Streamlit Secrets.

---

## Sample User Journey
1. User enters goal: *“Python for Data Science”*
2. Selects goal type: *Skill / Topic Completion*
3. Chooses duration and weekly availability
4. System generates a structured plan
5. User completes daily tasks
6. Dashboard updates progress and milestones
7. Full plan can be reviewed anytime in the **Full Plan** tab

---

## Notes
- The application supports **one active plan at a time** for simplicity and clarity
- SQLite storage is sufficient for demos and academic evaluation
- The architecture is extensible for multi-user or persistent storage if required

---

## Conclusion
This project demonstrates how AI-assisted planning combined with traditional rule-based logic can create a **reliable, user-friendly, and practical learning assistant**, suitable for both academic and real-world learning scenarios.



