from flask import Flask, render_template,request,redirect,url_for
from flask_login import login_user
from extensions import db, login_manager
from models import User, Trek
import models

app = Flask(__name__)

app.config["SECRET_KEY"] = "trekking-secret-key"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///trekking.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

login_manager.init_app(app)
login_manager.login_view = "login"


@login_manager.user_loader
def user_loader(user_id):
    return User.query.get(int(user_id))


@app.route("/",methods = ["GET","POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(
            email=email
        ).first()
        if user and user.password == password:
            login_user(user)
            if user.role == "admin":
                return redirect(url_for("admin_dashboard"))
            elif user.role == "staff":
                return redirect(url_for("staff_dashboard"))
            else:
                return redirect(url_for("user_dashboard"))
        return "Invalid Credentials"
    return render_template("login.html")
@app.route("/admin")
def admin_dashboard():
    return "<h1>Admin Dashboard</h1>"

@app.route("/staff")
def staff_dashboard():
    return "<h1>Staff Dashboard</h1>"

@app.route("/user")
def user_dashboard():
    return "<h1>User Dashboard</h1>"

if __name__ == "__main__":

    with app.app_context():

        db.create_all()

        admin = User.query.filter_by(
            email="admin@musafir.com"
        ).first()

        if not admin:
            admin = User(
                name="Musafir Admin",
                email="admin@musafir.com",
                password="musafir123",
                role="admin"
            )

            db.session.add(admin)
            db.session.commit()

            print("Admin created successfully")

        staff = User.query.filter_by(
            email="staff@musafir.com"
        ).first()

        if not staff:
            staff = User(
                name="Rahul Kumar",
                email="staff@musafir.com",
                password="staff123",
                role="staff"
            )

            db.session.add(staff)
            db.session.commit()

            print("Staff created")

        trek = Trek.query.filter_by(
            name="Rajgad Trek"
        ).first()

        if not trek:
            trek = Trek(
                name="Rajgad Trek",
                location="Pune",
                difficulty="Moderate",
                duration=2,
                available_slots=25,
                staff_id=staff.id,
                status="Open"
            )

            db.session.add(trek)
            db.session.commit()

            print("Trek created")

    app.run(debug=True)