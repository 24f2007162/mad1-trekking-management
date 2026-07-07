from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import login_user, login_required, current_user, logout_user
from extensions import db, login_manager
from models import User, Trek, Booking
import models
from werkzeug.security import generate_password_hash, check_password_hash
import requests
from config import WEATHER_API_KEY

app = Flask(__name__)

app.config["SECRET_KEY"] = "trekking-secret-key"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///trekking.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

login_manager.init_app(app)
login_manager.login_view = "login"


@login_manager.user_loader
def user_loader(user_id):
    return db.session.get(User, int(user_id))


LOCATION_MAP = {
    "Uttarakhand": "Joshimath",
    "Kashmir": "Srinagar",
    "Himachal Pradesh": "Manali",
    "Maharashtra": "Pune",
    "Karnataka": "Chikmagalur",
    "Ladakh": "Leh",
}


TREK_INFO = {
    "Uttarakhand": {
        "places": [
            "Valley of Flowers National Park",
            "Badrinath Temple",
            "Hemkund Sahib",
            "Joshimath",
            "Auli",
        ],
        "food": ["Kafuli", "Aloo Ke Gutke", "Bal Mithai", "Chainsoo", "Jhangora Kheer"],
    },
    "Pune": {
        "places": [
            "Sinhagad Fort",
            "Shaniwar Wada",
            "Lonavala",
            "Lavasa",
            "Khadakwasla Dam",
        ],
        "food": [
            "Misal Pav",
            "Vada Pav",
            "Bhakarwadi",
            "Puran Poli",
            "Sabudana Khichdi",
        ],
    },
    "Kashmir": {
        "places": ["Dal Lake", "Gulmarg", "Sonmarg", "Pahalgam", "Betaab Valley"],
        "food": ["Rogan Josh", "Gushtaba", "Yakhni", "Kahwa", "Dum Aloo"],
    },
    "West Bengal": {
        "places": [
            "Tiger Hill",
            "Batasia Loop",
            "Darjeeling Mall Road",
            "Peace Pagoda",
        ],
        "food": ["Momos", "Thukpa", "Darjeeling Tea", "Rosogolla", "Sandesh"],
    },
    "Himachal Pradesh": {
        "places": [
            "McLeod Ganj",
            "Bhagsu Waterfall",
            "Dalai Lama Temple",
            "Triund Ridge",
        ],
        "food": ["Siddu", "Madra", "Babru", "Dham", "Chha Gosht"],
    },
    "Karnataka": {
        "places": ["Jog Falls", "Agumbe", "Kodachadri Peak", "Kudremukh"],
        "food": [
            "Bisi Bele Bath",
            "Mysore Pak",
            "Neer Dosa",
            "Ragi Mudde",
            "Mangalore Buns",
        ],
    },
}


def get_weather(location):
    try:
        location = LOCATION_MAP.get(location, location)

        url = (
            f"https://api.openweathermap.org/data/2.5/weather"
            f"?q={location}&appid={WEATHER_API_KEY}&units=metric"
        )

        response = requests.get(url)
        data = response.json()

        if response.status_code == 200:
            return {
                "temp": data["main"]["temp"],
                "condition": data["weather"][0]["description"],
                "icon": "https://openweathermap.org/img/wn/"
                + data["weather"][0]["icon"]
                + ".png",
                "humidity": data["main"]["humidity"],
                "wind": data["wind"]["speed"],
            }

    except Exception as e:
        print("Weather error:", e)

    return None


def weather_insight(condition):
    condition = condition.lower()

    if "rain" in condition:
        return "🌧 Rain expected — avoid risky trails"
    elif "cloud" in condition:
        return "☁ Mostly cloudy — good trekking conditions"
    elif "clear" in condition:
        return "🌤 Perfect visibility for trekking"
    elif "snow" in condition:
        return "❄ Snow conditions — high difficulty"
    else:
        return "⛰ Normal mountain conditions"


