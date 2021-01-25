from flask import Flask, render_template, request
from flask_wtf import Form
from wtforms import StringField, PasswordField, IntegerField, validators, DateTimeField, FloatField
from wtforms.validators import InputRequired, Email, Length, AnyOf
from flask_bootstrap import Bootstrap
from wtforms import ValidationError
from datetime import datetime
from flask import jsonify, make_response
from flask import abort, redirect, url_for

app = Flask(__name__)
Bootstrap(app)
app.config['SECRET_KEY'] = 'DontTellAnyone'


class LoginForm(Form):

	# card_no = StringField('Credit Card Number',  render_kw={"placeholder": "xxxx-xxxx-xxxx-xxxx"},  validators=[InputRequired(), Length(max=16)])
	card_holder = StringField('Card Holder', render_kw={"autocomplete": "off"}, validators=[InputRequired()])
	expiry_date = DateTimeField('Expiration Date',  format='%m/%y', render_kw={"placeholder": "MM / YY"}, validators=[InputRequired()])
	security_code = PasswordField('Security Code', render_kw={"placeholder": "Optional"}, validators=[validators.optional(), Length(max=3)])
	amount = FloatField('Amount', render_kw={"autocomplete": "off", "placeholder": '€'})


	# suffix must contain name of the field and prefix should be validate.

	counter = 0

	@classmethod
	def update(cls):
		cls.counter += 1

	def validate_card_holder(self, field):
		if field.data.isalpha() is not True:
			LoginForm.update()
			raise ValidationError("Please Enter Card Holder Name Not Digits")


	def validate_expiry_date(self, field):
		current_year = datetime.now().year
		if field.data.year < current_year:
			global counter
			LoginForm.update()
			raise ValidationError("Expiration Year Should Not be in Past")

	def validate_amount(self, field):
		if field.data < 0:
			LoginForm.update()
			raise ValidationError("Amount should not be Negative.Try to Enter Amount again")


@app.route('/',  methods=['GET', 'POST'])
def ProcessPayment():

	form = LoginForm()
	card_no = request.form.get('card_no')
	print(card_no)
	c_holder = form.card_holder.data
	print(c_holder)
	edate = form.expiry_date.data
	print(edate)
	amount = form.amount.data
	print(amount)
	if form.validate_on_submit():
		if form.amount.data < 20:
			return redirect(url_for('cheap_payment_gateway',  cn=card_no, ch=c_holder, ed=edate, am=amount))
		elif (form.amount.data > 21) and (form.amount.data <= 500):
			return redirect(url_for('expensive_payment_gateway', cn=card_no, ch=c_holder, ed=edate, am=amount))
		else:
			print(LoginForm.counter)
			if LoginForm.counter <= 2:
				return redirect(url_for('premium_payment_gateway',  cn=card_no, ch=c_holder, ed=edate, am=amount))
			else:
				return redirect(url_for('failed'))

	return render_template('index1.html', form=form)


@app.route('/cheap_payment_gateway/<cn>/<ch>/<ed>/<am>')
def cheap_payment_gateway(cn, ch, ed, am):
	form = LoginForm()
	return render_template('CheapGateway.html',  cn=cn, ch=ch, ed=ed, am=am), 200


@app.route('/expensive_payment_gateway/<cn>/<ch>/<ed>/<am>')
def expensive_payment_gateway(cn, ch, ed, am):
	return render_template('ExpensiveGateway.html', cn=cn, ch=ch, ed=ed, am=am), 200


@app.route('/premium_payment_gateway/<cn>/<ch>/<ed>/<am>')
def premium_payment_gateway(cn, ch, ed, am):
	form = LoginForm()
	return render_template('PremiumGateway.html', cn=cn, ch=ch, ed=ed, am=am), 200


@app.route('/Payment', methods=['GET', 'POST'])
def BadRequest400():
	abort(400, "The Request is Invalid.Status Code :  400")


@app.route('/payment_success')
def payment_success():
	return render_template('payment_success.html')


@app.route('/premium_success')
def premium_success():
	return render_template('premium_success.html')


@app.route('/cheap_payment_gateway_success')
def cheap_payment_gateway_success():
	return render_template('cheap payment success.html')


@app.route('/failed')
def failed():
	return '''<h1>Tried 3 times but Your request is not get processed.Try again within few hours..</h1>'''


if __name__ == '__main__':
	app.run(debug=True)
