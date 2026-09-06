import os
import json
import datetime
from functools import wraps
from flask import (
    Flask, render_template, request, redirect, url_for,
    session, flash, jsonify, send_file, send_from_directory, abort
)
from werkzeug.security import check_password_hash, generate_password_hash
from config import Config
from models import db, Product, Order, OrderItem, User, AdminUser, Address
from storage import init_storage, save_uploaded_file, save_base64_preview
from seed_data import seed_database

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

with app.app_context():
    init_storage(app)
    db.create_all()
    seed_database()


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("Please login to proceed with your order.", "warning")
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function


# Context processor for global template variables (Cart badge, Occasion Categories, User Auth)
@app.context_processor
def inject_global_vars():
    cart = session.get('cart', [])
    cart_count = sum(item.get('quantity', 1) for item in cart)
    
    current_user = None
    if 'user_id' in session:
        user_obj = db.session.get(User, session['user_id'])
        if user_obj:
            current_user = user_obj
            
    # Occasion-based Photo Frame Categories
    categories = [
        {"name": "Wedding & Anniversary", "icon": "fa-heart", "desc": "Romantic & Luxury Couple Frames"},
        {"name": "Birthday & Milestones", "icon": "fa-cake-candles", "desc": "Celebration & Milestone Frames"},
        {"name": "Baby & Kids", "icon": "fa-baby", "desc": "Newborn & Nursery Wall Frames"},
        {"name": "Family & Home Living", "icon": "fa-people-roof", "desc": "Family Portraits & Gallery Sets"},
        {"name": "Graduation & Achievements", "icon": "fa-graduation-cap", "desc": "Degree & Convocation Displays"},
        {"name": "Memorial & Vintage", "icon": "fa-clock-rotate-left", "desc": "Cherished Remembrance Frames"}
    ]
    return {
        'site_name': 'FrameCraft',
        'cart_count': cart_count,
        'site_categories': categories,
        'current_user': current_user,
        'current_year': datetime.datetime.now().year,
        'admin_logged_in': session.get('admin_logged_in', False)
    }


# ==========================================
# CUSTOMER AUTHENTICATION
# ==========================================

@app.route('/login', methods=['GET', 'POST'])
def login():
    redirect_url = request.args.get('next') or request.form.get('next') or url_for('index')
    
    if request.method == 'POST':
        identifier = request.form.get('identifier', '').strip()
        password = request.form.get('password', '').strip()
        
        user = User.query.filter((User.email == identifier) | (User.phone == identifier)).first()
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['user_name'] = user.name
            session['user_email'] = user.email
            flash(f"Welcome back, {user.name}!", "success")
            return redirect(redirect_url)
        else:
            flash("Invalid email/phone or password. Please try again or create an account.", "danger")
            
    return render_template('auth/login.html', next=redirect_url)


@app.route('/register', methods=['GET', 'POST'])
def register():
    redirect_url = request.args.get('next') or request.form.get('next') or url_for('index')
    
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        phone = request.form.get('phone', '').strip()
        password = request.form.get('password', '').strip()
        
        if not (name and email and password):
            flash("Name, email, and password are required!", "danger")
            return render_template('auth/register.html', next=redirect_url)
            
        existing = User.query.filter((User.email == email) | (User.phone == phone if phone else False)).first()
        if existing:
            flash("An account already exists with this email or phone number. Please login.", "warning")
            return redirect(url_for('login', next=redirect_url))
            
        new_user = User(
            name=name,
            email=email,
            phone=phone
        )
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        
        session['user_id'] = new_user.id
        session['user_name'] = new_user.name
        session['user_email'] = new_user.email
        
        flash("Account created successfully! You can now proceed with your order.", "success")
        return redirect(redirect_url)
        
    return render_template('auth/register.html', next=redirect_url)


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('user_name', None)
    session.pop('user_email', None)
    flash("You have been signed out.", "info")
    return redirect(url_for('index'))


@app.route('/my-orders')
@login_required
def my_orders():
    orders = Order.query.filter_by(user_id=session['user_id']).order_by(Order.created_at.desc()).all()
    return render_template('account/my_orders.html', orders=orders)


# ==========================================
# STOREFRONT ROUTES
# ==========================================

@app.route('/')
def index():
    deals = Product.query.filter_by(is_deal_of_day=True).limit(4).all()
    featured = Product.query.filter_by(is_featured=True).limit(8).all()
    return render_template('index.html', deals=deals, featured=featured)


