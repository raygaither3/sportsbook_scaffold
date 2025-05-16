from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from sportsbook.models.sport import League, Sport, Team
from ..extensions import db
from ..models import Game, Market, Bet, BetSelection, Transaction
from ..utils.odds_api import get_odds
from ..utils.constants import SPORT_LABELS



bets = Blueprint('bets', __name__)



@bets.route('/games')
@login_required
def games():
    all_games = Game.query.order_by(Game.start_time).all()
    return render_template('bets/games.html', games=all_games)

@bets.route('/place_bet', methods=['POST'])
@login_required
def place_bet():
    game_id = request.form.get('game_id')
    selection = request.form.get('selection')
    amount = float(request.form.get('amount'))
    odds = float(request.form.get('odds'))

    # These may be blank if it's a DB game, so we fallback later
    home_team = request.form.get('home_team')
    away_team = request.form.get('away_team')

    game = Game.query.get(game_id) if game_id else None
    team_name = ""

    if game:
        if not home_team:
            home_team = game.home_team.name
        if not away_team:
            away_team = game.away_team.name

        if selection == 'home':
            team_name = home_team
        elif selection == 'away':
            team_name = away_team

    else:
        # fallback if no game object
        team_name = home_team if selection == 'home' else away_team

    payout = round(amount * odds, 2)

    # Wallet deduction
    if current_user.wallet.balance < amount:
        flash("Insufficient funds.", "danger")
        return redirect(url_for('bets.games'))

    current_user.wallet.balance -= amount

    # Save Bet
    bet = Bet(
        user_id=current_user.id,
        amount=amount,
        payout=payout,
        odds=odds,
        selection=selection,
        home_team=home_team,
        away_team=away_team,
        game_id=game.id if game else None
    )
    db.session.add(bet)
    db.session.flush()  # Get bet.id before next

    # Add selection if it's a DB-based game
    if game:
        market = game.markets[0]
        bet_selection = BetSelection(
            bet_id=bet.id,
            market_id=market.id,
            selection=selection,
            odds_at_bet_time=odds
        )
        db.session.add(bet_selection)

    # Log transaction
    tx = Transaction(
        wallet_id=current_user.wallet.id,
        amount=-amount,
        type='bet'
    )
    db.session.add(tx)

    db.session.commit()

    flash(f"Bet placed on {team_name} at {odds}", "success")
    return redirect(url_for('user.dashboard'))


@bets.route('/confirm', methods=['POST'])
@login_required
def confirm_bet():
    game = None
    team_name = None  # ← SAFETY DEFAULT

    game_id = request.form.get('game_id')
    home_team = request.form.get('home_team')
    away_team = request.form.get('away_team')
    selection_raw = request.form.get('selection')
    amount = request.form.get('amount')
    sport = request.form.get('sport')
    market_type = request.form.get('market_type', '')

    # Validate and convert amount
    try:
        amount = float(amount)
    except Exception:
        flash("Invalid amount format.", "danger")
        return redirect(url_for('main.home'))

    selection_raw = request.form.get('selection')

    try:
        selection_name, odds_str, market_type = selection_raw.split('|')
        odds = float(odds_str)
    except Exception:
        flash("Bet selection could not be processed.", "danger")
        return redirect(url_for('bets.live_betting'))

    payout = round(amount * odds, 2)

    if game_id:
        game = Game.query.get(game_id)
        if game:
            market = game.markets[0]
            odds = market.odds_home if selection_name == game.home_team.name else market.odds_away
            home_team = game.home_team.name
            away_team = game.away_team.name
            team_name = selection_name
            payout = round(amount * odds, 2)

    return render_template(
        "bets/confirm_bet.html",
        game=game,
        selection=selection_name,
        amount=amount,
        odds=odds,
        team_name=team_name,
        payout=payout,
        home_team=home_team,
        away_team=away_team,
        sport=sport,
        market_type=market_type
    )

@bets.route('/live')
@login_required
def live_betting():
    events = get_odds("mma_mixed_martial_arts")  # You can test with basketball_nba or similar
    return render_template('bets/live_betting.html', events=events)


