from ..extensions import db
from .user import User
from .bet import Bet, BetSelection
from .wallet import Wallet, Transaction
from .game import Game, Market
from .sport import Sport, League, Team
from .mixins import TimestampMixin

def create_database(app):
    with app.app_context():
        db.create_all()
        print("Database created!")