@app.route("/", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()

        if not user:
            flash("Invalid email or password.", "danger")
            return redirect(url_for("login"))

        if user.status == "inactive":
            flash(
                "Your account has been deactivated. Please contact the administrator.",
                "warning",
            )
            return redirect(url_for("login"))

        if check_password_hash(user.password, password):

            login_user(user)

            if user.role == "admin":
                return redirect(url_for("admin_dashboard"))

            elif user.role == "staff":
                return redirect(url_for("staff_dashboard"))

            else:
                return redirect(url_for("user_dashboard"))

        flash("Invalid email or password.", "danger")
        return redirect(url_for("login"))

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
        chart_labels.append(trek.name)
        chart_values.append(len(trek.bookings))

    return render_template(
        "admin_dashboard.html",
        total_users=total_users,
        total_staff=total_staff,
        total_treks=total_treks,
        total_bookings=total_bookings,
        chart_labels=chart_labels,
        chart_values=chart_values,
    )


# ======================================================
# Staff Routes
# ======================================================


@app.route("/staff")
@login_required
def staff_dashboard():
    if current_user.role != "staff":
        return "Access Denied!"
    treks = Trek.query.filter_by(staff_id=current_user.id).all()

    labels = []
    values = []
    for trek in treks:
        booked = len(trek.bookings)

        total = booked + trek.available_slots
        if total > 0:
            occupancy = round((booked / total) * 100)
        else:
            occupancy = 0

        labels.append(trek.name)
        values.append(occupancy)

    return render_template(
        "staff_dashboard.html", treks=treks, chart_labels=labels, chart_values=values
    )


@app.route("/staff/treks/<int:id>")
@login_required
def view_participants(id):
    if current_user.role != "staff":
        return "Access Denied!"

    trek = Trek.query.get_or_404(id)
    if trek.staff_id != current_user.id:
        return "Not Authorized"
    bookings = Booking.query.filter_by(trek_id=id).all()

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


# ======================================================
# User Routes
# ======================================================


@app.route("/user")
@login_required
def user_dashboard():
    if current_user.role != "user":
        return "Access Denied!"
    treks = Trek.query.filter(Trek.status == "Open", Trek.available_slots > 0).all()
    bookings = Booking.query.filter_by(user_id=current_user.id).all()

    staff_count = User.query.filter_by(role="staff").count()

    locations = db.session.query(Trek.location).distinct().count()

    next_booking = (
        Booking.query.filter_by(user_id=current_user.id)
        .order_by(Booking.booking_date.asc())
        .first()
    )
    return render_template(
        "user_dashboard.html",
        treks=treks,
        bookings=bookings,
        staff_count=staff_count,
        locations=locations,
        next_booking=next_booking,
    )


@app.route("/book/<int:id>")
@login_required
def book_trek(id):

    if current_user.role != "user":
        return "Users Only!"

    trek = Trek.query.get_or_404(id)

    existing_booking = Booking.query.filter_by(
        user_id=current_user.id, trek_id=id
    ).first()

    if existing_booking:
        flash("You have already booked this trek.", "warning")
        return redirect(url_for("trek_details", id=id))

    if trek.available_slots <= 0:
        flash("No slots available for this trek.", "danger")
        return redirect(url_for("trek_details", id=id))

    booking = Booking(user_id=current_user.id, trek_id=id)

    trek.available_slots -= 1

    db.session.add(booking)
    db.session.commit()

    flash("Trek booked successfully!", "success")

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

    flash("Booking cancelled successfully.", "success")

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

        if not name or not email:
            flash("Please fill in all required fields.", "warning")
            return redirect(url_for("register"))

        if not password or len(password) < 8:
            flash("Password must be at least 8 characters.", "warning")
            return redirect(url_for("register"))

        if password.isalpha():
            flash("Password must contain at least one number.", "warning")
            return redirect(url_for("register"))

        existing_user = User.query.filter_by(email=email).first()

        if existing_user:
            flash("An account with this email already exists.", "warning")
            return redirect(url_for("register"))

        hashed_password = generate_password_hash(password)

        user = User(
            name=name,
            email=email,
            password=hashed_password,
            role="user",
        )

        db.session.add(user)
        db.session.commit()

        flash("Registration successful! Please login.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():

    if request.method == "POST":

        email = request.form.get("email")

        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()

        if not user:

            flash("No account found with this email.", "danger")
            return redirect(url_for("forgot_password"))
        user.password = generate_password_hash(password)

        db.session.commit()

        flash("Password updated successfully.", "success")
        return redirect(url_for("login"))

    return render_template("forgot_password.html")


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
            flash("A staff account with this email already exists.", "warning")
            return redirect(url_for("create_staff"))
        
        if not name or not email or not password:
         flash("Please fill in all required fields.", "warning")
         return redirect(url_for("create_staff"))

        hashed_password = generate_password_hash(password)

        staff = User(name=name, email=email, password=hashed_password, role="staff")

        db.session.add(staff)
        db.session.commit()

        flash("Staff account created successfully.", "success")

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
    flash("Staff status updated successfully.", "success")

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
        flash("New trek created successfully.", "success")

        return redirect(url_for("view_treks"))
    return render_template("create_trek.html", staff=staff)


@app.route("/admin/treks/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit_trek(id):

    if current_user.role != "admin":
        return "Access Denied"

    trek = Trek.query.get_or_404(id)

    if request.method == "POST":

        

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
        flash("Trek updated successfully.", "success")

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
    flash("Trek deleted successfully.", "success")
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

    # Weather
    weather = get_weather(trek.location)

    weather_tip = None
    if weather:
        weather_tip = weather_insight(weather["condition"])

    # Tourist attractions & local food
    attractions = []
    foods = []

    for state, info in TREK_INFO.items():

        if state.lower() in trek.location.lower():
            attractions = info["places"]
            foods = info["food"]
            break

    return render_template(
        "trek_details.html",
        trek=trek,
        weather=weather,
        weather_tip=weather_tip,
        attractions=attractions,
        foods=foods,
    )


@app.route("/recommend", methods=["GET", "POST"])
@login_required
def recommend():

    if current_user.role != "user":
        return "Access Denied!"

    recommendations = []
    reason = ""
    places = []
    foods = []

    if request.method == "POST":

        difficulty = request.form.get("difficulty").strip().lower()

        location = request.form.get("location").strip().lower()

        previous_bookings = Booking.query.filter_by(user_id=current_user.id).all()

        booked_ids = []

        for booking in previous_bookings:

            booked_ids.append(booking.trek_id)

        treks = Trek.query.all()

        for trek in treks:

            # Skip booked treks
            if trek.id in booked_ids:
                continue

            # Match difficulty
            if trek.difficulty.strip().lower() != difficulty:
                continue

            # Match location
            if location not in trek.location.strip().lower():
                continue

            # Must be available
            if trek.status == "Open" and trek.available_slots > 0:

                recommendations.append(trek)

        if recommendations:

            reason = "Showing all matching treks"
            # Tourist attractions for the first recommended trek
            top_trek = recommendations[0]

            for key in TREK_INFO:

                if key.lower() in top_trek.location.lower():

                    
                    places = TREK_INFO[key]["places"]
                    foods = TREK_INFO[key]["food"]

                    break

        else:

            reason = "No matching treks found"

    return render_template(
        "recommend.html",
        recommendations=recommendations,
        reason=reason,
        places=places,
        foods=foods,
    )


if __name__ == "__main__":

    with app.app_context():

        db.create_all()

        admin = User.query.filter_by(email="admin@musafir.com").first()

        if not admin:
            admin = User(
                name="Musafir Admin",
                email="admin@musafir.com",
                password=generate_password_hash("musafir123"),
                role="admin",
            )

            db.session.add(admin)
            db.session.commit()

        staff = User.query.filter_by(email="staff@musafir.com").first()

        if not staff:
            staff = User(
                name="Rahul Kumar",
                email="staff@musafir.com",
                password=generate_password_hash("staff123"),
                role="staff",
            )

            db.session.add(staff)
            db.session.commit()

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

    app.run()