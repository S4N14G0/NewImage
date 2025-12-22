from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

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
    imagenes = db.relationship("ProductImage", backref="product", lazy=True, cascade="all, delete-orphan")
    activo = db.Column(db.Boolean, default=True)
    observacion = db.Column(db.String(200), nullable=True)

class Configuracion(db.Model):
    id = db.Column(db.Integer, primary_key= True)
    dolar_manual = db.Column(db.Float, nullable=False, default=1450)
    ventas_activas = db.Column(db.Boolean, default=True)
    
class ProductImage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(200), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("product.id"), nullable=False)   
    
class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    total = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    cuenta_pago_id = db.Column(db.Integer, db.ForeignKey("cuenta_pago.id"))
    estado_pago = db.Column(db.String(50), default="pendiente")

    cuenta_pago = db.relationship("CuentaPago", backref="ordenes")

    items = db.relationship("OrderItem", backref="order", lazy=True)


class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("order.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("product.id"), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)    
    
    
class CuentaPago(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    banco = db.Column(db.String(100))
    alias = db.Column(db.String(100))
    cbu = db.Column(db.String(22))
    email = db.Column(db.String(120))
    public_key = db.Column(db.String(200))
    access_token = db.Column(db.String(200))
    activo = db.Column(db.Boolean, default=False)
    
    def __repr__(self):
        return f"<CuentaPago {self.nombre}>"
    def to_dict(self):
        return {
            "id": self.id,
            "nombre": self.nombre,
            "email": self.email,
            "banco": getattr(self, "banco", None),
            "alias": getattr(self, "alias", None),
            "cbu": getattr(self, "cbu", None),
            "public_key": self.public_key,
            "activo": self.activo
        }
        

class Venta(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    comprador_nombre = db.Column(db.String(120))
    comprador_telefono = db.Column(db.String(50))
    comprador_email = db.Column(db.String(120))
    metodo_pago = db.Column(db.String(50))  # MP - Transferencia
    cuenta_destino = db.Column(db.String(120))  # alias o CBU
    monto_total = db.Column(db.Float)
    estado = db.Column(db.String(20), default="pendiente")
    items = db.relationship("VentaItem", backref="venta", cascade="all, delete-orphan")


class VentaItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    venta_id = db.Column(db.Integer, db.ForeignKey("venta.id"))
    producto_nombre = db.Column(db.String(200))
    cantidad = db.Column(db.Integer)
    precio_unitario = db.Column(db.Float)

class PasswordReset(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120))
    token = db.Column(db.String(200), unique = True)
    expires_at = db.Column(db.DateTime)    






