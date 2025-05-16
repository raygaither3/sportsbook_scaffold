from flask import render_template, request
from flask import Blueprint
from flask_login import current_user, login_required
from sqlalchemy import or_
from ..models import Game, Bet, Team
from ..utils.odds_api import get_odds
from ..utils.constants import SPORT_LABELS


main = Blueprint('main', __name__)


@main.route('/')
def home():
    selected_sport = request.args.get('sport')
    sports = ['mma_mixed_martial_arts', 'basketball_nba', 'americanfootball_nfl', 'baseball_mlb']
    sport_names = {
        'mma_mixed_martial_arts': 'MMA',
        'basketball_nba': 'NBA',
        'americanfootball_nfl': 'NFL',
        'baseball_mlb': 'MLB'
    }

    upcoming_events = []

    try:
        for sport in sports:
            if selected_sport and sport != selected_sport:
                continue
            events = get_odds(sport)
            for event in events:
                upcoming_events.append({
                    'home_team': event.get('home_team'),
                    'away_team': event.get('away_team'),
                    'start_time': event.get('commence_time'),
                    'sport': sport,
                    'event': event
                })
        upcoming_events.sort(key=lambda x: x['start_time'])
    except Exception:
        upcoming_events = []

    return render_template('home.html',
                           upcoming_events=upcoming_events,
                           selected_sport=selected_sport,
                           sport_names=sport_names)




@main.route('/live-odds')
def live_odds():
    events = get_odds("upcoming")  # or "basketball_nba", "mma_mixed_martial_arts"
    return render_template("main/live_odds.html", events=events)


@main.route('/events')
def events():
    return render_template('main/events.html', sport_labels=SPORT_LABELS)


@main.route('/search')
@login_required
def search():
    q = request.args.get('q', '').strip().lower()
    games = []
    bets = []
    api_matches = []

    if q:
        # Local database search
        games = (
            Game.query
                .filter(
                    or_(
                        Game.home_team.has(Team.name.ilike(f'%{q}%')),
                        Game.away_team.has(Team.name.ilike(f'%{q}%')),
                    )
                )
                .order_by(Game.start_time.desc())
                .all()
        )

        bets = (
            Bet.query
                .filter(Bet.user_id == current_user.id)
                .filter(
                    or_(
                        Bet.home_team.ilike(f'%{q}%'),
                        Bet.away_team.ilike(f'%{q}%'),
                        Bet.selection.ilike(f'%{q}%'),
                    )
                )
                .order_by(Bet.created_at.desc())
                .all()
        )

        # API search across supported sports
        sports = ['mma_mixed_martial_arts', 'basketball_nba', 'americanfootball_nfl', 'baseball_mlb']
        for sport in sports:
            try:
                odds_data = get_odds(sport)
                for event in odds_data:
                    home = event.get('home_team', '').lower()
                    away = event.get('away_team', '').lower()
                    if q in home or q in away:
                        api_matches.append({
                            'home_team': event.get('home_team'),
                            'away_team': event.get('away_team'),
                            'start_time': event.get('commence_time'),
                            'sport': sport,
                        })
            except Exception as e:
                # Log or handle API failure gracefully
                continue

    return render_template(
        'main/search_results.html',
        query=q,
        events=games,
        bets=bets,
        api_matches=api_matches,
    )