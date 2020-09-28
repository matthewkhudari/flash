from app import login_manager
from models import User

@login_manager.user_loader
def load_user(user_id):
	return User.query.filter_by(id=int(user_id)).first()

