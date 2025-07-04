from flask import Flask, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
from flask_admin import Admin, AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView
from flask_migrate import Migrate
from flask_wtf import CSRFProtect
from wtforms.fields import BooleanField
from config import Config

# Расширения
db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()
login_manager.login_view = 'main.login'

# 🔒 Безопасная домашняя страница админки
class AdminHomeView(AdminIndexView):
    @expose('/')
    def index(self):
        if not current_user.is_authenticated or not current_user.is_admin:
            return redirect(url_for('main.login'))
        return super().index()

# 🔒 View только для модели User
class UserAdminView(ModelView):
    form_overrides = {
        'is_admin': BooleanField
    }

    form_args = {
        'is_admin': {
            'label': 'Админ?',
            'default': False
        }
    }

    can_create = False
    can_edit = False
    can_delete = True

    column_exclude_list = ['password']
    form_excluded_columns = ['password']

    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('main.login'))

# 🔒 Общий View для моделей
class AdminOnlyModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('main.login'))

    def on_model_change(self, form, model, is_created):
        if is_created and hasattr(model, 'user_id') and not model.user_id:
            model.user_id = current_user.id

# ❌ Запрет удаления Place с покупками
class PlaceAdminView(AdminOnlyModelView):
    def delete_model(self, model):
        if hasattr(model, 'purchases') and model.purchases:
            flash("\u274c Нельзя удалить место — к нему привязаны покупки.", 'error')
            return False
        return super().delete_model(model)

# Инициализация админки
admin = Admin(name='Админка', template_mode='bootstrap4', index_view=AdminHomeView())

# ✅ Фабрика приложения
def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Инициализация расширений
    db.init_app(app)
    csrf.init_app(app)       # ✅ CSRF init
    login_manager.init_app(app)
    Migrate(app, db)

    # Импорт моделей и блюпринтов
    from app.models import User, Place, Purchase, Review, Complaint, Favorite
    from app.routes import bp as main_bp
    app.register_blueprint(main_bp)

    # Админ-панель
    admin.init_app(app)
    admin.add_view(UserAdminView(User, db.session))
    admin.add_view(PlaceAdminView(Place, db.session))
    admin.add_view(AdminOnlyModelView(Purchase, db.session))
    admin.add_view(AdminOnlyModelView(Review, db.session))
    admin.add_view(AdminOnlyModelView(Complaint, db.session))

    with app.app_context():
        db.create_all()

    return app
