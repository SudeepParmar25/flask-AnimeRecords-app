from flask import Flask, render_template, request, redirect,url_for, make_response
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///anime.db"
db = SQLAlchemy(app)


class Anime_list(db.Model):
    Sno = db.Column(db.Integer, primary_key = True)
    Anime_name = db.Column(db.String(200), nullable = False)
    Anime_desc = db.Column(db.String(500), nullable = False)
    Date_created = db.Column(db.DateTime, default= datetime.utcnow )
    Watch = db.Column(db.String(100))
    Watch_Status = db.Column(db.String(50), nullable=True) 

    def __repr__(self):
        return f"{self.Anime_name} - {self.Anime_desc}"

@app.route("/", methods=['GET', 'POST'])
def hello_world():
    if request.method=="POST":
        Anime_name = request.form['Anime_name']
        Anime_desc = request.form['Anime_desc']
        Watch = request.form['Watch']
        Watch_Status = request.form['Watch_Status']
        Anime1 = Anime_list(Anime_name = Anime_name, Anime_desc = Anime_desc,Watch = Watch,Watch_Status = Watch_Status)
        db.session.add(Anime1)
        db.session.commit()
        return redirect(url_for('hello_world'))

    allAnime = Anime_list.query.all()
    return render_template("index.html", allAnime = allAnime)

@app.route("/update/<int:Sno>", methods=['GET', 'POST'])
def update(Sno):
    if request.method=="POST":
        Anime_name = request.form['Anime_name']
        Anime_desc = request.form['Anime_desc']
        Watch = request.form['Watch']
        Watch_Status = request.form['Watch_Status']
        anime = Anime_list.query.filter_by(Sno=Sno).first()
        anime.Anime_name = Anime_name
        anime.Anime_desc = Anime_desc
        anime.Watch = Watch
        anime.Watch_Status = Watch_Status
        db.session.add(anime)
        db.session.commit()
        return redirect("/")

    anime = Anime_list.query.filter_by(Sno=Sno).first()
    return render_template("update.html", anime = anime)
    

@app.route("/delete/<int:Sno>")
def delete(Sno):
    anime = Anime_list.query.filter_by(Sno=Sno).first()
    db.session.delete(anime)
    db.session.commit()
    return redirect('/')

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query')  # Get the search term from the query string
    if query:
        # Query the database to search for anime where name or description contains the search query
        search_results = Anime_list.query.filter(
            (Anime_list.Anime_name.ilike(f"%{query}%")) | 
            (Anime_list.Anime_desc.ilike(f"%{query}%"))
        ).all()
    else:
        search_results = []  # No query entered, so return an empty list

    return render_template("index.html", allAnime=search_results) 

@app.route("/about")
def about():
    return render_template("about.html")

@app.route('/download')
def download_watchlist():
    allAnime = Anime_list.query.all()
    export_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    rendered_html = render_template('download.html', allAnime=allAnime, export_date=export_date)
    response = make_response(rendered_html)
    response.headers['Content-Type'] = 'text/html'
    response.headers['Content-Disposition'] = 'attachment; filename=anime_watchlist.html'
    return response

if __name__=="__main__":
    app.run(debug=True)