from datetime import datetime

from flask_login import UserMixin

from app import db


class User(db.Model, UserMixin):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(80), unique=True, nullable=False)
	password = db.Column(db.String(80), nullable=False)
	chinesepod_username = db.Column(db.Text, default="")
	chinesepod_password = db.Column(db.Text, default="")

	def get_id(self):
		return str(self.id)

	# Static
	def new(username, password):
		user = User(username=username, password=password)
		db.session.add(user)
		db.session.commit()
		return user

	def update_chinesepod_credentials(self, chinesepod_username, chinesepod_password):
		self.chinesepod_username = chinesepod_username
		self.chinesepod_password = chinesepod_password
		db.session.commit()


class Card(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
	user=db.relationship('User', backref=db.backref('card', lazy=True))
	created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
	phrase = db.Column(db.Text, nullable=False)
	translation = db.Column(db.Text)
	pinyin = db.Column(db.Text)
	audio = db.Column(db.LargeBinary)
	pending = db.Column(db.Boolean)

	# Static
	def new(user, phrase):
		card = Card(user=user, phrase=phrase, pending=True)
		db.session.add(card)
		db.session.commit()
		return card
	
	def update(self, translation, pinyin, audio):
		self.translation = translation
		self.pinyin = pinyin
		self.audio = audio
		self.pending = False
		db.session.commit()

	def delete(self):
		db.session.delete(self)
		db.session.commit()


if __name__ == '__main__':
	print('Creating database tables...')
	db.create_all()
	print('Done')
