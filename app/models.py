from datetime import datetime
from app import db, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    """Пользователь системы"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    avatar = db.Column(db.String(120), default='default.jpg')
    bio = db.Column(db.Text, default='')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Отношения
    places = db.relationship('Place', backref='author', lazy=True)
    purchases = db.relationship('Purchase', backref='user', lazy=True)
    favorites = db.relationship('Favorite', backref='user', lazy=True)

    reviews_written = db.relationship('Review', foreign_keys='Review.reviewer_id', backref='reviewer', lazy=True)
    reviews_received = db.relationship('Review', foreign_keys='Review.seller_id', backref='seller', lazy=True)

    complaints_made = db.relationship('Complaint', foreign_keys='Complaint.reporter_id', backref='reporter', lazy=True)
    complaints_received = db.relationship('Complaint', foreign_keys='Complaint.seller_id', backref='complained_user', lazy=True)

    chats_as_user1 = db.relationship('Chat', foreign_keys='Chat.user1_id', backref='user1', lazy=True)
    chats_as_user2 = db.relationship('Chat', foreign_keys='Chat.user2_id', backref='user2', lazy=True)

    messages_sent = db.relationship('Message', backref='sender', lazy=True)


class Place(db.Model):
    """Продаваемое место"""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    image_file = db.Column(db.String(120), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    purchases = db.relationship('Purchase', backref='place', lazy=True)
    favorites = db.relationship('Favorite', backref='place', lazy=True)
    complaints = db.relationship('Complaint', backref='place', lazy=True)


class Purchase(db.Model):
    """Покупка места"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    place_id = db.Column(db.Integer, db.ForeignKey('place.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


class Favorite(db.Model):
    """Избранные места"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    place_id = db.Column(db.Integer, db.ForeignKey('place.id'), nullable=False)

    __table_args__ = (db.UniqueConstraint('user_id', 'place_id', name='_user_place_uc'),)


class Review(db.Model):
    """Отзыв от покупателя продавцу"""
    id = db.Column(db.Integer, primary_key=True)
    reviewer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    seller_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    text = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    reply = db.Column(db.Text, nullable=True)  # Ответ продавца на отзыв


class Complaint(db.Model):
    """Жалоба на продавца"""
    id = db.Column(db.Integer, primary_key=True)
    reporter_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    seller_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    text = db.Column(db.Text, nullable=False)
    response = db.Column(db.Text, nullable=True)  # Ответ продавца на жалобу
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    place_id = db.Column(db.Integer, db.ForeignKey('place.id'), nullable=True)


class Chat(db.Model):
    """Чат между двумя пользователями"""
    id = db.Column(db.Integer, primary_key=True)
    user1_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user2_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    messages = db.relationship('Message', backref='chat', lazy=True)


class Message(db.Model):
    """Сообщение в чате"""
    id = db.Column(db.Integer, primary_key=True)
    chat_id = db.Column(db.Integer, db.ForeignKey('chat.id'), nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    text = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
