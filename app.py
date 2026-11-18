
from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import datetime, date
from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from functools import wraps
from flask import abort
from flask_login import (
    LoginManager,
    login_user,
    logout_user,
    login_required,
    current_user
)
from flask_wtf.csrf import CSRFProtect
from werkzeug.security import generate_password_hash, check_password_hash

from config import Config
from models import db, User, Product, Booking , Order

app = Flask(__name__)

# Load configuration
app.config.from_object(Config)

# Initialize database
db.init_app(app)

# Protect forms against CSRF attacks
csrf = CSRFProtect(app)

# Initialize login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
login_manager.login_message = "Please login to access this page."


# Find logged-in user
@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


# Admin Access Protection
def admin_required(view_function):

    @wraps(view_function)
    @login_required
    def decorated_function(*args, **kwargs):

        if not current_user.is_admin:
            abort(403)

        return view_function(*args, **kwargs)

    return decorated_function

# Home page
@app.route("/")
def home():
    return render_template("index.html")


# Signup page
@app.route("/signup", methods=["GET", "POST"])
def signup():

    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    if request.method == "POST":

        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        phone = request.form.get("phone", "").strip()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        if not all([name, email, phone, password, confirm_password]):
            flash("Please fill in all fields.", "danger")
            return redirect(url_for("signup"))

        if len(name) > 100 or len(email) > 120:
            flash("Name or email is too long.", "danger")
            return redirect(url_for("signup"))

        if "@" not in email or "." not in email.split("@")[-1]:
            flash("Please enter a valid email address.", "danger")
            return redirect(url_for("signup"))

        if len(phone) > 15:
            flash("Please enter a valid phone number.", "danger")
            return redirect(url_for("signup"))

        if len(password) < 8:
            flash("Password must contain at least 8 characters.", "danger")
            return redirect(url_for("signup"))

        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return redirect(url_for("signup"))

        existing_user = db.session.execute(
            db.select(User).filter_by(email=email)
        ).scalar_one_or_none()

        if existing_user:
            flash("This email is already registered.", "danger")
            return redirect(url_for("signup"))

        # Hash the password
        hashed_password = generate_password_hash(password)

        # Create customer
        new_user = User(
            name=name,
            email=email,
            phone=phone,
            password_hash=hashed_password
        )

        db.session.add(new_user)
        db.session.commit()

        flash("Account created successfully! Please login.", "success")

        return redirect(url_for("login"))

    return render_template("signup.html")


# Login page
@app.route("/login", methods=["GET", "POST"])
def login():

    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    if request.method == "POST":

        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        user = db.session.execute(
            db.select(User).filter_by(email=email)
        ).scalar_one_or_none()

        if user and check_password_hash(user.password_hash, password):

            login_user(user)

            flash("Welcome back!", "success")

            return redirect(url_for("dashboard"))

        flash("Invalid email or password.", "danger")

    return render_template("login.html")

    # About Our Business
@app.route("/about")
def about():

    return render_template("about.html")


# Customer dashboard
@app.route("/dashboard")
@login_required
def dashboard():

    return render_template("dashboard.html")


# Products page
@app.route("/products")
@login_required
def products():

    all_products = db.session.execute(
        db.select(Product).order_by(Product.created_at.desc())
    ).scalars().all()

    return render_template(
        "products.html",
        products=all_products
    )


# Services page
@app.route("/services")
@login_required
def services():

    return render_template("services.html")



# Book a Service
@app.route("/book-service", methods=["GET", "POST"])
@login_required
def book_service():

    if request.method == "POST":

        customer_name = request.form.get(
            "customer_name", ""
        ).strip()

        phone = request.form.get(
            "phone", ""
        ).strip()

        service_type = request.form.get(
            "service_type", ""
        ).strip()

        motor_type = request.form.get(
            "motor_type", ""
        ).strip()

        problem_description = request.form.get(
            "problem_description", ""
        ).strip()

        preferred_date = request.form.get(
            "preferred_date", ""
        ).strip()

        address = request.form.get(
            "address", ""
        ).strip()

        # Validate required fields
        if not all([
            customer_name,
            phone,
            service_type,
            motor_type,
            problem_description,
            preferred_date,
            address
        ]):
            flash("Please fill in all fields.", "danger")
            return redirect(url_for("book_service"))

        # Validate phone number
        if not phone.isdigit() or not 10 <= len(phone) <= 15:
            flash("Please enter a valid phone number.", "danger")
            return redirect(url_for("book_service"))

        # Validate date
        try:
            booking_date = datetime.strptime(
                preferred_date, "%Y-%m-%d"
            ).date()

            if booking_date < date.today():
                flash("Please select today or a future date.", "danger")
                return redirect(url_for("book_service"))

        except ValueError:
            flash("Please enter a valid date.", "danger")
            return redirect(url_for("book_service"))

        # Create booking
        new_booking = Booking(
            user_id=current_user.id,
            customer_name=customer_name,
            phone=phone,
            service_type=service_type,
            motor_type=motor_type,
            problem_description=problem_description,
            preferred_date=booking_date,
            address=address
        )

        db.session.add(new_booking)
        db.session.commit()

        flash("Your service booking has been submitted successfully!", "success")

        return redirect(url_for("dashboard"))

    return render_template(
    "book_service.html",
    today=date.today().isoformat()
)


