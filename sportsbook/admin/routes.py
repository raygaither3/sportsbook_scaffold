from flask import Blueprint, render_template, redirect, request, url_for, flash
from flask_login import login_required, current_user
from ..extensions import db
from ..models import Bet, Wallet
from ..models import Game, Bet, Transaction

admin = Blueprint('admin', __name__)

def admin_required(f):
    from functools import wraps
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash("Access denied.", "danger")
            return redirect(url_for("main.home"))
        return f(*args, **kwargs)
    return wrapper

@admin.route('/bets')
@login_required
@admin_required
def manage_bets():
    all_bets = Bet.query.order_by(Bet.created_at.desc()).all()
    return render_template('admin/manage_bets.html', bets=all_bets)

@admin.route('/bets/<int:bet_id>/<status>')
@login_required
@admin_required
def update_bet_status(bet_id, status):
    bet = Bet.query.get_or_404(bet_id)

    if status not in ['won', 'lost', 'void']:
        flash("Invalid status.", "danger")
        return redirect(url_for('admin.manage_bets'))

    # Only pay out if newly marked as won
    if bet.status != 'won' and status == 'won':
        user_wallet = bet.user.wallet
        user_wallet.balance += bet.payout

        from ..models import Transaction
        tx = Transaction(
            wallet_id=user_wallet.id,
            amount=bet.payout,
            type='payout'
        )
        db.session.add(tx)

    bet.status = status
    db.session.commit()

    flash(f"Bet #{bet.id} marked as {status.upper()}.", "success")
    return redirect(url_for('admin.manage_bets'))


@admin.route('/games')
@login_required
@admin_required
def manage_games():
    games = Game.query.order_by(Game.start_time.desc()).all()
    return render_template('admin/manage_games.html', games=games)

@admin.route('/games/<int:game_id>/update', methods=['POST'])
@login_required
@admin_required
def update_game_result(game_id):
    game = Game.query.get_or_404(game_id)
    game.final_score_home = int(request.form.get('score_home'))
    game.final_score_away = int(request.form.get('score_away'))
    game.method_of_victory = request.form.get('method')
    game.round_ended = int(request.form.get('round'))
    game.status = 'completed'
    db.session.commit()

    # Auto-settle related bets
    for market in game.markets:
        for bet in market.selections[0].bet.user.bets:
            if bet.status != 'pending':
                continue  # Already settled

            selection = bet.selections[0]
            selected_side = selection.selection

            # Determine winner
            if game.final_score_home > game.final_score_away:
                winner = 'home'
            elif game.final_score_away > game.final_score_home:
                winner = 'away'
            else:
                bet.status = 'void'
                db.session.commit()
                continue

            # Settle
            if selected_side == winner:
                bet.status = 'won'
                bet.user.wallet.balance += bet.payout
                db.session.add(Transaction(
                    wallet_id=bet.user.wallet.id,
                    amount=bet.payout,
                    type='payout'
                ))
            else:
                bet.status = 'lost'

            db.session.commit()

    flash(f"Game #{game.id} updated and related bets settled.", "success")
    return redirect(url_for('admin.manage_games'))