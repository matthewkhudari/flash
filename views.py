import time

from flask import render_template, request, redirect, url_for, session, Response
from flask import flash as flask_flash
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.security import check_password_hash, generate_password_hash

from redis import Redis
from rq import Queue

from app import app
from models import User, Card
from scraper import Scraper

def make_card(card_id, is_sentence, credentials):
	card = Card.query.filter_by(id=card_id).first()
	s = Scraper(credentials=credentials)
	if is_sentence:
		scraped_data = s.scrape_sentence(card.phrase)
	else:
		scraped_data = s.scrape_word(card.phrase)
	card.update(scraped_data[3], scraped_data[0], scraped_data[1])


@app.route('/')
def index():
	return render_template('index.html')


@app.route('/home', methods=('GET', 'POST'))
@login_required
def home():
	if request.method == 'POST':
		if 'submit' in request.form:
			# Download selected cards
			to_download = tuple(int(id) for id in request.form.getlist('download'))
			cards = Card.query.filter(Card.id.in_(to_download)).all()
			retval = ''
			for card in cards:
				audio_filename = 'flashcard{}.mp3'.format(card.id) if card.audio else '#####.mp3'
				retval += (
					card.pinyin + '\n' +
					'[sound:' + audio_filename + ']\n' +
					card.phrase + '\n' +
					card.translation + '\n\n'
				)
			return Response(
				retval,
				mimetype="text/plain",
				headers={"Content-disposition":
							"attachment; filename=flashcards.txt"}
			)
		# Else, download audio file
		for key in request.form.keys():
			try:
				id = int(key)
			except ValueError:
				pass
			else:
				card = Card.query.filter_by(id=id).first()
				if card is None:
					continue
				filename = 'flashcard{}.mp3'.format(card.id) if card.audio else '#####.mp3'
				return Response(
					card.audio,
					mimetype='audio/mpeg',
					headers={'Content-disposition':
								'attachment; filename='+filename}
				)
		flask_flash('No audio file found: no valid card id given')
	cards = Card.query.filter_by(user_id=current_user.id, pending=False).all()[::-1]
	in_progress = Card.query.filter_by(user_id=current_user.id, pending=True).all()
	return render_template('home.html', cards=cards, in_progress=in_progress)


@app.route('/create', methods=('GET', 'POST'))
@login_required
def create():
	if request.method == 'POST':
		phrase = request.form['phrase']
		is_sentence = len(request.form.getlist('is-sentence')) > 0
		error = None

		if not phrase:
			error = 'Phrase is required'

		if error is None:
			q = Queue(connection=Redis())
			card = Card.new(current_user, phrase)
			credentials = (current_user.chinesepod_username, current_user.chinesepod_password)
			q.enqueue(make_card, card.id, is_sentence, credentials)
			return redirect(url_for('home'))

		flask_flash(error)

	return render_template('create.html')



def get_card(id, check_user=True):
	card = Card.query=filter_by(id=id).first()

	if card is None:
		abort(404, "Card id {0} doesn't exist.".format(id))

	if check_user and card.user_id != current_user.id:
		abort(403)

	return card


@app.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
	card = get_card(id)
	card.delete()
	return redirect(url_for('home'))





@app.route('/credentials', methods=('GET', 'POST'))
@login_required
def credentials():
	if request.method == 'POST':
		chinesepod_username = request.form['chinesepod-username']
		chinesepod_password = request.form['chinesepod-password']
		error = None

		if not chinesepod_username:
			error = 'Chinesepod username is required'
		elif not chinesepod_password:
			error = 'Chinesepod password is required'

		s = Scraper(credentials=(chinesepod_username, chinesepod_password))
		if not s.verify_chinesepod_credentials():
			error = 'Invalid credentials'

		if error is None:
			current_user.update_chinesepod_credentials(chinesepod_username, chinesepod_password)

		flask_flash(error or 'Credentials updated successfully')

	return render_template('credentials.html')





@app.route('/register', methods=('GET', 'POST'))
def register():
	if request.method == 'POST':
		username = request.form['username']
		password = request.form['password']
		error = None

		if not username:
			error = 'Username is required.'
		elif not password:
			error = 'Password is required.'
		elif User.query.filter_by(username=username).first() is not None:
			error = 'User {} is already registered.'.format(username)

		if error is None:
			User.new(username, generate_password_hash(password))
			return redirect(url_for('login'))

		flask_flash(error)

	return render_template('register.html')


@app.route('/login', methods=('GET', 'POST'))
def login():
	if request.method == 'POST':
		username = request.form['username']
		password = request.form['password']
		remember = len(request.form.getlist('remember-me')) > 0
		error = None
		user = User.query.filter_by(username=username).first()

		if user is None:
			error = 'Incorrect username.'
		elif not check_password_hash(user.password, password):
			error = 'Incorrect password.'

		if error is None:
			login_user(user, remember=remember)
			return redirect(url_for('home'))

		flask_flash(error)

	return render_template('login.html')


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))
