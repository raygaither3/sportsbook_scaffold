📘 Sportsbook (Work In Progress)
A custom-built Flask web application for placing sports bets, including standard and live betting features. Designed with a dark theme and red-accented interface for a sleek user experience.

⚙️ Tech Stack
Python / Flask

Flask-Login for authentication

Flask-SQLAlchemy for database models

WTForms for form handling

Jinja2 for templating

SQLite (dev database)

HTML / CSS (custom styling)

🎯 Features
User authentication (registration, login, logout)

Standard bets with dynamic odds

Live betting interface using API-driven odds

Bet confirmation and tracking

Modular codebase (auth, bets, events, admin, etc.)

Admin dropdown and messaging

Responsive layout with sidebar and top navbar

🚧 Status
This project is currently in development and is not considered feature complete. The core structure is in place, but several enhancements and refinements are planned. It is being actively developed as both a portfolio piece and a potential full-featured product.

📂 Setup (Optional)
If you want to run this locally:

bash
Copy
Edit
git clone https://github.com/raygaither3/sportsbook_scaffold.git
cd sportsbook_scaffold
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
flask run
