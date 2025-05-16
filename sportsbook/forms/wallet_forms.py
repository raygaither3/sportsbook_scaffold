from flask_wtf import FlaskForm
from wtforms import DecimalField, SubmitField
from wtforms.validators import DataRequired, NumberRange

class DepositForm(FlaskForm):
    amount = DecimalField("Amount ($)", validators=[DataRequired(), NumberRange(min=1)], places=2)
    submit = SubmitField("Deposit")