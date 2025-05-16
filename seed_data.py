from sportsbook import create_app, db
from sportsbook.models import Team, League, Sport, Game, Market
from datetime import datetime, timedelta

app = create_app()

with app.app_context():
    db.drop_all()
    db.create_all()

    # Add a sport
    sport = Sport(name="MMA")
    db.session.add(sport)
    db.session.commit()

    # Add a league
    league = League(name="UFC", sport_id=sport.id)
    db.session.add(league)
    db.session.commit()

    # Add teams (fighters)
    team1 = Team(name="Jon Jones", league_id=league.id)
    team2 = Team(name="Stipe Miocic", league_id=league.id)
    db.session.add_all([team1, team2])
    db.session.commit()

    # Add a game
    game = Game(
        home_team_id=team1.id,
        away_team_id=team2.id,
        league_id=league.id,
        start_time=datetime.utcnow() + timedelta(days=1),
        status="pending"
    )
    db.session.add(game)
    db.session.commit()

    # Add a market
    market = Market(
        game_id=game.id,
        market_type="Moneyline",
        odds_home=1.8,
        odds_away=2.1
    )
    db.session.add(market)
    db.session.commit()

    print("✅ Seed data inserted!")