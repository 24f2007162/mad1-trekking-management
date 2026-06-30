from flask import Flask, render_template, request, redirect, url_for
from flask_login import login_user, login_required, current_user, logout_user
from extensions import db, login_manager
from models import User, Trek, Booking
import models
from werkzeug.security import generate_password_hash, check_password_hash

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


@app.route("/", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()

        if not user:
            return "Invalid Credentials"

        if user.status == "inactive":
            return "Account Disabled"

        if check_password_hash(user.password, password):

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
@login_required
def admin_dashboard():
    if current_user.role != "admin":
        return "Access Denied!"

    total_users = User.query.filter_by(role="user").count()

    total_staff = User.query.filter_by(role="staff").count()

    total_treks = Trek.query.count()
    total_bookings = Booking.query.count()

    treks = Trek.query.all()
    chart_labels = []
    chart_values = []
    for trek in treks:
        chart_labels.append(
            trek.name
        )
        chart_values.append(
            len(trek.bookings)
        )

    return render_template(
        "admin_dashboard.html",
        total_users=total_users,
        total_staff=total_staff,
        total_treks=total_treks,
        total_bookings=total_bookings,
        chart_labels = chart_labels,
        chart_values = chart_values
    )


@app.route("/staff")
@login_required
def staff_dashboard():
    if current_user.role != "staff":
        return "Access Denied!"
    treks = Trek.query.filter_by(staff_id=current_user.id).all()

    return render_template("staff_dashboard.html", treks=treks)


@app.route("/staff/treks/<int:id>")
@login_required
def view_participants(id):
    if current_user.role != "staff":
        return "Access Denied!"

    trek = Trek.query.get_or_404(id)
    if trek.staff_id != current_user.id:
        return "Not Authorized"
    bookings = Booking.query.filter_by(trek_id=id).all()

    print("BOOKED", bookings)

    return render_template("staff_participants.html", trek=trek, bookings=bookings)


@app.route("/staff/request/<int:id>")
@login_required
def request_assignment(id):
    if current_user.role != "staff":
        return "Access Denied!"

    trek = Trek.query.get_or_404(id)
    if trek.staff_id != current_user.id:
        return "Not Authorized"
    trek.status = "Guide Change Requested"

    db.session.commit()
    return redirect(url_for("staff_dashboard"))


@app.route("/staff/trek/start/<int:id>")
@login_required
def start_trek(id):
    if current_user.role != "staff":
        return "Access Denied!"
    trek = Trek.query.get_or_404(id)

    if trek.staff_id != current_user.id:
        return "Not Authorized"
    trek.status = "Ongoing"

    db.session.commit()
    return redirect(url_for("staff_dashboard"))


@app.route("/staff/trek/complete/<int:id>")
@login_required
def complete_trek(id):
    if current_user.role != "staff":
        return "Access Denied!"
    trek = Trek.query.get_or_404(id)
    if trek.staff_id != current_user.id:
        return "Not Authorized"
    trek.status = "Completed"

    db.session.commit()
    return redirect(url_for("staff_dashboard"))


@app.route("/user")
@login_required
def user_dashboard():
    if current_user.role != "user":
        return "Access Denied!"
    treks = Trek.query.filter(Trek.status == "Open", Trek.available_slots > 0).all()
    return render_template("user_dashboard.html", treks=treks)


@app.route("/book/<int:id>")
@login_required
def book_trek(id):
    if current_user.role != "user":
        return "Users Only!"
    trek = Trek.query.get_or_404(id)

    existing_booking = Booking.query.filter_by(
        user_id=current_user.id, trek_id=trek.id
    ).first()

    if existing_booking:
        return "Already Booked"

    if trek.available_slots <= 0:
        return "No slots Available"
    booking = Booking(user_id=current_user.id, trek_id=trek.id)
    trek.available_slots -= 1
    db.session.add(booking)
    db.session.commit()
    return redirect(url_for("user_dashboard"))


@app.route("/my-bookings")
@login_required
def my_bookings():
    if current_user.role != "user":
        return "Access Denied!"
    bookings = Booking.query.filter_by(user_id=current_user.id).all()
    return render_template("my_bookings.html", bookings=bookings)


@app.route("/cancel-booking/<int:id>")
@login_required
def cancel_booking(id):
    if current_user.role != "user":
        return "Access Denied!"
    booking = Booking.query.get_or_404(id)

    if booking.user_id != current_user.id:
        return "Unauthorized"
    trek = booking.trek
    trek.available_slots += 1
    db.session.delete(booking)
    db.session.commit()

    return redirect(url_for("my_bookings"))


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        if len(password) < 8:
            return "Password must be at least 8 characters"

        if password.isalpha():
            return "Password should include numbers"

        existing_user = User.query.filter_by(email=email).first()

        if existing_user:
            return "User Already Exists"

        hashed_password = generate_password_hash(password)

        user = User(name=name, email=email, password=password, role="user")
        db.session.add(user)
        db.session.commit()

        return redirect(url_for("login"))
    return render_template("register.html")


@app.route("/admin/staff/create", methods=["GET", "POST"])
@login_required
def create_staff():
    if current_user.role != "admin":
        return "Access Denied!"
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")

        existing = User.query.filter_by(email=email).first()
        if existing:
            return "Staff Already Exists"
        staff = User(name=name, email=email, password=password, role="staff")
        db.session.add(staff)
        db.session.commit()

        return redirect(url_for("view_users"))
    return render_template("create_staff.html")


@app.route("/admin/users")
@login_required
def view_users():

    if current_user.role != "admin":
        return "Access Denied"
    users = User.query.all()
    return render_template("admin_users.html", users=users)


@app.route("/admin/staff")
@login_required
def view_staff():
    if current_user.role != "admin":
        return "Access Denied!"
    search = request.args.get("search")
    if search:
        staff = User.query.filter(
            User.role == "staff", User.name.contains(search)
        ).all()
    else:
        staff = User.query.filter_by(role="staff").all()

    return render_template("admin_staff.html", staff=staff)


@app.route("/admin/staff/toggle/<int:id>")
@login_required
def toggle_staff(id):

    if current_user.role != "admin":
        return "Access Denied"

    staff = User.query.get_or_404(id)

    if staff.status.lower() == "active":
        staff.status = "inactive"

    else:
        staff.status = "active"

    db.session.commit()

    return redirect(url_for("view_staff"))


@app.route("/admin/treks", methods=["GET", "POST"])
@login_required
def view_treks():
    if current_user.role != "admin":
        return "Access Denied!"
    search = request.args.get("search")
    if search:
        treks = Trek.query.filter(Trek.name.contains(search)).all()
    else:
        treks = Trek.query.all()
    return render_template("admin_treks.html", treks=treks)


@app.route("/admin/treks/create", methods=["GET", "POST"])
@login_required
def create_trek():
    if current_user.role != "admin":
        return "Access Denied!"
    staff = User.query.filter_by(role="staff").all()
    print("STAFF FOUND", staff)
    if request.method == "POST":
        name = request.form.get("name")
        location = request.form.get("location")
        difficulty = request.form.get("difficulty")
        duration = request.form.get("duration")
        slots = request.form.get("slots")
        staff_id = request.form.get("staff_id")

        trek = Trek(
            name=name,
            location=location,
            difficulty=difficulty,
            duration=int(duration),
            available_slots=int(slots),
            staff_id=int(staff_id),
            status="Open",
            image=request.form.get("image"),
        )
        db.session.add(trek)
        db.session.commit()

        return redirect(url_for("view_treks"))
    return render_template("create_trek.html", staff=staff)


@app.route("/admin/treks/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit_trek(id):

    if current_user.role != "admin":
        return "Access Denied"

    trek = Trek.query.get_or_404(id)

    if request.method == "POST":

        print(request.form)

        trek.name = request.form.get("name")
        trek.location = request.form.get("location")
        trek.difficulty = request.form.get("difficulty")
        trek.duration = int(request.form.get("duration"))
        trek.available_slots = int(request.form.get("slots"))
        selected_staff = request.form.get("staff_id")
        trek.image = request.form.get("image")

        old_staff = trek.staff_id

        if selected_staff:
            trek.staff_id = int(selected_staff)
            if old_staff != trek.staff_id and trek.status == "Guide Change Requested":
                trek.status = "Open"
        else:
            trek.staff_id = None

        db.session.commit()

        return redirect(url_for("view_treks"))

    staff = User.query.filter_by(role="staff").all()

    return render_template("edit_trek.html", trek=trek, staff=staff)


@app.route("/admin/treks/delete/<int:id>")
@login_required
def delete_trek(id):
    if current_user.role != "admin":
        return "Access Denied!"
    trek = Trek.query.get_or_404(id)

    db.session.delete(trek)
    db.session.commit()

    return redirect(url_for("view_treks"))


@app.route("/about")
@login_required
def about_site():
    return render_template("about.html")


@app.route("/trek/<int:id>")
@login_required
def trek_details(id):
    if current_user.role != "user":
        return "Access Denied!"
    trek = Trek.query.get_or_404(id)
    return render_template("trek_details.html", trek=trek)


if __name__ == "__main__":

    with app.app_context():

        db.create_all()

        admin = User.query.filter_by(email="admin@musafir.com").first()

        if not admin:
            admin = User(
                name="Musafir Admin",
                email="admin@musafir.com",
                password="musafir123",
                role="admin",
            )

            db.session.add(admin)
            db.session.commit()

            print("Admin created successfully")

        staff = User.query.filter_by(email="staff@musafir.com").first()

        if not staff:
            staff = User(
                name="Rahul Kumar",
                email="staff@musafir.com",
                password="staff123",
                role="staff",
            )

            db.session.add(staff)
            db.session.commit()

            print("Staff created")

        trek = Trek.query.filter_by(name="Rajgad Trek").first()

        if not trek:
            trek = Trek(
                name="Rajgad Trek",
                location="Pune",
                difficulty="Moderate",
                duration=2,
                available_slots=25,
                staff_id=staff.id,
                status="Open",
            )

            db.session.add(trek)
            db.session.commit()

            print("Trek created")

    app.run(debug=True)
