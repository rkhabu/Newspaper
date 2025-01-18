from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, current_user
from extensions import db, app, login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime


class Article(db.Model):
    now = datetime.now()
    date_time = now.strftime("%d/%m/%Y, %H:%M:%S")

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=False, nullable=False)
    date = db.Column(db.String)
    text = db.Column(db.Text, unique=False, nullable=False)
    image = db.Column(db.String(80), unique=False, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    author = db.relationship('User', back_populates='articles')
    comments = db.relationship('Comment', backref='one_article', lazy=True)
    likes = db.relationship('Like', backref='article', lazy=True)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(50), default="guest")
    articles = db.relationship('Article', back_populates='author', lazy=True)

    # def __init__(self, username, password, role="guest"):
    #     self.username = username
    #     self.password = generate_password_hash(password)
    #     self.role = role
    #
    # def check_password(self, password):
    #     return check_password_hash(self.password, password)


class Comment(db.Model):
    now = datetime.now()
    date_time = now.strftime("%d/%m/%Y, %H:%M:%S")

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String)
    content = db.Column(db.Text, unique=False, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    article_id = db.Column(db.Integer, db.ForeignKey('article.id'), nullable=False)
    user = db.relationship('User', backref='comments')


class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    mail = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, unique=False, nullable=False)
    user_id = db.Column(db.Integer)


class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    article_id = db.Column(db.Integer, db.ForeignKey('article.id'), nullable=False)
    user = db.relationship('User', backref='likes')


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


if __name__ == "__main__":
    now = datetime.now()
    date_time = now.strftime("%d/%m/%Y, %H:%M:%S")
    articles = [{"name": "Lizard", "date": date_time, "text": "abcd", "image": "img1.jpeg", "id": 0, "user_id": 0},
                {"name": "Something One", "date": date_time, "text": "ef g", "image": "img2.jpeg", "id": 1, "user_id": 0},
                {"name": "Something Two", "date": date_time, "text": "ijkl", "image": "img3.jpeg", "id": 2, "user_id": 0}]

    with app.app_context():
        db.create_all()

        for article in articles:
            new_article = Article(name=article["name"], date=article["date"], text=article["text"], image=article["image"], user_id=0)
            db.session.add(new_article)
            db.session.commit()

        user = User(username="user", password="123")
        db.session.add(user)

        admin = User(username="admin", password="admin123", role="admin")
        db.session.add(admin)

        db.session.commit()
