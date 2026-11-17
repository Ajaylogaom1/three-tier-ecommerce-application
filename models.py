
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()


class User(UserMixin, db.Model):

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100), nullable=False)

    email = db.Column(db.String(120), unique=True, nullable=False)

    phone = db.Column(db.String(15), nullable=False)

    password_hash = db.Column(db.String(255), nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    is_admin = db.Column(
    db.Boolean,
    default=False,
    nullable=False
)


# Products table
class Product(db.Model):

    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(
        db.String(150),
        nullable=False
    )

    category = db.Column(
        db.String(100),
        nullable=False
    )

    description = db.Column(
        db.Text,
        nullable=False
    )

    price = db.Column(
        db.Numeric(10, 2),
        nullable=False
    )

    stock = db.Column(
        db.Integer,
        default=0,
        nullable=False
    )

    image_filename = db.Column(
        db.String(255),
        nullable=True
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )


# Service Bookings table
class Booking(db.Model):

    __tablename__ = "bookings"

    id = db.Column(db.Integer, primary_key=True)

    # Link booking to registered customer
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    customer_name = db.Column(
        db.String(100),
        nullable=False
    )

    phone = db.Column(
        db.String(15),
        nullable=False
    )

    service_type = db.Column(
        db.String(100),
        nullable=False
    )

    motor_type = db.Column(
        db.String(100),
        nullable=False
    )

    problem_description = db.Column(
        db.Text,
        nullable=False
    )

    preferred_date = db.Column(
        db.Date,
        nullable=False
    )

    address = db.Column(
        db.Text,
        nullable=False
    )

    status = db.Column(
        db.String(30),
        default="Pending",
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

class Order(db.Model):
    __tablename__ = "orders"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    product_id = db.Column(
        db.Integer,
        db.ForeignKey("products.id"),
        nullable=False
    )

    customer_name = db.Column(db.String(150), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    address = db.Column(db.Text, nullable=False)

    quantity = db.Column(db.Integer, nullable=False)
    total_amount = db.Column(db.Numeric(10, 2), nullable=False)

    status = db.Column(
        db.String(30),
        default="Pending",
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.current_timestamp()
    )
