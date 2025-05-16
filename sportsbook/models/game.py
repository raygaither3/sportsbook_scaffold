from ..extensions import db


class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    home_team_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=False)
    away_team_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=False)
    league_id = db.Column(db.Integer, db.ForeignKey('league.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default='pending')
    final_score_home = db.Column(db.Integer)
    final_score_away = db.Column(db.Integer)
    markets = db.relationship('Market', backref='game', lazy=True)
    method_of_victory = db.Column(db.String(50))  # e.g., KO, Submission, Decision
    round_ended = db.Column(db.Integer)  # e.g., 1, 2, 3

    home_team = db.relationship('Team', foreign_keys=[home_team_id])
    away_team = db.relationship('Team', foreign_keys=[away_team_id])


class Market(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'), nullable=False)
    market_type = db.Column(db.String(50), nullable=False)  # Moneyline, Spread, OverUnder
    odds_home = db.Column(db.Float)
    odds_away = db.Column(db.Float)
    spread_points = db.Column(db.Float)
    over_under_total = db.Column(db.Float)
    selections = db.relationship('BetSelection', backref='market', lazy=True)