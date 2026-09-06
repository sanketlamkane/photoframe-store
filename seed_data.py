from models import db, Product, Order, OrderItem, AdminUser
import datetime

def seed_database():
    # Only seed initial sample products if database is empty to preserve data permanently
    if Product.query.first():
        # Ensure default admin user exists without wiping data
        if not AdminUser.query.filter_by(username='admin').first():
            admin = AdminUser(
                username='admin',
                name='Print Lab Master Admin',
                email='admin@framecraft.com',
                role='Super Admin'
            )
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
        return
    
    sample_products = [
        Product(
            title="Royal Wedding & Anniversary Gold Leaf Frame",
            slug="royal-wedding-anniversary-gold-leaf-frame",
            category="Wedding & Anniversary",
            price=1299.0,
            original_price=2599.0,
            discount_percent=50,
            rating=4.9,
            rating_count=4210,
            description="Exquisite gold leaf finish with dual couple photo matting. Designed specifically for wedding portraits, engagement memories, and anniversary celebrations.",
            image_url="https://images.unsplash.com/photo-1519741497674-611481863552?w=800&auto=format&fit=crop&q=80",
            badge="Top Seller",
            dimensions="8x10, 12x18, 16x24, 20x30, 24x36",
            materials="Solid Handcrafted Timber + Gold Patina Gilding, Anti-Glare Glass",
            is_customizable=True,
            is_featured=True,
            is_deal_of_day=True
        ),
        Product(
            title="Happy Birthday Special Keepsake Photo Frame",
            slug="happy-birthday-special-keepsake-photo-frame",
            category="Birthday & Milestones",
            price=699.0,
            original_price=1399.0,
            discount_percent=50,
            rating=4.8,
            rating_count=3120,
            description="Vibrant celebration frame with customizable date and celebration border. Perfect gift for 1st birthday, sweet 16, 18th, 21st, 50th, and milestone birthdays.",
            image_url="https://images.unsplash.com/photo-1530103862676-de8c9debad1d?w=800&auto=format&fit=crop&q=80",
            badge="Birthday Special",
            dimensions="6x4, 8x10, 12x18, 16x24",
            materials="Nordic White Pine Wood, Acid-free Party Bevel Mat",
            is_customizable=True,
            is_featured=True,
            is_deal_of_day=True
        ),
        Product(
            title="Precious Baby Birth Milestone & Nursery Frame",
            slug="precious-baby-birth-milestone-nursery-frame",
            category="Baby & Kids",
            price=749.0,
            original_price=1499.0,
            discount_percent=50,
            rating=4.9,
            rating_count=2890,
            description="Soft natural wood with pastel ivory matting. Safe, non-toxic shatterproof acrylic glass ideal for newborn baby portraits, handprint memories, and kids rooms.",
            image_url="https://images.unsplash.com/photo-1519689680058-324335c77eba?w=800&auto=format&fit=crop&q=80",
            badge="Newborn Special",
            dimensions="6x4, 8x10, 12x18, 16x24",
            materials="Natural Sustainable Pine, Shatterproof Baby-Safe Acrylic",
            is_customizable=True,
            is_featured=True,
            is_deal_of_day=False
        ),
        Product(
            title="Grand Family Portrait Solid Walnut Wooden Frame",
            slug="grand-family-portrait-solid-walnut-wooden-frame",
            category="Family & Home Living",
            price=999.0,
            original_price=1999.0,
            discount_percent=50,
            rating=4.8,
            rating_count=5140,
            description="Deep rich walnut hardwood with double-thick off-white museum matting. Designed for multi-generation family gatherings, living room centerpieces, and heritage walls.",
            image_url="https://images.unsplash.com/photo-1511895426328-dc8714191300?w=800&auto=format&fit=crop&q=80",
            badge="Family Favorite",
            dimensions="8x10, 12x18, 16x24, 20x30, 24x36",
            materials="Solid Hardwood Walnut, Cotton Rag Mat, Anti-Reflective Glass",
            is_customizable=True,
            is_featured=True,
            is_deal_of_day=True
        ),
        Product(
            title="Graduation Degree & Convocation Photo Frame",
            slug="graduation-degree-convocation-photo-frame",
            category="Graduation & Achievements",
            price=849.0,
            original_price=1699.0,
            discount_percent=50,
            rating=4.7,
            rating_count=1950,
            description="Matte black satin finish with dual cutout for holding both your university degree / certificate and graduation convocation portrait side by side.",
            image_url="https://images.unsplash.com/photo-1523050854058-8df90110c9f1?w=800&auto=format&fit=crop&q=80",
            badge="Achievement",
            dimensions="8x10, 12x18, 16x24",
            materials="Anodized Satin Black Wood, Gold Inlay Bevel Mat",
            is_customizable=True,
            is_featured=False,
            is_deal_of_day=False
        ),
        Product(
            title="Modern Couple Floating Acrylic Glass Frame",
            slug="modern-couple-floating-acrylic-glass-frame",
            category="Wedding & Anniversary",
            price=1199.0,
            original_price=2399.0,
            discount_percent=50,
            rating=4.9,
            rating_count=3600,
            description="Frameless double-sheet acrylic with stainless steel chrome wall standoffs. Your romantic photo appears suspended in air with futuristic 3D depth.",
            image_url="https://images.unsplash.com/photo-1582561424760-0321d75e81fa?w=800&auto=format&fit=crop&q=80",
            badge="Trending",
            dimensions="8x10, 12x18, 16x24, 20x30",
            materials="Double Cast Acrylic Glass + 4 Brushed Steel Wall Standoffs",
            is_customizable=True,
            is_featured=True,
            is_deal_of_day=True
        ),
        Product(
            title="Family Multi-Photo Story Collage Frame Set",
            slug="family-multi-photo-story-collage-frame-set",
            category="Family & Home Living",
            price=1499.0,
            original_price=2999.0,
            discount_percent=50,
            rating=4.8,
            rating_count=2420,
            description="Multi-aperture mat displaying your favorite 4 to 6 family travel memories together in a single magnificent gallery frame.",
            image_url="https://images.unsplash.com/photo-1513519245088-0e12902e5a38?w=800&auto=format&fit=crop&q=80",
            badge="Best Value",
            dimensions="12x18, 16x24, 20x30",
            materials="Solid Oak Profile, 6-Opening Beveled Collage Mat",
            is_customizable=True,
            is_featured=True,
            is_deal_of_day=False
        ),
        Product(
            title="Loving Memorial & Remembrance Heritage Frame",
            slug="loving-memorial-remembrance-heritage-frame",
            category="Memorial & Vintage",
            price=899.0,
            original_price=1799.0,
            discount_percent=50,
            rating=4.9,
            rating_count=1380,
            description="Dignified dark mahogany with antique gold inner fillet and black velvet backing. A timeless tribute for honoring cherished ancestors and loved ones.",
            image_url="https://images.unsplash.com/photo-1583847268964-b28dc8f51f92?w=800&auto=format&fit=crop&q=80",
            badge="Heritage",
            dimensions="8x10, 12x18, 16x24",
            materials="Solid Mahogany Wood, Gold Fillet Inset, Velvet Backing",
            is_customizable=True,
            is_featured=False,
            is_deal_of_day=False
        )
    ]
    
    db.session.bulk_save_objects(sample_products)
    
    if not AdminUser.query.filter_by(username='admin').first():
        admin = AdminUser(
            username='admin',
            name='Print Lab Master Admin',
            email='admin@framecraft.com',
            role='Super Admin'
        )
        admin.set_password('admin123')
        db.session.add(admin)
        
    db.session.commit()
    print("Database initialized with Occasion-based Photo Frames & Admin Account!")
