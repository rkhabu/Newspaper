from flask import Flask, render_template, request, redirect, flash, url_for
from forms import AddArticleForm, RegisterForm, LogInForm, Survey
from extensions import app, db
import os
from models import Article, User, Comment, Feedback, Like
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/us")
def us():
    return render_template("us.html")


@app.route("/plan")
def plan():
    return render_template("plan.html")


@app.route("/survey", methods=["GET", "POST"])
@login_required
def survey():
    form = Survey()

    if request.method == "POST":
        survey = Feedback(name=form.name.data, mail=form.mail.data, content=form.content.data, user_id=current_user.id)
        db.session.add(survey)
        db.session.commit()
        flash("Feedback Sent Successfully!", "success")
        return redirect("../../")

    return render_template("survey.html", form=form)


@app.route("/articles")
def articles():
    articles = Article.query.all()
    return render_template("articles.html", articles=articles)


@app.route("/add_article", methods=["GET", "POST"])
@login_required
def add_article():
    form = AddArticleForm()

    if request.method == "POST":

        now = datetime.now()  # current date and time
        date_time = now.strftime("%d/%m/%Y, %H:%M:%S")

        file = request.files.get("image")
        if file and file.filename:  # If file exists and has a name
            filename = file.filename
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
        else:
            filename = None

        article = Article(name=form.name.data, date=date_time, text=form.text.data, image=filename, user_id=current_user.id)
        db.session.add(article)
        db.session.commit()
        return redirect("../../articles")
    return render_template("add_article.html", form=form)


@app.route("/edit_article/<int:id>", methods=["GET", "POST"])
@login_required
def edit_article(id):
    selected_article = Article.query.get(id)
    form = AddArticleForm(name=selected_article.name, text=selected_article.text, image=selected_article.image)

    if request.method == "POST":
        file = request.files["image"]
        file.save(os.path.join(app.config["UPLOAD_FOLDER"], file.filename))
        selected_article.name = form.name.data
        selected_article.text = form.text.data
        selected_article.image = file.filename
        db.session.commit()
        return redirect("../../articles")

    return render_template("edit_article.html", form=form, selected_article=selected_article)


@app.route("/delete/<int:id>", methods=["GET", "POST"])
@login_required
def delete(id):
    selected_article = Article.query.get_or_404(id)
    Like.query.filter_by(user_id=current_user.id, article_id=selected_article.id).delete()
    Comment.query.filter_by(user_id=current_user.id, article_id=selected_article.id).delete()
    db.session.delete(selected_article)
    db.session.commit()
    return redirect("../../articles")


@app.route("/details/<int:id>", methods=["GET", "POST"])
@login_required
def details(id):
    selected_article = Article.query.get_or_404(id)

    if request.method == 'POST':
        if not current_user.is_authenticated:
            flash("You must be logged in to leave a comment!", "warning")
            return redirect(url_for("login"))

        content = request.form['content']
        if not content:
            flash("Comment cannot be empty!", "warning")

        now = datetime.now()
        date_time = now.strftime("%d/%m/%Y, %H:%M:%S")

        comment = Comment(content=content, date=date_time, user_id=current_user.id, article_id=id)
        db.session.add(comment)
        db.session.commit()
        flash("Comment Added Successfully!", "success")

    like = Like(user_id=current_user.id, article_id=id)
    like_user_ids = Like.query.filter_by(user_id=current_user.id, article_id=selected_article.id).first()
    if selected_article.user_id != 0:
        selected_user = User.query.get_or_404(selected_article.user_id)
    else:
        selected_user = 0
    return render_template("details.html", article=selected_article, like=like, like_user_ids=like_user_ids, selected_user=selected_user)


@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if request.method == 'POST':
        if User.query.filter_by(username=form.username.data).first():
            flash("This account is already registered!", "warning")
            return redirect("../../register")
        if form.password.data != form.repeat_password.data:
            flash("Passwords must be the same", "danger")
        if form.password.data == form.repeat_password.data:
            new_user = User(username=form.username.data, password=form.password.data)
            db.session.add(new_user)
            db.session.commit()
            flash(f"You Successfully Registered, Welcome, {form.username.data}!", "success")
            return redirect("../../")
    return render_template("register.html", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LogInForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        # if user and check_password_hash(user.password, form.password.data):
        if user and user.password == form.password.data:
            flash("You Logged In Successfully", "success")
            login_user(user)
            return redirect("../")
        else:
            flash("Invalid username or password", "danger")
    return render_template("login.html", form=form)


@app.route("/logout", methods=["GET", "POST"])
@login_required
def logout():
    logout_user()
    flash("You Logged Out Successfully", "success")
    return redirect("../../")


@app.route("/account/<int:id>")
@login_required
def account(id):
    articles = Article.query.all()
    article_user_ids = Article.query.filter_by(user_id=current_user.id).first()
    return render_template("account.html", id=current_user.id, articles=articles, article_user_ids=article_user_ids)


@app.route("/comment_edit/<int:article_id>/<int:comment_id>", methods=["GET", "POST"])
@login_required
def edit_comment(article_id, comment_id):
    all_comments = Comment.query.all()
    article = Article.query.get(article_id)
    flash("Enter the comment, press 'post comment' and the edited version will appear", "primary")

    if request.method == 'POST':
        if not current_user.is_authenticated:
            flash("You must be logged in to leave a comment!", "warning")
            return redirect(url_for("login"))

        content = request.form['content']
        if not content:
            flash("Comment cannot be empty!", "warning")

        for other_comment in all_comments:
            if other_comment.id == comment_id:
                now = datetime.now()
                date_time = now.strftime("%d/%m/%Y, %H:%M:%S")

                other_comment.content = content
                other_comment.date = date_time
                db.session.commit()
                flash("Comment Edited Successfully!", "success")
                return redirect(url_for('details', id=other_comment.article_id))

    like = Like(user_id=current_user.id, article_id=article_id)
    like_user_ids = Like.query.filter_by(user_id=current_user.id, article_id=article_id).first()
    if article.user_id != 0:
        selected_user = User.query.get_or_404(article.user_id)
    else:
        selected_user = 0
    return render_template("details.html", article=article, like=like, like_user_ids=like_user_ids, selected_user=selected_user)


@app.route("/comment_delete/<int:id>", methods=["GET", "POST"])
@login_required
def delete_comment(id):
    selected_comment = Comment.query.get_or_404(id)
    db.session.delete(selected_comment)
    db.session.commit()
    flash("Comment Removed Successfully!", "success")
    return redirect(url_for('details', id=selected_comment.article_id))


@app.route("/like/<int:article_id>", methods=["GET", "POST"])
@login_required
def like(article_id):

    like = Like.query.filter_by(user_id=current_user.id, article_id=article_id).first()
    if not like:
        new_like = Like(user_id=current_user.id, article_id=article_id)
        db.session.add(new_like)
        db.session.commit()
    else:
        db.session.delete(like)
        db.session.commit()

    return redirect(url_for('details', id=article_id))
