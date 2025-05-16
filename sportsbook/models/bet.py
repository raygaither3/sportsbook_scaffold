from .mixins import TimestampMixin
from ..extensions import db


class Bet(db.Model, TimestampMixin):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'), nullable=True)  # ← must allow NULL
    amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='pending')
    payout = db.Column(db.Float)
    home_team = db.Column(db.String(100))  
    away_team = db.Column(db.String(100))  
    selection = db.Column(db.String(20))   
    odds = db.Column(db.Float) 

    selections = db.relationship('BetSelection', backref='bet', lazy=True)            


class BetSelection(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bet_id = db.Column(db.Integer, db.ForeignKey('bet.id'), nullable=False)
    market_id = db.Column(db.Integer, db.ForeignKey('market.id'), nullable=False)
    selection = db.Column(db.String(20), nullable=False)  # home, away, over, under
    odds_at_bet_time = db.Column(db.Float, nullable=False)