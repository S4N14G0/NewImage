from app import app, db
from models import User, Product, ProductImage, Configuracion, CuentaPago
from werkzeug.security import generate_password_hash

with app.app_context():

    print("🟦 Cargando datos iniciales...")

    # -----------------------------
    # 1) CONFIGURACIÓN GLOBAL
    # -----------------------------
    config = Configuracion(dolar_manual=1450, ventas_activas=True)
    db.session.add(config)

    # -----------------------------
    # 2) USUARIO ADMIN
    # -----------------------------
    admin = User(
        username="admin",
        email="admin@admin.com",
        password=generate_password_hash("1"),
        is_admin=True
    )
    db.session.add(admin)

    # -----------------------------
    # 3) CUENTA DE COBRO (Mercado Pago)
    # -----------------------------
    cuenta = CuentaPago(
        nombre="Cuenta Principal",
        banco="Galicia",
        alias="mi.cuenta.alias",
        cbu="0123456789012345678900",
        email="micuenta@correo.com",
        public_key="APP_USR-TU_PUBLIC_KEY",
        access_token="APP_USR-TU_ACCESS_TOKEN",
        activo=True
    )
    db.session.add(cuenta)

    # -----------------------------
    # 4) PRODUCTOS DE EJEMPLO
    # -----------------------------
    producto1 = Product(
        nombre="Producto de prueba",
        categoria="general",
        precio=10000,
        descripcion="Producto cargado automáticamente",
        en_stock=True,
        stock=20,
        tipo="principal",
        activo=True,
        observacion="Ninguna"
    )
    db.session.add(producto1)

    # Imagen asociada (si querés)
    img1 = ProductImage(
        filename="ejemplo.jpg",
        product=producto1
    )
    db.session.add(img1)

    # GUARDAR TODO
    db.session.commit()

    print("✅ Datos iniciales cargados exitosamente")