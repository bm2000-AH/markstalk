import os
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from datetime import datetime
from app.forms import MessageForm, LoginForm, RegisterForm, PlaceForm, ReviewForm, ComplaintForm, ResponseForm


from app import db
from app.models import User, Place, Purchase, Review, Complaint, Chat, Message
from app.forms import LoginForm, RegisterForm, PlaceForm, ReviewForm, ComplaintForm

bp = Blueprint('main', __name__)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'jpg', 'jpeg', 'png', 'gif'}

@bp.route('/')
def index():
    places = Place.query.all()
    return render_template('index.html', places=places)

from app.models import Favorite

@bp.route('/favorites')
@login_required
def favorites():
    favorites = Place.query.join(Favorite).filter(Favorite.user_id == current_user.id).all()
    return render_template('favorites.html', places=favorites)


@bp.route('/favorite/<int:place_id>/toggle', methods=['POST'])
@login_required
def toggle_favorite(place_id):
    existing = Favorite.query.filter_by(user_id=current_user.id, place_id=place_id).first()
    if existing:
        db.session.delete(existing)
    else:
        new_fav = Favorite(user_id=current_user.id, place_id=place_id)
        db.session.add(new_fav)
    db.session.commit()
    return redirect(request.referrer or url_for('main.index'))

@bp.route('/search')
def search():
    query = request.args.get('q', '').lower()
    results = []
    if query:
        all_places = Place.query.all()
        results = [p for p in all_places if query in p.title.lower()]
    return render_template('search_results.html', query=query, results=results)

@bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if User.query.filter_by(username=form.username.data).first():
            flash('Имя пользователя уже занято.')
            return redirect(url_for('main.register'))
        user = User(username=form.username.data, password=form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Регистрация прошла успешно.')
        return redirect(url_for('main.login'))
    return render_template('register.html', form=form)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.password == form.password.data:
            login_user(user)
            flash('Вы вошли в систему.')
            return redirect(url_for('main.index'))
        flash('Неверные учетные данные.')
    return render_template('login.html', form=form)

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Вы вышли из системы.')
    return redirect(url_for('main.index'))

@bp.route('/place/new', methods=['GET', 'POST'])
@login_required
def create_place():
    form = PlaceForm()
    if form.validate_on_submit():
        filename = None
        if form.image.data and allowed_file(form.image.data.filename):
            filename = secure_filename(form.image.data.filename)
            path = os.path.join(os.getenv('UPLOAD_FOLDER', 'app/static/uploads'), filename)
            form.image.data.save(path)
        place = Place(
            title=form.title.data,
            description=form.description.data,
            latitude=form.latitude.data,
            longitude=form.longitude.data,
            price=form.price.data,
            image_file=filename,
            author=current_user
        )
        db.session.add(place)
        db.session.commit()
        flash('Место добавлено.')
        return redirect(url_for('main.index'))
    return render_template('create_place.html', form=form)

@bp.route('/place/<int:place_id>')
@login_required
def place_detail(place_id):
    place = Place.query.get_or_404(place_id)
    purchased = Purchase.query.filter_by(user_id=current_user.id, place_id=place.id).first()
    reviews = Review.query.filter_by(seller_id=place.user_id).all()
    return render_template('place_detail.html', place=place, purchased=bool(purchased), reviews=reviews)

@bp.route('/place/<int:place_id>/buy', methods=['POST'])
@login_required
def buy(place_id):
    place = Place.query.get_or_404(place_id)
    if place.user_id == current_user.id:
        flash('Вы не можете купить собственное место.')
        return redirect(url_for('main.place_detail', place_id=place.id))
    existing = Purchase.query.filter_by(user_id=current_user.id, place_id=place.id).first()
    if existing:
        flash('Вы уже купили это место.')
    else:
        purchase = Purchase(user_id=current_user.id, place_id=place.id)
        db.session.add(purchase)
        db.session.commit()
        flash('Покупка прошла успешно!')
    return redirect(url_for('main.place_detail', place_id=place.id))

@bp.route('/user/<int:user_id>/review', methods=['GET', 'POST'])
@login_required
def review_user(user_id):
    form = ReviewForm()
    if form.validate_on_submit():
        review = Review(
            reviewer_id=current_user.id,
            seller_id=user_id,
            text=form.text.data,
            rating=form.rating.data
        )
        db.session.add(review)
        db.session.commit()
        flash('Отзыв оставлен.')
        return redirect(url_for('main.index'))
    return render_template('review_form.html', form=form)

@bp.route('/user/<int:user_id>/complaint', methods=['GET', 'POST'])
@login_required
def complain_user(user_id):
    form = ComplaintForm()
    if form.validate_on_submit():
        complaint = Complaint(
            reporter_id=current_user.id,
            seller_id=user_id,
            text=form.text.data
        )
        db.session.add(complaint)
        db.session.commit()
        flash('Жалоба отправлена.')
        return redirect(url_for('main.index'))
    return render_template('complaint_form.html', form=form)

@bp.route('/chats')
@login_required
def chat_list():
    chats = Chat.query.filter(
        (Chat.user1_id == current_user.id) | (Chat.user2_id == current_user.id)
    ).all()
    return render_template('chats.html', chats=chats)

@bp.route('/chat/<int:chat_id>', methods=['GET', 'POST'])
@login_required
def chat_detail(chat_id):
    chat = Chat.query.get_or_404(chat_id)

    if chat.user1_id == current_user.id:
        other_user = chat.user2
    else:
        other_user = chat.user1

    form = MessageForm()

    if form.validate_on_submit():
        message = Message(
            chat_id=chat.id,
            sender_id=current_user.id,
            text=form.body.data,
            timestamp=datetime.utcnow()
        )
        db.session.add(message)
        db.session.commit()
        return redirect(url_for('main.chat_detail', chat_id=chat.id))  # чтобы избежать повторной отправки

    messages = Message.query.filter_by(chat_id=chat.id).order_by(Message.timestamp).all()

    return render_template(
        'chat_detail.html',
        chat=chat,
        messages=messages,
        form=form,
        other_user=other_user
    )

@bp.route('/chat/<int:chat_id>/edit/<int:message_id>', methods=['POST'])
@login_required
def edit_message(chat_id, message_id):
    message = Message.query.get_or_404(message_id)
    if message.sender_id != current_user.id:
        abort(403)
    new_text = request.form.get('text')
    if new_text:
        message.text = new_text
        message.timestamp = datetime.utcnow()
        db.session.commit()
    return redirect(url_for('main.chat_detail', chat_id=chat_id))

@bp.route('/chat/<int:chat_id>/delete/<int:message_id>', methods=['POST'])
@login_required
def delete_message(chat_id, message_id):
    message = Message.query.get_or_404(message_id)
    if message.sender_id != current_user.id:
        abort(403)
    db.session.delete(message)
    db.session.commit()
    return redirect(url_for('main.chat_detail', chat_id=chat_id))



@bp.route('/start_chat/<int:user_id>', methods=['POST'])
@login_required
def start_chat(user_id):
    if user_id == current_user.id:
        flash("Нельзя начать чат с самим собой.")
        return redirect(url_for('main.index'))

    existing = Chat.query.filter(
        ((Chat.user1_id == current_user.id) & (Chat.user2_id == user_id)) |
        ((Chat.user1_id == user_id) & (Chat.user2_id == current_user.id))
    ).first()

    if existing:
        return redirect(url_for('main.chat_detail', chat_id=existing.id))

    new_chat = Chat(user1_id=current_user.id, user2_id=user_id)
    db.session.add(new_chat)
    db.session.commit()
    return redirect(url_for('main.chat_detail', chat_id=new_chat.id))

@bp.route('/my_places')
@login_required
def my_places():
    places = Place.query.filter_by(user_id=current_user.id).all()
    return render_template('my_places.html', places=places)

@bp.route('/my_purchases')
@login_required
def my_purchases():
    purchases = Purchase.query.filter_by(user_id=current_user.id).all()
    return render_template('my_purchases.html', purchases=purchases)

@bp.route('/my_reviews')
@login_required
def my_reviews():
    reviews = Review.query.filter_by(reviewer_id=current_user.id).all()
    return render_template('my_reviews.html', reviews=reviews)

@bp.route('/reviews_about_me')
@login_required
def reviews_about_me():
    reviews = Review.query.filter_by(seller_id=current_user.id).all()
    return render_template('reviews_about_me.html', reviews=reviews)

@bp.route('/my_complaints')
@login_required
def my_complaints():
    complaints = Complaint.query.filter_by(reporter_id=current_user.id).all()
    return render_template('my_complaints.html', complaints=complaints)

@bp.route('/review/<int:review_id>/respond', methods=['GET', 'POST'])
@login_required
def respond_review(review_id):
    review = Review.query.get_or_404(review_id)
    if current_user.id != review.seller_id:
        abort(403)

    form = ResponseForm()
    if form.validate_on_submit():
        review.reply = form.response.data
        db.session.commit()
        flash('Ответ на отзыв сохранён.')
        return redirect(url_for('main.my_reviews'))

    form.response.data = review.reply or ''
    return render_template('response_form.html', form=form, target='отзыв')


@bp.route('/complaint/<int:complaint_id>/respond', methods=['GET', 'POST'])
@login_required
def respond_complaint(complaint_id):
    complaint = Complaint.query.get_or_404(complaint_id)
    if current_user.id != complaint.seller_id:
        abort(403)

    form = ResponseForm()
    if form.validate_on_submit():
        complaint.response = form.response.data
        db.session.commit()
        flash('Ответ на жалобу сохранён.')
        return redirect(url_for('main.my_complaints'))

    form.response.data = complaint.response or ''
    return render_template('response_form.html', form=form, target='жалобу')
