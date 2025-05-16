from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from sportsbook.forms.wallet_forms import DepositForm
from ..extensions import db
from ..models import Wallet, Transaction

user = Blueprint('user', __name__)

@user.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    form = DepositForm()

    if form.validate_on_submit():
        amount = float(form.amount.data)

        # Ensure wallet exists
        if not current_user.wallet:
            wallet = Wallet(user_id=current_user.id, balance=0.0)
            db.session.add(wallet)
            db.session.commit()

        # Update balance
        current_user.wallet.balance += amount
        db.session.commit()

        # Log the transaction
        transaction = Transaction(
            wallet_id=current_user.wallet.id,
            amount=amount,
            type='deposit'
        )
        db.session.add(transaction)
        db.session.commit()

        flash(f'Deposited ${amount:.2f} into your wallet.', 'success')
        return redirect(url_for('user.dashboard'))

    # ✅ Get most recent 5 bets
    recent_bets = sorted(current_user.bets, key=lambda b: b.created_at, reverse=True)[:5]

    # ✅ Get all transactions
    transactions = sorted(current_user.wallet.transactions, key=lambda t: t.timestamp, reverse=True) if current_user.wallet else []

    return render_template(
        'user/dashboard.html',
        user=current_user,
        form=form,
        transactions=transactions,
        recent_bets=recent_bets
    )


@user.route('/my-bets')
@login_required
def my_bets():
    bets = current_user.bets  # Already defined via relationship
    return render_template('user/my_bets.html', bets=bets)