@bets.route('/submit-live-bet', methods=['POST'])
@login_required
def submit_live_bet():
    

    sport_name = request.form.get('sport', 'MMA')
    home_team_name = request.form.get('home_team')
    away_team_name = request.form.get('away_team')
    selection_raw = request.form.get('selection')
    amount = float(request.form.get('amount'))

    if not all([home_team_name, away_team_name, selection_raw, amount]):
        flash("Invalid bet submission.", "danger")
        return redirect(url_for('bets.live_betting'))

    try:
        selection_name, odds_str, market_type = selection_raw.split('|')
        odds = float(odds_str)
    except Exception:
        flash("Bet selection could not be processed.", "danger")
        return redirect(url_for('bets.live_betting'))

    if current_user.wallet.balance < amount:
        flash("Insufficient funds.", "danger")
        return redirect(url_for('bets.live_betting'))

    # Get or create sport
    sport = Sport.query.filter_by(name=sport_name).first()
    if not sport:
        sport = Sport(name=sport_name)
        db.session.add(sport)
        db.session.commit()

    # Get or create league
    league = League.query.filter_by(name=f"Live {sport_name}").first()
    if not league:
        league = League(name=f"Live {sport_name}", sport_id=sport.id)
        db.session.add(league)
        db.session.commit()

    # Get or create teams
    home_team = Team.query.filter_by(name=home_team_name).first()
    if not home_team:
        home_team = Team(name=home_team_name, league_id=league.id)
        db.session.add(home_team)

    away_team = Team.query.filter_by(name=away_team_name).first()
    if not away_team:
        away_team = Team(name=away_team_name, league_id=league.id)
        db.session.add(away_team)

    db.session.commit()

    # Create Game
    game = Game(
        home_team_id=home_team.id,
        away_team_id=away_team.id,
        league_id=league.id,
        start_time=datetime.utcnow() + timedelta(minutes=5),
        status='pending'
    )
    db.session.add(game)
    db.session.commit()

    # Create Market
    market = Market(
        game_id=game.id,
        market_type=market_type,
        odds_home=odds if selection_name == home_team.name else None,
        odds_away=odds if selection_name == away_team.name else None
    )
    db.session.add(market)
    db.session.commit()

    # Deduct from wallet
    current_user.wallet.balance -= amount

    # Create Bet
    payout = round(amount * odds, 2)
    bet = Bet(
        user_id=current_user.id,
        amount=amount,
        payout=payout,
        odds=odds,
        selection=selection_name,
        home_team=home_team.name,
        away_team=away_team.name,
        game_id=game.id,
        status="pending"
    )
    db.session.add(bet)
    db.session.commit()

    # Create BetSelection
    bet_selection = BetSelection(
        bet_id=bet.id,
        market_id=market.id,
        selection=selection_name,
        odds_at_bet_time=odds
    )
    db.session.add(bet_selection)

    # Log Transaction
    tx = Transaction(
        wallet_id=current_user.wallet.id,
        amount=-amount,
        type='bet'
    )
    db.session.add(tx)

    db.session.commit()

    flash(f"Bet placed on {selection_name} at {odds}", "success")
    return redirect(url_for('user.dashboard'))


@bets.route('/nba')
@login_required
def nba_betting():
    return redirect(url_for('bets.sport_odds', sport_key="basketball_nba"))

@bets.route('/nfl')
@login_required
def nfl_betting():
    return redirect(url_for('bets.sport_odds', sport_key="americanfootball_nfl"))

@bets.route('/mlb')
@login_required
def mlb_betting():
    return redirect(url_for('bets.sport_odds', sport_key="baseball_mlb"))

@bets.route('/mma')
@login_required
def mma_betting():
    return redirect(url_for('bets.sport_odds', sport_key="mma_mixed_martial_arts"))


@bets.route('/odds/<sport_key>')
@login_required
def sport_odds(sport_key):
    if sport_key not in SPORT_LABELS:
        return "Invalid sport.", 404

    events = get_odds(sport_key)
    label = SPORT_LABELS[sport_key]
    return render_template('bets/view_odds.html', events=events, label=label, sport_key=sport_key)


@bets.route('/game/<int:game_id>')
@login_required
def game_detail(game_id):
    game = Game.query.get_or_404(game_id)
    return render_template('bets/game_detail.html', game=game)


@bets.route('/live-betting/api')
@login_required
def live_betting_api():
    home_team = request.args.get('home_team')
    away_team = request.args.get('away_team')
    sport = request.args.get('sport', 'mma_mixed_martial_arts')

    if not home_team or not away_team:
        return "Missing teams", 400

    # Search live odds from API
    events = get_odds(sport)
    for event in events:
        if event['home_team'] == home_team and event['away_team'] == away_team:
            return render_template(
                'bets/live_bet_api.html',  # You'll create this template
                event=event,
                sport=sport
            )

    return "Game not found", 404
    
