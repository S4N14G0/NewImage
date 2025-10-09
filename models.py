from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    categoria = db.Column(db.String(50), nullable=False)
    precio = db.Column(db.Float, nullable=False)
    descripcion = db.Column(db.Text, nullable=True)
    en_stock = db.Column(db.Boolean, default=True)
    stock = db.Column(db.Integer, default=0)
    tipo = db.Column(db.String(50), default = "principal")

    # Relación 1:N con imágenes
    imagenes = db.relationship("ProductImage", backref="product", lazy=True, cascade="all, delete-orphan")


class ProductImage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(200), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("product.id"), nullable=False)   
    
class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    total = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    items = db.relationship("OrderItem", backref="order", lazy=True)


class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("order.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("product.id"), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)    