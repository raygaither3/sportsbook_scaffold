from sportsbook import create_app, db
from sportsbook.models import User

app = create_app()
with app.app_context():
    user = User.query.filter_by(email="raygaither3@gmail.com").first()
    user.is_admin = True
    db.session.commit()
    print("✅ Admin privileges granted.")