# Logout
@app.route("/logout", methods=["POST"])
@login_required
def logout():

    logout_user()

    flash("You have logged out successfully.", "success")

    return redirect(url_for("home"))



@app.route('/buy-now/<int:product_id>')
@login_required
def buy_now(product_id):

    product = Product.query.get_or_404(product_id)

    if product.stock <= 0:
        flash('Sorry! This product is currently out of stock.', 'danger')
        return redirect(url_for('products'))

    return redirect(url_for('checkout', product_id=product.id))


@app.route('/checkout/<int:product_id>', methods=['GET', 'POST'])
@login_required
def checkout(product_id):

    product = Product.query.get_or_404(product_id)

    if product.stock <= 0:
        flash('Sorry! This product is currently out of stock.', 'danger')
        return redirect(url_for('products'))

    if request.method == 'POST':

        customer_name = request.form.get('customer_name', '').strip()
        phone = request.form.get('phone', '').strip()
        address = request.form.get('address', '').strip()

        try:
            quantity = int(request.form.get('quantity', 1))
        except (ValueError, TypeError):
            quantity = 0

        if not customer_name or not phone or not address:
            flash('Please fill in all customer details.', 'danger')

        elif len(phone) < 10:
            flash('Please enter a valid phone number.', 'danger')

        elif quantity <= 0:
            flash('Please select a valid quantity.', 'danger')

        elif quantity > product.stock:
            flash('Requested quantity is not available.', 'danger')

        else:

            total_amount = product.price * quantity

            order = Order(
                user_id=current_user.id,
                product_id=product.id,
                customer_name=customer_name,
                phone=phone,
                address=address,
                quantity=quantity,
                total_amount=total_amount,
                status='Pending'
            )

            product.stock -= quantity

            db.session.add(order)
            db.session.commit()

            flash('Your order has been placed successfully!', 'success')

            return redirect(url_for('order_success', order_id=order.id))

    return render_template('checkout.html', product=product)


@app.route('/order-success/<int:order_id>')
@login_required
def order_success(order_id):

    order = Order.query.filter_by(
        id=order_id,
        user_id=current_user.id
    ).first_or_404()

    return render_template('order_success.html', order=order)


@app.route('/admin/orders')
@admin_required
def admin_orders():

    orders = (
        db.session.query(Order, Product)
        .join(Product, Order.product_id == Product.id)
        .order_by(Order.created_at.desc())
        .all()
    )

    total_orders = Order.query.count()

    pending_orders = Order.query.filter_by(
        status='Pending'
    ).count()

    confirmed_orders = Order.query.filter_by(
        status='Confirmed'
    ).count()

    delivered_orders = Order.query.filter_by(
        status='Delivered'
    ).count()

    return render_template(
        'admin_orders.html',
        orders=orders,
        total_orders=total_orders,
        pending_orders=pending_orders,
        confirmed_orders=confirmed_orders,
        delivered_orders=delivered_orders
    )


@app.route('/admin/orders/<int:order_id>/status', methods=['POST'])
@admin_required
def update_order_status(order_id):

    order = Order.query.get_or_404(order_id)

    new_status = request.form.get('status')

    allowed_statuses = [
        'Pending',
        'Confirmed',
        'Shipped',
        'Delivered',
        'Cancelled'
    ]

    if new_status not in allowed_statuses:

        flash('Invalid order status.', 'danger')

        return redirect(url_for('admin_orders'))

    order.status = new_status

    db.session.commit()

    flash(
        f'Order #{order.id} status updated to {new_status}.',
        'success'
    )

    return redirect(url_for('admin_orders'))



# Create database tables
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
