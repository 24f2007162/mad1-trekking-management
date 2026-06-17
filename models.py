from extensions import db
from datetime import datetime,UTC
from flask_login import UserMixin

class User(UserMixin,db.Model):
  __tablename__ = "users"
  id = db.Column(db.Integer, primary_key = True)
  name = db.Column(db.String(100),nullable =  False)
  email = db.Column(db.String(120), unique = True,nullable = False)
  password = db.Column(db.String(255),nullable = False)
  role = db.Column(db.String(20),nullable = False)
  status = db.Column(db.String(20),default = "active")
  staff_profile = db.relationship("StaffProfile",backref = "user",uselist =  False)
  bookings = db.relationship("Booking",backref = "user",lazy = True)

class Trek(db.Model):
  __tablename__ = "treks"
  id = db.Column(db.Integer,primary_key = True)
  name = db.Column(db.String(120),nullable =  False)
  location = db.Column(db.String(100),nullable = False)
  difficulty = db.Column(db.String(20),nullable = False)
  duration = db.Column(db.Integer,nullable =  False)
  available_slots = db.Column(db.Integer,nullable = False)
  staff_id = db.Column(db.Integer,db.ForeignKey("users.id"))
  staff = db.relationship("User",backref = "assigned_treks")
  status = db.Column(db.String(20),nullable = False)
  start_date = db.Column(db.Date)
  end_date = db.Column(db.Date)
  bookings = db.relationship("Booking",backref = "trek",lazy = True)
  description = db.Column(db.Text)
  image = db.Column(db.String(255),default = "default-trek.jpg")
  created_at = db.Column(db.DateTime, default = lambda: datetime.now(UTC))
    

class Booking(db.Model):
  __tablename__ = "bookings"
  id = db.Column(db.Integer,primary_key = True)
  user_id = db.Column(db.Integer,db.ForeignKey("users.id"),nullable = False)
  trek_id = db.Column(db.Integer,db.ForeignKey("treks.id"),nullable = False)
  booking_date = db.Column(db.DateTime, default = lambda: datetime.now(UTC))
  status = db.Column(db.String(20),default = "Booked")
  payment_status = db.Column(db.String(20),default = "Pending")

class StaffProfile(db.Model):
  __tablename__ = "staff_profiles"
  id = db.Column(db.Integer,primary_key = True)
  user_id = db.Column(db.Integer,db.ForeignKey("users.id"),unique = True,nullable = False)
  contact_number =db.Column(db.String(15))
  experience_years = db.Column(db.Integer,default = 0)  
  bio = db.Column(db.Text)
  approval_status = db.Column(db.String(20),default = "pending")

