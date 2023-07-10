from flask import Flask, request, redirect, render_template, session, flash
from forms import RegisterUserForm, LoginUserForm, AddFeedbackForm, UpdateFeedbackForm
from models import db, connect_db, User, bcrypt, Feedback


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///feedback_exercise'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = 'this key'

connect_db(app)

# Upon connection, drop all tables and create new tables (based on models provided)
# Comment this out if you need to test data extraction when closing and opening flask
with app.app_context():
    db.drop_all()
    db.create_all()


@app.route('/')
def return_to_register():
    return redirect('/register')

@app.route('/register', methods=["GET", "POST"])
def register_form():
    session.pop('user_id', None)
    form = RegisterUserForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        email = form.email.data
        first_name = form.first_name.data
        last_name = form.last_name.data
        with app.app_context():
            new_user = User.register(username, password, email, first_name, last_name)
            if new_user:
                db.session.add(new_user)
                db.session.commit()
                all_users = User.query.all()
                new_user_index = (len(all_users) - 1)
                new_user = all_users[new_user_index]
                session['user_id'] = new_user.id
                return redirect('/users/' + str(new_user.id))
            else:
                flash(f'Username {username} is already taken.')
                return render_template('registration.html', form=form)
    else:
        return render_template('registration.html', form=form)

@app.route('/login', methods=["GET", "POST"])
def login_form():
    form = LoginUserForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        with app.app_context():
            potential_user = User.authenticate(username, password)
            if User.authenticate(username, password):
                session['user_id'] = potential_user.id
                return redirect('/users/' + str(potential_user.id))
            else:
                flash('Invalid username/password')
                return render_template('login.html', form=form)
    else:
        return render_template('login.html', form=form)

@app.route('/users/<int:user_id>')
def success(user_id):
    if session['user_id']:
        user_id = request.view_args['user_id']
        with app.app_context():
            user_page = User.query.get_or_404(user_id)
            all_feedback = Feedback.query.filter(Feedback.user_id == user_id).all()
        return render_template('user.html', user=user_page, feedbacks=all_feedback)
    else:
        return '<h1>You must be a user to access this</h1>'

@app.route('/logout', methods=["POST"])
def logout():
    session.pop('user_id', None)
    return redirect('/login')

@app.route('/users/<int:user_id>/delete', methods=["POST"])
def delete_user(user_id):
    # Only allow the user with the given user_id to delete their account
    url_id = request.view_args['user_id']
    if session["user_id"] == url_id:
        with app.app_context():
            # Delete any feedback associated with the user (otherwise the foreign key constraint will be raised)
            Feedback.query.filter(Feedback.user_id == url_id).delete()
            db.session.commit()
            # Once all feedback has been deleted, delete the user from the database
            User.query.filter(User.id == url_id).delete()
            db.session.commit()
        # Remove user_id from session and redirect to login screen
        session.pop('user_id', None)
        return redirect('/register')

@app.route('/users/<int:user_id>/feedback/add', methods=["GET", "POST"])
def add_feedback(user_id):
    # Extract a few essential values (the user_id and form)
    url_id = request.view_args['user_id']
    form = AddFeedbackForm()
    
    # Only allow the user with the given user_id to add feedback on their account
    if session["user_id"] == url_id:
        if form.validate_on_submit():
            
            # Extract form data
            title = form.title.data
            content = form.content.data
            
            # Use class method and add/commit to database
            new_feedback = Feedback.add(title, content, url_id)
            with app.app_context():
                db.session.add(new_feedback)
                db.session.commit()
            return redirect('/users/' + str(url_id))
        
        else:
            # Extract information on user and pass it to the template
            with app.app_context():
                current_user = User.query.get(url_id)
            return render_template('add_feedback.html', form=form, user=current_user)
    
    # If the user is not the user listed in the url (but is logged in), then the page will redirect back to their respective user page
    elif session["user_id"]:
        return redirect('/users/' + str(session["user_id"]))
    
    # If the user is not logged in, then the page will redirect to the login page
    else:
        return redirect('/login')

@app.route('/feedback/<int:feedback_id>/update', methods=["GET", "POST"])
def update_feedback(feedback_id):
    # Extract a few essential values and define the form
    url_id = request.view_args['feedback_id']
    form = UpdateFeedbackForm()
    with app.app_context():
        feedback = Feedback.query.get_or_404(url_id)
        user_id = feedback.user_id
    
    # If the user is the author of the feedback, then the routes will work
    if session["user_id"] == url_id:
        
        if form.validate_on_submit():
            
            # Extract form data
            title = form.title.data
            content = form.content.data
            
            # Extract the feedback instance you are updating
            with app.app_context():
                current_feedback = Feedback.query.get(url_id)

                # If any of form data is empty, then the value for that field will remain unchanged (otherwise, it will be edited with the form data)
                if title:
                    current_feedback.title = title
                if content:
                    current_feedback.content = content

                # Add/Commit the changes to the database and redirect the user to their respective user page
                db.session.add(current_feedback)
                db.session.commit()
                return redirect('/users/' + str(user_id))
        
        else:
            # Extract information on feedback and pass it to the template
            with app.app_context():
                current_feedback = Feedback.query.get(url_id)
            return render_template('update_feedback.html', form=form, feedback=current_feedback)
    
    # If the user_id in session does not correspond with the user_id in feedback (but the user is logged in), the page will redirect back to their respective user page
    elif session["user_id"]:
        return redirect('/users/' + str(session["user_id"]))
    
    # If the user is not logged in, the page will redirect to the login page
    else:
        return redirect('/login')

@app.route('/feedback/<int:feedback_id>/delete', methods=["POST"])
def delete_feedback(feedback_id):
    url_id = request.view_args['feedback_id']
    with app.app_context():
        feedback = Feedback.query.get_or_404(url_id)
        user_id = feedback.user_id
    
    # If the user is the author of the feedback, then the feedback can be deleted. 
    # Otherwise, the page will indicate that the user can't delete the feedback.
    if session["user_id"] == user_id:
        with app.app_context():
            Feedback.query.filter(Feedback.id == url_id).delete()
            db.session.commit()
        return redirect('/users/' + str(user_id))
    else:
        return '<h1>You cannot delete feedback that is not yours</h1>'