@app.route('/products')
def product_catalog():
    query = request.args.get('q', '').strip()
    category = request.args.get('cat', '').strip()
    sort = request.args.get('sort', 'popular')
    
    prod_query = Product.query
    if query:
        prod_query = prod_query.filter(Product.title.ilike(f'%{query}%') | Product.description.ilike(f'%{query}%'))
    if category:
        prod_query = prod_query.filter(Product.category.ilike(f'%{category}%'))
        
    if sort == 'price_low':
        prod_query = prod_query.order_by(Product.price.asc())
    elif sort == 'price_high':
        prod_query = prod_query.order_by(Product.price.desc())
    elif sort == 'rating':
        prod_query = prod_query.order_by(Product.rating.desc())
    else:
        prod_query = prod_query.order_by(Product.is_featured.desc(), Product.id.asc())
        
    products = prod_query.all()
    return render_template('products.html', products=products, query=query, category=category, sort=sort)


@app.route('/product/<slug>')
def product_detail(slug):
    product = Product.query.filter_by(slug=slug).first_or_404()
    related = Product.query.filter(Product.id != product.id, Product.category == product.category).limit(4).all()
    return render_template('product_detail.html', product=product, related=related)


# ==========================================
# INTERACTIVE LIVE FRAME STUDIO
# ==========================================

@app.route('/studio')
@app.route('/studio/<slug>')
def studio(slug=None):
    product = None
    if slug:
        product = Product.query.filter_by(slug=slug).first()
    products = Product.query.all()
    return render_template('studio.html', current_product=product, all_products=products)


@app.route('/api/upload-studio-image', methods=['POST'])
def api_upload_studio_image():
    if 'photo' not in request.files:
        return jsonify({'success': False, 'error': 'No file uploaded'}), 400
    file = request.files['photo']
    if file.filename == '':
        return jsonify({'success': False, 'error': 'No file selected'}), 400
        
    uploaded_url = save_uploaded_file(file, folder_sub='originals')
    if not uploaded_url:
        return jsonify({'success': False, 'error': 'Failed to save image'}), 500
        
    return jsonify({
        'success': True,
        'image_url': uploaded_url
    })


# ==========================================
# CART & CHECKOUT (STRICT LOGIN REQUIRED)
# ==========================================

@app.route('/cart')
def view_cart():
    cart = session.get('cart', [])
    total_price = sum(item.get('price', 0) * item.get('quantity', 1) for item in cart)
    discount = int(total_price * 0.15) if total_price > 1000 else 0
    final_total = max(0, total_price - discount)
    return render_template('cart.html', cart=cart, total_price=total_price, discount=discount, final_total=final_total)


