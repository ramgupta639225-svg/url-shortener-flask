from flask import Flask, request, jsonify, redirect, render_template
from config import Config
from models import db, Url
import string
import secrets


app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

with app.app_context():
    db.create_all()



@app.route('/', methods=['GET', 'POST'])
def home():
    short_url = None
    error = None
    if request.method == 'POST':
        original_url = request.form.get("url")
        if not original_url:
            error = "URL is required"
        else:
            characters = string.ascii_letters + string.digits
            while True:
                short_code = ''.join(secrets.choice(characters) for _ in range(10))
                existing_url = Url.query.filter_by(short_code=short_code).first()
                if not existing_url:
                    break
            new_url = Url(original_url=original_url, short_code=short_code)
            db.session.add(new_url)
            db.session.commit()
            short_url = f"http://127.0.0.1:5000/{short_code}"
    return render_template("index.html", short_url=short_url, error=error)



@app.route('/shorten', methods=['POST'])
def shorten_url():
    data = request.get_json()
    if not data:
        return jsonify({"error": "JSON data is required"}), 400
    original_url = data.get("url")
    if not original_url:
        return jsonify({"error": "URL is required"}), 400
    characters = string.ascii_letters + string.digits

    while True:
        short_code = ''.join(secrets.choice(characters) for _ in range(10))
        existing_url = Url.query.filter_by(short_code=short_code).first()
        if not existing_url:
            break
    new_url = Url(original_url=original_url, short_code=short_code)
    db.session.add(new_url)
    db.session.commit()
    return jsonify({
        "message": "URL shortened successfully",
        "short_code": short_code,
        "short_url": f"http://127.0.0.1:5000/{short_code}"
    }), 201



@app.route('/<short_code>')
def redirect_url(short_code):
    url = Url.query.filter_by(short_code=short_code).first()
    if not url:
        return "Short URL not found", 404
    url.clicks += 1
    db.session.commit()
    return redirect(url.original_url)



if __name__ == '__main__':
    app.run(debug=True)

