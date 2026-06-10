from flask import Flask, render_template
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


@app.route("/")
def home():
    return render_template("login.html")


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