@app.route('/api/cart/add', methods=['POST'])
def api_add_to_cart():
    try:
        if request.content_type and 'multipart/form-data' in request.content_type:
            title = request.form.get('product_title', 'Custom Photo Frame')
            price = float(request.form.get('price', 799.0))
            frame_type = request.form.get('frame_type', 'Classic Solid Walnut')
            frame_size = request.form.get('frame_size', '12x18 inch')
            mat_color = request.form.get('mat_color', 'Off-White')
            mat_width = request.form.get('mat_width', '1.5 inch')
            glass_type = request.form.get('glass_type', 'Anti-Glare Acrylic')
            quantity = int(request.form.get('quantity', 1))
            product_id = request.form.get('product_id', None)
            crop_data = request.form.get('crop_data', '{}')
            
            high_res_url = request.form.get('high_res_image_path', '')
            if 'photo_file' in request.files and request.files['photo_file'].filename != '':
                high_res_url = save_uploaded_file(request.files['photo_file'], folder_sub='originals')
                
            preview_mockup_url = request.form.get('preview_mockup_url', '')
            preview_base64 = request.form.get('preview_mockup_base64', '')
            if preview_base64:
                preview_mockup_url = save_base64_preview(preview_base64, folder_sub='previews')
        else:
            data = request.get_json() or {}
            title = data.get('product_title', 'Custom Photo Frame')
            price = float(data.get('price', 799.0))
            frame_type = data.get('frame_type', 'Classic Solid Walnut')
            frame_size = data.get('frame_size', '12x18 inch')
            mat_color = data.get('mat_color', 'Off-White')
            mat_width = data.get('mat_width', '1.5 inch')
            glass_type = data.get('glass_type', 'Anti-Glare Acrylic')
            quantity = int(data.get('quantity', 1))
            product_id = data.get('product_id', None)
            high_res_url = data.get('high_res_image_path', '')
            preview_mockup_url = data.get('preview_mockup_url', '')
            crop_data = json.dumps(data.get('crop_data', {}))
            
            if data.get('preview_mockup_base64'):
                preview_mockup_url = save_base64_preview(data.get('preview_mockup_base64'), folder_sub='previews')

        if not high_res_url:
            high_res_url = preview_mockup_url or "https://images.unsplash.com/photo-1513519245088-0e12902e5a38?w=800"

        cart = session.get('cart', [])
        cart_item = {
            'item_id': len(cart) + 1,
            'product_id': product_id,
            'product_title': title,
            'frame_type': frame_type,
            'frame_size': frame_size,
            'mat_color': mat_color,
            'mat_width': mat_width,
            'glass_type': glass_type,
            'price': price,
            'quantity': quantity,
            'high_res_image_path': high_res_url,
            'preview_mockup_path': preview_mockup_url or high_res_url,
            'crop_data': crop_data
        }
        cart.append(cart_item)
        session['cart'] = cart
        session.modified = True
        
        return jsonify({'success': True, 'cart_count': len(cart), 'message': 'Frame added to cart!'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/cart/remove/<int:item_id>', methods=['POST'])
def api_remove_from_cart(item_id):
    cart = session.get('cart', [])
    cart = [item for item in cart if item.get('item_id') != item_id]
    session['cart'] = cart
    session.modified = True
    return jsonify({'success': True, 'cart_count': len(cart)})


@app.route('/api/cart/clear', methods=['POST'])
def api_clear_cart():
    session['cart'] = []
    session.modified = True
    return jsonify({'success': True})


# Strict Login Enforcement on Checkout
@app.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    cart = session.get('cart', [])
    if not cart:
        flash("Your cart is empty. Choose a frame to customize first!", "warning")
        return redirect(url_for('index'))
        
    total_price = sum(item.get('price', 0) * item.get('quantity', 1) for item in cart)
    discount = int(total_price * 0.15) if total_price > 1000 else 0
    final_total = max(0, total_price - discount)
    
    current_user = User.query.get(session['user_id'])
    saved_addresses = Address.query.filter_by(user_id=current_user.id).order_by(Address.is_default.desc(), Address.id.desc()).all()

    if request.method == 'POST':
        name = request.form.get('customer_name', '').strip()
        email = request.form.get('customer_email', '').strip()
        phone = request.form.get('customer_phone', '').strip()
        address1 = request.form.get('address_line1', '').strip()
        address2 = request.form.get('address_line2', '').strip()
        city = request.form.get('city', '').strip()
        state = request.form.get('state', '').strip()
        pincode = request.form.get('pincode', '').strip()
        address_type = request.form.get('address_type', 'HOME').upper()
        save_addr = request.form.get('save_address', '1')  # Default to saving
        payment_method = request.form.get('payment_method', 'COD')

        if not (name and phone and address1 and city and state and pincode):
            flash("Please fill in all mandatory address fields!", "danger")
            return render_template('checkout.html', cart=cart, total_price=total_price, discount=discount, final_total=final_total, user=current_user, saved_addresses=saved_addresses)

        # Automatically Save / Update address in user profile
        if save_addr in ['1', 'true', 'on', 'yes']:
            existing_addr = Address.query.filter_by(
                user_id=current_user.id,
                pincode=pincode,
                address_line1=address1
            ).first()
            if not existing_addr:
                is_first = (len(saved_addresses) == 0)
                new_saved_addr = Address(
                    user_id=current_user.id,
                    name=name,
                    phone=phone,
                    pincode=pincode,
                    address_line1=address1,
                    address_line2=address2,
                    city=city,
                    state=state,
                    address_type=address_type if address_type in ['HOME', 'WORK'] else 'HOME',
                    is_default=is_first
                )
                db.session.add(new_saved_addr)
            if not current_user.phone and phone:
                current_user.phone = phone

        order_num = Order.generate_order_number()
        new_order = Order(
            order_number=order_num,
            user_id=current_user.id,
            customer_name=name,
            customer_email=email or current_user.email,
            customer_phone=phone or current_user.phone or 'Not provided',
            address_line1=address1,
            address_line2=address2,
            city=city,
            state=state,
            pincode=pincode,
            payment_method=payment_method,
            payment_status='Pending' if payment_method == 'COD' else 'Paid (Verified)',
            order_status='Pending',
            total_amount=final_total
        )
        db.session.add(new_order)
        db.session.flush()

        for item in cart:
            order_item = OrderItem(
                order_id=new_order.id,
                product_id=item.get('product_id'),
                product_title=item.get('product_title', 'Custom Frame'),
                frame_type=item.get('frame_type', 'Classic Solid Walnut'),
                frame_size=item.get('frame_size', '12x18 inch'),
                mat_color=item.get('mat_color', 'Off-White'),
                mat_width=item.get('mat_width', '1.5 inch'),
                glass_type=item.get('glass_type', 'Anti-Glare Acrylic'),
                price=item.get('price', 799.0),
                quantity=item.get('quantity', 1),
                high_res_image_path=item.get('high_res_image_path'),
                preview_mockup_path=item.get('preview_mockup_path'),
                crop_data=str(item.get('crop_data', ''))
            )
            db.session.add(order_item)

        db.session.commit()
        
        session['cart'] = []
        session.modified = True

        return redirect(url_for('order_success', order_number=order_num))

    return render_template('checkout.html', cart=cart, total_price=total_price, discount=discount, final_total=final_total, user=current_user, saved_addresses=saved_addresses)


@app.route('/api/addresses/save', methods=['POST'])
@login_required
def api_save_address():
    data = request.form or request.get_json() or {}
    name = data.get('name', '').strip()
    phone = data.get('phone', '').strip()
    pincode = data.get('pincode', '').strip()
    address1 = data.get('address_line1', '').strip()
    address2 = data.get('address_line2', '').strip()
    city = data.get('city', '').strip()
    state = data.get('state', '').strip()
    address_type = data.get('address_type', 'HOME').upper()

    if not (name and phone and pincode and address1 and city and state):
        return jsonify({'success': False, 'message': 'Missing mandatory address fields'}), 400

    new_addr = Address(
        user_id=session['user_id'],
        name=name,
        phone=phone,
        pincode=pincode,
        address_line1=address1,
        address_line2=address2,
        city=city,
        state=state,
        address_type=address_type if address_type in ['HOME', 'WORK'] else 'HOME',
        is_default=False
    )
    db.session.add(new_addr)
    db.session.commit()
    return jsonify({'success': True, 'address_id': new_addr.id, 'message': 'Address saved successfully!'})


@app.route('/api/addresses/<int:addr_id>/delete', methods=['POST'])
@login_required
def api_delete_address(addr_id):
    addr = Address.query.filter_by(id=addr_id, user_id=session['user_id']).first_or_404()
    db.session.delete(addr)
    db.session.commit()
    flash("Address removed.", "info")
    return redirect(url_for('checkout'))


@app.route('/order-success/<order_number>')
@login_required
def order_success(order_number):
    order = Order.query.filter_by(order_number=order_number).first_or_404()
    return redirect(url_for('order_detail', order_number=order_number))


@app.route('/order/<order_number>')
def order_detail(order_number):
    order = Order.query.filter_by(order_number=order_number).first_or_404()
    return render_template('order_detail.html', order=order)


@app.route('/track-order', methods=['GET', 'POST'])
def track_order():
    if request.method == 'POST':
        order_num = request.form.get('order_number', '').strip()
        phone = request.form.get('phone', '').strip()
        order = Order.query.filter_by(order_number=order_num).first()
        if not order or (phone and order.customer_phone[-4:] != phone[-4:]):
            flash("No order found matching these details. Please check the order number.", "danger")
            return render_template('track_order.html', order=None)
        return redirect(url_for('order_detail', order_number=order.order_number))
    return render_template('track_order.html', order=None)


# ==========================================
# ADMIN DASHBOARD & PRINT ORDER CENTER
# ==========================================

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if session.get('admin_logged_in'):
        return redirect(url_for('admin_orders'))
        
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        # Check against database AdminUser
        admin_user = AdminUser.query.filter((AdminUser.username == username) | (AdminUser.email == username)).first()
        
        if admin_user and admin_user.check_password(password):
            session['admin_logged_in'] = True
            session['admin_user_id'] = admin_user.id
            session['admin_name'] = admin_user.name
            flash(f"Welcome back, {admin_user.name}! Print Lab Connected.", "success")
            return redirect(url_for('admin_orders'))
        elif username == Config.ADMIN_USERNAME and password == Config.ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            session['admin_name'] = "Master Admin"
            flash("Master Admin Authenticated! Welcome to Print Fulfillment Hub.", "success")
            return redirect(url_for('admin_orders'))
        else:
            flash("Invalid Admin username or security key.", "danger")
            
    return render_template('admin/login.html')


@app.route('/admin/register', methods=['GET', 'POST'])
def admin_register():
    if session.get('admin_logged_in'):
        return redirect(url_for('admin_orders'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        
        if not username or not email or not password:
            flash("All fields are required to register an Admin account.", "warning")
            return render_template('admin/register.html')
            
        existing = AdminUser.query.filter((AdminUser.username == username) | (AdminUser.email == email)).first()
        if existing:
            flash("An admin with this username or email already exists.", "danger")
            return render_template('admin/register.html')
            
        new_admin = AdminUser(username=username, name=name, email=email)
        new_admin.set_password(password)
        db.session.add(new_admin)
        db.session.commit()
        
        session['admin_logged_in'] = True
        session['admin_user_id'] = new_admin.id
        session['admin_name'] = new_admin.name
        flash(f"Admin account for '{name}' created successfully! Welcome to FrameCraft Lab.", "success")
        return redirect(url_for('admin_orders'))

    return render_template('admin/register.html')


@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    session.pop('admin_user_id', None)
    session.pop('admin_name', None)
    flash("Admin logged out successfully.", "info")
    return redirect(url_for('admin_login'))


@app.route('/admin')
@app.route('/admin/orders')
def admin_orders():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
        
    status_filter = request.args.get('status', 'all')
    if status_filter != 'all':
        orders = Order.query.filter_by(order_status=status_filter).order_by(Order.created_at.desc()).all()
    else:
        orders = Order.query.order_by(Order.created_at.desc()).all()
        
    total_orders = Order.query.count()
    pending_orders = Order.query.filter_by(order_status='Pending').count()
    printing_orders = Order.query.filter_by(order_status='Printing Photo').count()
    shipped_orders = Order.query.filter_by(order_status='Shipped').count()
    
    return render_template(
        'admin/orders.html',
        orders=orders,
        status_filter=status_filter,
        total_orders=total_orders,
        pending_orders=pending_orders,
        printing_orders=printing_orders,
        shipped_orders=shipped_orders
    )


@app.route('/admin/orders/<int:order_id>/status', methods=['POST'])
def admin_update_order_status(order_id):
    if not session.get('admin_logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
        
    order = Order.query.get_or_404(order_id)
    new_status = request.form.get('order_status')
    tracking_number = request.form.get('tracking_number')
    admin_notes = request.form.get('admin_notes')
    
    if new_status:
        order.order_status = new_status
    if tracking_number is not None:
        order.tracking_number = tracking_number
    if admin_notes is not None:
        order.admin_notes = admin_notes
        
    db.session.commit()
    flash(f"Order {order.order_number} status updated to '{order.order_status}'!", "success")
    return redirect(url_for('admin_orders'))


@app.route('/admin/download-photo/<int:item_id>')
def admin_download_photo(item_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
        
    item = OrderItem.query.get_or_404(item_id)
    photo_path = item.high_res_image_path
    
    if not photo_path:
        flash("No uploaded photo found for this order item.", "danger")
        return redirect(url_for('admin_orders'))
        
    if photo_path.startswith('/uploads/'):
        relative_path = photo_path.replace('/uploads/', '', 1)
        full_path = os.path.join(Config.UPLOAD_FOLDER, relative_path)
        if os.path.exists(full_path):
            ext = os.path.splitext(full_path)[1]
            download_filename = f"PRINT_{item.order.order_number}_{item.frame_size.replace(' ', '_')}_{item_id}{ext}"
            return send_file(full_path, as_attachment=True, download_name=download_filename)
        else:
            flash("Image file not found on local storage.", "danger")
            return redirect(url_for('admin_orders'))
            
    return redirect(photo_path)


@app.route('/admin/products')
def admin_products():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    products = Product.query.order_by(Product.id.asc()).all()
    return render_template('admin/products.html', products=products)


@app.route('/admin/products/add', methods=['POST'])
def admin_add_product():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
        
    title = request.form.get('title')
    category = request.form.get('category')
    price = float(request.form.get('price', 799))
    original_price = float(request.form.get('original_price', 1599))
    description = request.form.get('description')
    image_url = request.form.get('image_url')
    dimensions = request.form.get('dimensions', '8x10, 12x18, 16x24')
    
    import re
    slug = re.sub(r'[^a-zA-Z0-9]+', '-', title.lower()).strip('-')
    discount = int(((original_price - price) / original_price) * 100) if original_price > price else 0
    
    new_p = Product(
        title=title,
        slug=slug,
        category=category,
        price=price,
        original_price=original_price,
        discount_percent=discount,
        description=description,
        image_url=image_url or "https://images.unsplash.com/photo-1513519245088-0e12902e5a38?w=800",
        dimensions=dimensions
    )
    db.session.add(new_p)
    db.session.commit()
    flash(f"Frame '{title}' added successfully!", "success")
    return redirect(url_for('admin_products'))


@app.route('/uploads/<path:filename>')
def serve_uploads(filename):
    return send_from_directory(Config.UPLOAD_FOLDER, filename)


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
