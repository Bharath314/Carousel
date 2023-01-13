import os, secrets
from flask import render_template, url_for, flash, redirect, request, abort
from carousel import app, db
from carousel.forms import RegistrationForm, LoginForm, UpdateAccountForm, PostForm, SearchBar
from carousel.models import User, Post, Followers, current_user


@app.route("/")
@app.route("/home")
def home():
    return render_template(
        'feed.html',
        posts=reversed(Post.query.all()),
        current_user=current_user,
    )


def save_dp(form):
    _, picture_fn = os.path.splitext(form.display_picture.data.filename)
    picture_fn = current_user.username + picture_fn
    picture_path = os.path.join(
        app.root_path, 'static/profile_pictures', picture_fn)
    form.display_picture.data.save(picture_path)
    return picture_fn


@app.route('/profile', methods=['GET', 'POST'])
def profile():
    form = UpdateAccountForm(current_username=current_user.username)
    print(current_user.display_picture)
    print(os.path.join(
                        app.root_path, 'static/profile_pictures/default.png'))
    print(current_user.display_picture != os.path.join(
        app.root_path, 'static/profile_pictures/default.png'
    ))
    if form.validate_on_submit():
        user_to_update = User.query.filter_by(username=current_user.username).first()
        user_to_update.username = form.username.data
        if form.display_picture.data:
            user_to_update.display_picture = save_dp(form)
        else:
            _, dp_name_update = os.path.splitext(current_user.display_picture)
            dp_name_update = form.username.data + dp_name_update
            
            if current_user.display_picture != '/static/profile_pictures/default.png':
                os.rename(
                    os.path.join(
                        app.root_path, 'static/profile_pictures', current_user.display_picture.split('/')[-1]
                    ),
                    os.path.join(
                        app.root_path, 'static/profile_pictures', dp_name_update
                    )
                )
                user_to_update.display_picture = dp_name_update
        db.session.commit()
        current_user.login(user_to_update)
    if request.method == 'GET':
        form.username.data = current_user.username
    return render_template(
        'profile.html',
        title = 'Profile',
        form = form,
        posts=list(reversed(Post.query.filter_by(
            user_id=current_user.user_id
        ).all())),
        followers = [follower.follower_id for follower in Followers.query.filter_by(followed_id = current_user.user_id).all()],
        following = [followee.followed_id for followee in Followers.query.filter_by(follower_id = current_user.user_id).all()],
        current_user = current_user
    )


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, password=form.password.data)
        db.session.add(user)
        db.session.commit()
        flash(f'Account created for {form.username.data}!', 'success')
        return redirect(url_for('home'))
    return render_template('register.html', title='Register', form=form, current_user=current_user)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.password == form.password.data:
            current_user.login(user)
            flash(f'Welcome back {current_user.username}', 'success')
            return redirect(url_for('home'))
        else:
            flash('Please check your credentials', 'danger')
    return render_template('login.html', title='Login', form=form, current_user=current_user)



@app.route("/logout")
def logout():
    current_user.logout()
    return redirect(url_for('home'))


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/posts', picture_fn)
    form_picture.save(picture_path)
    return picture_fn


@app.route("/post/new", methods=['GET', 'POST'])
def create_post():
    form = PostForm()
    if form.validate_on_submit():
        if form.picture.data:
            post = Post(
                caption = form.caption.data,
                image_file = save_picture(form.picture.data),
                user_id = current_user.user_id
            )
        else:
            post = Post(
                caption = form.caption.data,
                user_id = current_user.user_id
            )
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('post.html',
        title = 'New Post',
        form = form,
        legend = 'New Post',
        current_user = current_user
    )


@app.route('/<string:username>')
def user_posts(username):
    print(username)
    user = User.query.filter_by(username=str(username)).first()
    return render_template(
        'user_posts.html',
        title =  username,
        user = user,
        posts=list(reversed(Post.query.filter_by(
            user_id=user.id
        ).all())),
        followers = [follower.follower_id for follower in Followers.query.filter_by(followed_id = user.id).all()],
        following = [followee.followed_id for followee in Followers.query.filter_by(follower_id = user.id).all()],
        current_user=current_user
    )

@app.route('/<string:username>/<int:post_id>/update', methods=['GET', 'POST'])
def update_post(post_id, username):
    post = Post.query.get_or_404(post_id)
    if post.author.username != current_user.username:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        if form.picture.data:
            post.caption = form.caption.data
            if post.image_file:
                os.remove(os.path.join(app.root_path, 'static/posts', post.image_file))
            post.image_file = save_picture(form.picture.data)
        else:
            post.caption = form.caption.data
        db.session.commit()
        flash('Your post has been updated!', 'success')
        return redirect(url_for('home'))
    elif request.method == 'GET':
        form.caption.data = post.caption
        form.picture.data = "Upload to replace picture"
    return render_template(
        'post.html',
        title = 'Update Post',
        form = form,
        legend = 'Update Post',
        current_user = current_user
    )


@app.route('/<string:username>/<int:post_id>/delete', methods=['GET', 'POST'])
def delete_post(post_id,username):
    post = Post.query.get_or_404(post_id)
    if post.author.username != current_user.username:
        abort(403)
    os.remove(os.path.join(app.root_path, 'static/posts', post.image_file))
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted!', 'success')
    return redirect(url_for('home'))

@app.route('/search', methods = ['POST', 'GET'])
def search():
    form = SearchBar()
    if form.validate_on_submit():
        return render_template(
        'search.html',
        form = form,
        current_user = current_user
    )
    return render_template(
        'search.html',
        form = form,
        current_user = current_user
    )

@app.route('/<int:user_id>/follow')
def follow(user_id):
    connection = Followers(followed_id = user_id, follower_id = current_user.user_id)
    db.session.add(connection)
    db.session.commit()
    username = User.query.filter_by(id = user_id).first().username
    flash(f"You are now following {username}", 'success')
    return redirect(url_for('user_posts', username = username))


@app.route('/<int:user_id>/unfollow')
def unfollow(user_id):
    connection = Followers.query.get((user_id, current_user.user_id))
    print(connection)
    db.session.delete(connection)
    db.session.commit()
    username = User.query.filter_by(id = user_id).first().username
    flash(f"You are no longer following {username}", 'secondary')
    return redirect(url_for('user_posts', username = username))
