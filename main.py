from datetime import date
from flask import Flask, abort, render_template, redirect, url_for, flash, request
from flask_bootstrap import Bootstrap5
from flask_ckeditor import CKEditor
from flask_gravatar import Gravatar
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Text
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from wtforms.fields.simple import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, email
from forms import CommentForm

from forms import CreatePostForm


app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
ckeditor = CKEditor(app)
Bootstrap5(app)

login_manager = LoginManager()
login_manager.init_app(app)
@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(User,user_id)

class RegisterForm(FlaskForm):
    email=StringField('Email',validators=[DataRequired()])
    password=PasswordField('password',validators=[DataRequired()])
    name=StringField('name',validators=[DataRequired()])
    submit=SubmitField('Submit')

class LoginForm(FlaskForm):
    email=StringField('Email',validators=[DataRequired()])
    password=PasswordField('password',validators=[DataRequired()])
    submit=SubmitField('Submit')



class Base(DeclarativeBase):
    pass
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)




class BlogPost(db.Model):
    __tablename__ = "blog_posts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    subtitle: Mapped[str] = mapped_column(String(250), nullable=False)
    date: Mapped[str] = mapped_column(String(250), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    author = relationship("User", back_populates="posts")
    img_url: Mapped[str] = mapped_column(String(250), nullable=False)
    author_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("users.id"))
    comments = relationship("Comment", back_populates="parent_post")


class User(UserMixin,db.Model):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email:Mapped[str]=mapped_column(String,nullable=False)
    password:Mapped[str]=mapped_column(String,nullable=False)
    username:Mapped[str]=mapped_column(String,nullable=False)
    posts = relationship("BlogPost", back_populates="author")
    comments = relationship("Comment", back_populates="comment_author")

with app.app_context():
    db.create_all()

class Comment(db.Model):
    __tablename__ = "comments"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    author_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("users.id"))
    comment_author = relationship("User", back_populates="comments")

    # ***************Child Relationship*************#
    post_id: Mapped[str] = mapped_column(Integer, db.ForeignKey("blog_posts.id"))
    parent_post = relationship("BlogPost", back_populates="comments")
    text: Mapped[str] = mapped_column(Text, nullable=False)

gravatar = Gravatar(app,
                    size=100,
                    rating='g',
                    default='retro',
                    force_default=False,
                    force_lower=False,
                    use_ssl=False,
                    base_url=None)

def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            print("User not authenticated.")
            flash("You need to log in to access this page.", "warning")
            return redirect(url_for('login'))

        print(f"Current User ID: {current_user.id}")

        # Check if the user ID is 10
        if current_user.id != 1:
            print(f"Access denied for user with ID: {current_user.id}")
            flash("You do not have permission to access this page.", "danger")
            return abort(403)

        print(f"Access granted for user with ID: {current_user.id}")
        return f(*args, **kwargs)

    return decorated_function


@app.route('/', methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():

        result = db.session.execute(db.select(User).where(User.email == form.email.data))
        user = result.scalar()
        if user:
            flash("You've already signed up with that email, log in instead!")
            return redirect(url_for('login'))

        hash_and_salted_password = generate_password_hash(
            form.password.data,
            method='pbkdf2:sha256',
            salt_length=8
        )
        new_user = User(
            email=form.email.data,
            username=form.name.data,
            password=hash_and_salted_password,
        )
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for("get_all_posts"))
    return render_template("register.html", form=form)

@app.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        user = db.session.execute(db.select(User).filter_by(email=email)).scalar_one_or_none()

        if user and check_password_hash(user.password, password):
            login_user(user)
            print(f"Logged-in User ID: {user.id}")
            flash("Successfully logged in!", "success")
            return redirect(url_for('get_all_posts'))
        else:
            flash("Invalid email or password. Please try again.", "danger")
    return render_template("login.html", form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('get_all_posts'))


@app.route('/get_all_posts')
def get_all_posts():
    result = db.session.execute(db.select(BlogPost))
    posts = result.scalars().all()
    return render_template("index.html", all_posts=posts)


@app.route("/post/<int:post_id>", methods=["GET", "POST"])
def show_post(post_id):
    requested_post = db.get_or_404(BlogPost, post_id)
    comment_form = CommentForm()

    # Handle comment form submission
    if comment_form.validate_on_submit():
        if current_user.is_authenticated:
            new_comment = Comment(
                author_id=current_user.id,
                post_id=requested_post.id,
                text=comment_form.comment_text.data  # Assuming `comment_text` is the field name in your form
            )
            db.session.add(new_comment)
            db.session.commit()
            flash("Your comment has been added!", "success")
            return redirect(url_for("show_post", post_id=post_id))
        else:
            flash("You need to log in to comment on posts.", "danger")
            return redirect(url_for("login"))

    # Render the post and form
    return render_template(
        "post.html",
        post=requested_post,
        current_user=current_user,
        form=comment_form
    )

@app.route("/new-post", methods=["GET", "POST"])
@admin_only
def add_new_post():
    form = CreatePostForm()
    if form.validate_on_submit():
        new_post = BlogPost(
            title=form.title.data,
            subtitle=form.subtitle.data,
            body=form.body.data,
            img_url=form.img_url.data,
            author=current_user,
            date=date.today().strftime("%B %d, %Y")
        )
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for("get_all_posts"))
    return render_template("make-post.html", form=form)


@app.route("/edit-post/<int:post_id>", methods=["GET", "POST"])
@admin_only
def edit_post(post_id):
    post = db.get_or_404(BlogPost, post_id)
    edit_form = CreatePostForm(
        title=post.title,
        subtitle=post.subtitle,
        img_url=post.img_url,
        author=post.author,
        body=post.body
    )
    if edit_form.validate_on_submit():
        post.title = edit_form.title.data
        post.subtitle = edit_form.subtitle.data
        post.img_url = edit_form.img_url.data
        post.author = current_user
        post.body = edit_form.body.data
        db.session.commit()
        return redirect(url_for("show_post", post_id=post.id))
    return render_template("make-post.html", form=edit_form, is_edit=True)


@app.route("/delete/<int:post_id>")
@admin_only
def delete_post(post_id):
    post_to_delete = db.get_or_404(BlogPost, post_id)
    db.session.delete(post_to_delete)
    db.session.commit()
    return redirect(url_for('get_all_posts'))


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


if __name__ == "__main__":
    app.run(debug=True, port=5002)
