from flask import Flask, render_template, request, redirect, url_for
from flask_login import login_user, login_required, current_user, logout_user
from extensions import db, login_manager
from models import User, Trek, Booking
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


@app.route("/", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(
            email=email
        ).first()

        if not user:
            return "Invalid Credentials"

        if user.status == "inactive":
            return "Account Disabled"

        if user.password == password:

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
    return """
    <h1>Admin DashBoard</h1>
    <a href = "/admin/users">View Users</a>
    <br><br>
    <a href = "/admin/treks">View Treks</a>
    <br><br>
    <a href = "/admin/treks/create"> Create Treks </a>
    <br><br>
    <a href = "/admin/staff/create">Add Staff</a>
    <br><br>
    <a href = "/admin/staff">View Staff</a>
    """


@app.route("/staff")
@login_required
def staff_dashboard():
    if current_user.role != "staff":
        return "Access Denied!"
    return "<h1>Staff Dashboard</h1>"


@app.route("/user")
@login_required
def user_dashboard():
    if current_user.role != "user":
        return "Access Denied!"
    return "<h1>User Dashboard</h1>"


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

        existing_user = User.query.filter_by(email=email).first()

        if existing_user:
            return "User Already Exists"

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
        if selected_staff:
            trek.staff_id = int(selected_staff)
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
