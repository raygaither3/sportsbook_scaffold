from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from dotenv import load_dotenv
from flask_wtf import CSRFProtect



# Create instances (but don't init_app yet)
load_dotenv()
db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()
bcrypt = Bcrypt()
csrf = CSRFProtect()

@login_manager.user_loader
def load_user(user_id):
    from .models import User
    return User.query.get(int(user_id))
