import datetime
import uuid
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    phone = db.Column(db.String(50), nullable=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    
    orders = db.relationship('Order', backref='user', lazy=True)
    addresses = db.relationship('Address', backref='user', cascade='all, delete-orphan', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Address(db.Model):
    __tablename__ = 'addresses'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(150), nullable=False)
    phone = db.Column(db.String(50), nullable=False)
    pincode = db.Column(db.String(20), nullable=False)
    address_line1 = db.Column(db.String(255), nullable=False)
    address_line2 = db.Column(db.String(255), nullable=True)
    city = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(100), nullable=False)
    address_type = db.Column(db.String(20), default='HOME')  # HOME, WORK
    is_default = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)


class AdminUser(db.Model):
    __tablename__ = 'admin_users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), default='Print Lab Admin')
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Product(db.Model):
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    slug = db.Column(db.String(255), unique=True, nullable=False)
    category = db.Column(db.String(100), nullable=False, default='Photo Frames')
    price = db.Column(db.Float, nullable=False)
    original_price = db.Column(db.Float, nullable=False)
    discount_percent = db.Column(db.Integer, default=0)
    rating = db.Column(db.Float, default=4.5)
    rating_count = db.Column(db.Integer, default=120)
    description = db.Column(db.Text, nullable=True)
    image_url = db.Column(db.String(500), nullable=False)
    badge = db.Column(db.String(100), nullable=True, default=None)
    dimensions = db.Column(db.String(255), default='8x10, 12x18, 16x24, 20x30, 24x36')
    materials = db.Column(db.String(255), default='Solid Pine Wood, Acrylic Glass, Acid-free Mat')
    is_customizable = db.Column(db.Boolean, default=True)
    is_featured = db.Column(db.Boolean, default=False)
    is_deal_of_day = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'slug': self.slug,
            'category': self.category,
            'price': self.price,
            'original_price': self.original_price,
            'discount_percent': self.discount_percent,
            'rating': self.rating,
            'rating_count': self.rating_count,
            'description': self.description,
            'image_url': self.image_url,
            'badge': self.badge,
            'dimensions': self.dimensions.split(', ') if self.dimensions else [],
            'is_customizable': self.is_customizable,
            'is_featured': self.is_featured,
            'is_deal_of_day': self.is_deal_of_day
        }


class Order(db.Model):
    __tablename__ = 'orders'
    
    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.String(64), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    customer_name = db.Column(db.String(255), nullable=False)
    customer_email = db.Column(db.String(255), nullable=False)
    customer_phone = db.Column(db.String(50), nullable=False)
    address_line1 = db.Column(db.String(255), nullable=False)
    address_line2 = db.Column(db.String(255), nullable=True)
    city = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(100), nullable=False)
    pincode = db.Column(db.String(20), nullable=False)
    payment_method = db.Column(db.String(50), default='COD')
    payment_status = db.Column(db.String(50), default='Pending')
    order_status = db.Column(db.String(50), default='Pending')
    total_amount = db.Column(db.Float, nullable=False, default=0.0)
    tracking_number = db.Column(db.String(100), nullable=True)
    admin_notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    
    items = db.relationship('OrderItem', backref='order', cascade='all, delete-orphan', lazy=True)

    @staticmethod
    def generate_order_number():
        return f"FC-ORD-{uuid.uuid4().hex[:8].upper()}"


class OrderItem(db.Model):
    __tablename__ = 'order_items'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=True)
    product_title = db.Column(db.String(255), nullable=False)
    frame_type = db.Column(db.String(100), default='Classic Walnut Wood')
    frame_size = db.Column(db.String(100), default='12x18 inch')
    mat_color = db.Column(db.String(50), default='Off-White')
    mat_width = db.Column(db.String(50), default='1.5 inch')
    glass_type = db.Column(db.String(100), default='Anti-Glare Acrylic')
    price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, default=1)
    
    # Customer's uploaded photos
    high_res_image_path = db.Column(db.String(500), nullable=True)  # Untouched original for admin print
    preview_mockup_path = db.Column(db.String(500), nullable=True)  # Visualizer preview snapshot
    crop_data = db.Column(db.Text, nullable=True)
