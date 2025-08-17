from flask import Flask, render_template, request, redirect, url_for, make_response, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, UserMixin, current_user
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import re
from flask import session

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///anime.db"
app.config['SECRET_KEY'] = 'supersecretkey'
db = SQLAlchemy(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)


class Anime_list(db.Model):
    Sno = db.Column(db.Integer, primary_key=True)
    Anime_name = db.Column(db.String(200), nullable=False)
    Anime_desc = db.Column(db.String(500), nullable=False)
    Date_created = db.Column(db.DateTime, default=datetime.utcnow)
    Watch = db.Column(db.String(100))
    Watch_Status = db.Column(db.String(50), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))  

    def __repr__(self):
        return f"{self.Anime_name} - {self.Anime_desc}"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def is_strong_password(password):
    return len(password) >= 8


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')      
        password = request.form.get('password')

        if not email or not password:
            flash('Please fill out both email and password.', 'error')
            return redirect(url_for('register'))
        
        if not is_strong_password(password):
            flash('Password must be at least 8 characters long.', 'danger')
            return render_template('register.html', email=email)

        if User.query.filter_by(email=email).first():
            flash('Email already registered!', 'error')
            return redirect(url_for('register'))

        hashed_pw = generate_password_hash(password)
        new_user = User(email=email, password=hashed_pw)
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful. Please login.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')  
        password = request.form.get('password')

        if not email or not password:
            flash('Please fill out both email and password.', 'error')
            return redirect(url_for('login'))

        user = User.query.filter_by(email=email).first()

        if user is None:
            flash('Email not registered. Please register first.', 'error')
            return redirect(url_for('login'))

        if not check_password_hash(user.password, password):
            flash('Incorrect password. Please try again.', 'error')
            return redirect(url_for('login'))

        login_user(user)
        
        if 'guest_list' in session and session['guest_list']:
            for guest_anime in session['guest_list']:
                new_anime = Anime_list(
                    Anime_name=guest_anime['Anime_name'],
                    Anime_desc=guest_anime['Anime_desc'],
                    Watch=guest_anime['Watch'],
                    Watch_Status=guest_anime['Watch_Status'],
                    user_id=user.id
                )
                db.session.add(new_anime)
            db.session.commit()
            session.pop('guest_list', None) 

        return redirect(url_for('hello_world'))

    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/delete_account', methods=['POST'])
@login_required
def delete_account():
    user = User.query.get(current_user.id)
    Anime_list.query.filter_by(user_id=user.id).delete()
    db.session.delete(user)
    db.session.commit()
    logout_user()
    flash('Your account and watchlist have been deleted.', 'success')
    return redirect(url_for('hello_world'))


@app.route("/", methods=['GET', 'POST'])
def hello_world():
    if request.method == "POST":
        anime_name = request.form['Anime_name']
        anime_desc = request.form['Anime_desc']
        watch = request.form['Watch']
        watch_status = request.form['Watch_Status']

        if current_user.is_authenticated:
            anime = Anime_list(
                Anime_name=anime_name,
                Anime_desc=anime_desc,
                Watch=watch,
                Watch_Status=watch_status,
                user_id=current_user.id
            )
            db.session.add(anime)
            db.session.commit()
        else:
            if 'guest_list' not in session:
                session['guest_list'] = []
            
            guest_anime = {
                "Anime_name": anime_name,
                "Anime_desc": anime_desc,
                "Watch": watch,
                "Watch_Status": watch_status,
                "Date_created": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            session['guest_list'].append(guest_anime)
            session.modified = True

        return redirect(url_for('hello_world'))

    if current_user.is_authenticated:
        allAnime = Anime_list.query.filter_by(user_id=current_user.id).all()
    else:
        allAnime = session.get('guest_list', [])

    return render_template("index.html", allAnime=allAnime)


# Routes for logged-in users
@app.route("/update/<int:Sno>", methods=['GET', 'POST'])
@login_required
def update_db(Sno):
    anime = Anime_list.query.filter_by(Sno=Sno, user_id=current_user.id).first_or_404()
    if request.method == "POST":
        anime.Anime_name = request.form['Anime_name']
        anime.Anime_desc = request.form['Anime_desc']
        anime.Watch = request.form['Watch']
        anime.Watch_Status = request.form['Watch_Status']
        db.session.commit()
        return redirect(url_for('hello_world'))

    return render_template("update.html", anime=anime)

@app.route("/delete/<int:Sno>")
@login_required
def delete_db(Sno):
    anime = Anime_list.query.filter_by(Sno=Sno, user_id=current_user.id).first_or_404()
    db.session.delete(anime)
    db.session.commit()
    return redirect(url_for('hello_world'))


# Routes for guest users
@app.route("/guest_update/<int:index>", methods=['GET', 'POST'])
def update_guest(index):
    all_anime = session.get('guest_list', [])
    if 0 <= index < len(all_anime):
        anime_to_update = all_anime[index]

        if request.method == "POST":
            anime_to_update['Anime_name'] = request.form['Anime_name']
            anime_to_update['Anime_desc'] = request.form['Anime_desc']
            anime_to_update['Watch'] = request.form['Watch']
            anime_to_update['Watch_Status'] = request.form['Watch_Status']
            session.modified = True
            return redirect(url_for('hello_world'))
        
        return render_template("update.html", anime=anime_to_update, index=index)
    
    flash("Anime not found.", "error")
    return redirect(url_for('hello_world'))

@app.route("/guest_delete/<int:index>")
def delete_guest(index):
    all_anime = session.get('guest_list', [])
    if 0 <= index < len(all_anime):
        all_anime.pop(index)
        session.modified = True
    else:
        flash("Anime not found.", "error")
    
    return redirect(url_for('hello_world'))


@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query')
    if query:
        if current_user.is_authenticated:
            search_results = Anime_list.query.filter_by(user_id=current_user.id).filter(
                (Anime_list.Anime_name.ilike(f"%{query}%")) |
                (Anime_list.Anime_desc.ilike(f"%{query}%"))
            ).all()
        else:
            all_anime = session.get('guest_list', [])
            search_results = [
                anime for anime in all_anime 
                if query.lower() in anime['Anime_name'].lower() or 
                   query.lower() in anime['Anime_desc'].lower()
            ]
    else:
        if current_user.is_authenticated:
            search_results = Anime_list.query.filter_by(user_id=current_user.id).all()
        else:
            search_results = session.get('guest_list', [])

    return render_template("index.html", allAnime=search_results)

@app.route("/about")
def about():
    return render_template("about.html")

@app.route('/download')
@login_required
def download_watchlist():
    allAnime = Anime_list.query.filter_by(user_id=current_user.id).all()
    export_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    rendered_html = render_template('download.html', allAnime=allAnime, export_date=export_date)
    response = make_response(rendered_html)
    response.headers['Content-Type'] = 'text/html'
    response.headers['Content-Disposition'] = 'attachment; filename=anime_watchlist.html'
    return response

@app.route("/profile", methods=['GET', 'POST'])
@login_required
def profile():
    user_id = current_user.id  
    allAnime = Anime_list.query.filter_by(user_id=user_id).all()  

    return render_template('profile.html', allAnime=allAnime)


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)