import os
from flask import Flask, render_template, request, redirect, url_for, flash, session, g, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Product, Order, OrderItem, ProductImage, Configuracion, CuentaPago
from helpers import login_required
from werkzeug.utils import secure_filename
from functools import wraps
from flask import abort
# from flask_migrate import Migrate
from mercadopago import SDK
print(CuentaPago.query.all())        # Ver si hay cuentas
print(CuentaPago.query.filter_by(activo=True).first())   # Ver si hay activa
# ---------------------------------------------------
# CONFIGURACIÓN DE FLASK
# ---------------------------------------------------
app = Flask(__name__)
app.secret_key = "NewImage"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///tienda.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
# migrate = Migrate(app, db)

ALLOWED_HOSTS = [
    "newimagepilates.com",
    "www.newimagepilates.com",
    "newimage-9i3u.onrender.com",
]

db.init_app(app)

#----------------------------------------------------
# CONFIGURACION MERCADO PAGO
#----------------------------------------------------
sdk = SDK("TOKEN")

MP_ACCESS_TOKEN = os.getenv("MP_ACCESS_TOKEN")
MP_PUBLIC_KEY = os.getenv("MP_PUBLIC_KEY")

if MP_ACCESS_TOKEN:
    mp = SDK(MP_ACCESS_TOKEN)
else:
    mp = None



# Crea tablas
with app.app_context():
    db.create_all()

# ---------------------------------------------------
# DECORADORES Y FUNCIONES AUXILIARES
# ---------------------------------------------------

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        
        user = User.query.get(session["user_id"])
        if not user or not user.is_admin:
            abort(403)  # Prohibido
        return f(*args, **kwargs)
    return decorated_function

def obtener_estado_ventas():
    config = Configuracion.query.first()
    if not config:
        config = Configuracion(dolar_manual=1450, ventas_activas=True)
        db.session.add(config)
        db.session.commit()
    return config.ventas_activas

def obtener_dolar_manual():
    config = Configuracion.query.first()
    if not config:
        config = Configuracion(dolar_manual=1450, ventas_activas=True)
        db.session.add(config)
        db.session.commit()
    return config.dolar_manual

@app.route('/update_dolar', methods=['POST'])
@login_required
def update_dolar():
    nuevo_valor = request.form.get("nuevo_dolar")

    if not nuevo_valor:
        flash("Debes ingresar un valor.", "error")
        return redirect(url_for('admin_dashboard'))

    config = Configuracion.query.first()
    if not config:
        config = Configuracion(dolar=nuevo_valor)
        db.session.add(config)
    else:
        config.dolar = nuevo_valor

    db.session.commit()

    flash("Valor del dólar actualizado correctamente.", "success")
    return redirect(url_for('admin_dashboard'))

def serializar_producto(producto):
    return {
        "id": producto.id,
        "nombre": producto.nombre,
        "descripcion": producto.descripcion,
        "precio": producto.precio,
        "tipo": producto.tipo,
        "imagenes": [{"filename": img.filename} for img in producto.imagenes],
        "stock": producto.stock,
        "en_stock": producto.en_stock,
        "observacion": producto.observacion
    }

# ---------------------------------------------------
# RUTAS PRINCIPALES
# ---------------------------------------------------

# Ruta Index
@app.route("/")
def index():
    user = None
    if "user_id" in session:
        user = User.query.get(session["user_id"])  # Recupera el usuario logueado
    return render_template("index.html", user=user)

# Ruta Login
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            session["user_id"] = user.id
            session["username"] = user.username
            session["is_admin"] = bool(user.is_admin)
            print("Usuario logueado:", user.username, "Admin:", session.get("is_admin"))
            return redirect(url_for("index"))

        else:
            flash("La contraseña o el email no son correctos. Inténtalo de nuevo.", "error")
            return redirect(url_for("login")), 401

    return render_template("Login.html")

# Ruta SignUp
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]
        confirm = request.form["confirm_password"]

        if password != confirm:
            flash("Las contraseñas no coinciden", "error")
            return redirect(url_for("signup"))

        # Encriptar la contraseña
        hashed_pw = generate_password_hash(password, method="pbkdf2:sha256")

        # Crear usuario
        new_user = User(username=username, email=email, password=hashed_pw)

        try:
            db.session.add(new_user)
            db.session.commit()
            flash("Cuenta creada con éxito. Inicia sesión ahora.", "success")
            return redirect(url_for("login"))
        except:
            flash("El email ya está registrado", "error")
            return redirect(url_for("signup"))

    return render_template("Login.html")

# Ruta tienda (protegida, requiere login)
@app.route("/shop")
def shop():
    products = Product.query.filter_by(tipo="principal").all()
    dolar_manual = obtener_dolar_manual()
    ventas_activas = obtener_estado_ventas()
    
    # Convertir productos a lista de diccionarios
    productos_json = [serializar_producto(p) for p in products]

    return render_template("Shop.html", products=productos_json, dolar=dolar_manual, ventas_activas=ventas_activas)

# Ruta de los repuestos
@app.route("/repuestos")
def repuestos():
    productos = Product.query.filter_by(tipo="repuesto", activo=True).all()
    dolar_manual = obtener_dolar_manual()
    ventas_activas = obtener_estado_ventas()
    
    productos_json = [serializar_producto(p) for p in productos]
    
    return render_template("repuestos.html", products=productos_json, dolar=dolar_manual, ventas_activas=ventas_activas)

# Página de detalle de un producto
@app.route("/product/<int:product_id>")
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)
    dolar_manual = obtener_dolar_manual()
    ventas_activas = obtener_estado_ventas()
    # Convertir a diccionario serializable
    producto_json = serializar_producto(product)

    return render_template(
        "product_detail.html",
        product=producto_json,
        dolar=dolar_manual,
        ventas_activas=ventas_activas
    )

@app.template_filter('formato_pesos')
def formato_pesos(valor):
    """Convierte números a formato argentino con puntos como separador de miles."""
    try:
        return "{:,.2f}".format(float(valor)).replace(",", "X").replace(".", ",").replace("X", ".")
    except (ValueError, TypeError):
        return valor

# ---------------------------------------------------
# RUTAS DE CHECKOUT Y SESIÓN
# ---------------------------------------------------

# Ruta checkout
@app.route("/check")
@login_required
def check():
    cuenta = get_cuenta_activa()
    
    if cuenta is None:
        return "No hay cuenta activa configurada en el panel admin", 500
    
    return render_template("CheckOut.html", cuenta=cuenta, public_key=cuenta.public_key)



# Logout
@app.route("/logout", methods=["POST"])
def logout():
    session.pop("user_id", None)
    session.pop("username", None)
    return redirect(url_for("index"))

# ---------------------------------------------------
# RUTAS DE PERFIL Y ADMIN
# ---------------------------------------------------

# Ruta de perfiles
@app.route("/profile")
@login_required
def profile():
    user = User.query.get(session["user_id"])
    return render_template("profile.html", user=user)

# Ruta de admin
@app.route("/admin")
@admin_required
def admin_dashboard():
    cuentas = CuentaPago.query.all()
    filtro = request.args.get("filtro", "todo")
    config = Configuracion.query.first()
    ventas_activas = config.ventas_activas if config else True
    
    if filtro == "principal":
        productos = Product.query.filter_by(tipo="principal").all()
    elif filtro == "repuesto":
        productos = Product.query.filter_by(tipo="repuesto").all()
    else: 
        productos = Product.query.all()
        
    dolar = obtener_dolar_manual()    
    
    return render_template("admin_dashboard.html", cuentas=cuentas, products=productos, filtro=filtro, dolar=dolar, ventas_activas=ventas_activas)

@app.route("/admin_cuentas")
@login_required
def admin_cuentas():
    cuentas = CuentaPago.query.all()
    return render_template("admin_cuentas.html", cuentas=cuentas)

# ---------------------------------------------------
# CONTEXT PROCESSORS Y BEFORE REQUEST
# ---------------------------------------------------

@app.context_processor
def inject_user():
    user_id = session.get("user_id")
    if user_id:
        user = User.query.get(user_id)
        return dict(user=user)
    return dict(user=None)

@app.before_request
def load_logged_in_user():
    g.user = None
    if "user_id" in session:
        g.user = User.query.get(session["user_id"])

# ----------------------------------------------------------------------------
# CONFIGURACIÓN DE SUBIDAS DE ARCHIVOS
# ----------------------------------------------------------------------------
UPLOAD_FOLDER = os.path.join("static", "uploads")
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # Crea la carpeta si no existe

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

# ---------------------------------------------------
# RUTAS DE PRODUCTOS (ADMIN)
# ---------------------------------------------------

# Crear producto
@app.route("/product/new", methods=["GET", "POST"])
@admin_required
def new_product():
    if request.method == "POST":
        nombre = request.form["nombre"]
        categoria = request.form["categoria"]
        precio = float(request.form["precio"])
        descripcion = request.form["descripcion"]
        stock = int(request.form["stock"])
        tipo = request.form["tipo"]
        observacion = request.form.get("observacion", "")

        product = Product(
            nombre=nombre,
            categoria=categoria,
            precio=precio,
            descripcion=descripcion,
            en_stock=(stock > 0),
            stock=stock,
            tipo=tipo,
            observacion=observacion
        )
        db.session.add(product)
        db.session.commit()  # ahora el producto ya tiene un ID válido

        # Manejo de múltiples imágenes
        files = request.files.getlist("imagenes")
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))

                new_image = ProductImage(filename=filename, product_id=product.id)
                db.session.add(new_image)

        db.session.commit()  # guarda imágenes en la DB

        flash("Producto agregado con éxito", "success")
        return redirect(url_for("admin_dashboard"))

    return render_template("new_product.html")

# Editar un producto
@app.route("/product/<int:product_id>/edit", methods=["GET", "POST"])
@admin_required
def edit_product(product_id):
    product = Product.query.get_or_404(product_id)

    if request.method == "POST":
        # Actualizar datos base
        product.nombre = request.form["nombre"]
        product.categoria = request.form["categoria"]
        product.precio = float(request.form["precio"])
        product.descripcion = request.form["descripcion"]
        product.stock = int(request.form["stock"])
        product.en_stock = product.stock > 0
        product.tipo = request.form.get("tipo", "principal")

        # Manejo de imágenes (permite varias)
        files = request.files.getlist("imagenes")

        if files and files[0].filename != "":
            # Eliminar imágenes anteriores
            for img in product.imagenes:
                db.session.delete(img)

            # Determinar carpeta según el tipo
            if product.tipo == "repuesto":
                upload_folder = os.path.join(app.config["UPLOAD_FOLDER"], "repuestos")
            else:
                upload_folder = app.config["UPLOAD_FOLDER"]

            os.makedirs(upload_folder, exist_ok=True)

            # Guardar nuevas imágenes
            for file in files:
                if allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    file.save(os.path.join(upload_folder, filename))

                    new_image = ProductImage(filename=filename, product_id=product.id)
                    db.session.add(new_image)
        print("Tipo guardado:", product.tipo)
        db.session.commit()
        flash("Producto actualizado con éxito", "success")
        return redirect(url_for("admin_dashboard"))
    
    return render_template("edit_product.html", product=product)

# Eliminar un producto
@app.route("/product/delete/<int:product_id>", methods=["POST"])
@admin_required
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    flash("Producto eliminado con éxito", "success")
    return redirect(url_for("admin_dashboard"))

# ---------------------------------------------------
# RUTAS DE CHECKOUT Y PAGOS
# ---------------------------------------------------

@app.route("/update_observacion/<int:product_id>", methods=["POST"])
@admin_required
def update_observacion(product_id):
    data = request.get_json()
    obs = data.get("observacion", "")

    product = Product.query.get_or_404(product_id)
    product.observacion = obs
    db.session.commit()

    return jsonify({"message": "Observación actualizada correctamente"})

@app.route("/checkout", methods=["POST"])
@login_required
def checkout():
    cart = request.json.get("cart", [])
    repuestos = request.json.get("repuestos", [])

    if not cart and not repuestos:
        return {"error": "El carrito está vacío"}, 400

    total = sum(
        (item.get("priceARS") or item.get("price") or 0) * item.get("quantity", 0)
        for item in cart + repuestos
    )
    order = Order(user_id=session["user_id"], total=total)
    db.session.add(order)
    db.session.commit()

    for item in cart + repuestos:
        order_item = OrderItem(
            order_id=order.id,
            product_id=item["id"],
            quantity=item["quantity"],
            price=item.get("priceARS") or item.get("price") or 0
        )
        db.session.add(order_item)

    db.session.commit()

    return {
        "message": "Compra realizada con éxito",
        "order_id": order.id,
        "total": total
    }, 201

@app.route("/checkout/confirm", methods=["POST"])
@login_required
def checkout_confirm():
    cart = request.json.get("cart", [])
    for item in cart:
        product = Product.query.get(item["id"])
        if product:
            if product.stock < item["quantity"]:
                return {"error": f"Stock insuficiente para {product.nombre}"}, 400
            
            product.stock -= item["quantity"]
            if product.stock <= 0:
                product.en_stock = False
    db.session.commit()
    return {"success": True, "message": "Compra realizada correctamente."}

@app.route("/crear_pago", methods=["POST"])
def crear_pago():
    # Obtener la cuenta activa desde la base de datos
    cuenta = get_cuenta_activa()

    if not cuenta or not cuenta.access_token:
        return jsonify({"error": "No hay una cuenta activa con Access Token configurado"}), 400

    # Instancia real del SDK con el Access Token de la cuenta activa
    sdk = SDK(cuenta.access_token)

    data = request.get_json()
    if not data:
        return jsonify({"error": "No se recibió JSON válido"}), 400

    email = data.get("email")
    cart = data.get("cart", [])

    if not cart:
        return jsonify({"error": "El carrito está vacío"}), 400

    # Convertir carrito a items de MercadoPago
    items_mp = []
    for item in cart:
        items_mp.append({
            "title": item["name"],
            "quantity": int(item["quantity"]),
            "currency_id": "ARS",
            "unit_price": float(item["price"])
        })

    preference_data = {
        "items": items_mp,
        "payer": {
            "email": email
        },
        "back_urls": {
            "success": "https://newimagepilates.com/pago_exitoso",
            "failure": "https://newimagepilates.com/pago_fallido",
            "pending": "https://newimagepilates.com/pago_pendiente"
        },
        "auto_return": "approved"
    }

    preference_response = sdk.preference().create(preference_data)

    # Log para debug
    print("JSON recibido:", data)
    print("Carrito:", cart)
    print("Email:", email)

    return jsonify(preference_response["response"])

# ---------------------------------------------------
# FUNCIONES AUXILIARES
# ---------------------------------------------------

def ventas_activas():
    """Obtiene el estado de las ventas desde la tabla Configuracion."""
    config = Configuracion.query.first()
    if not config:
        config = Configuracion(dolar_manual=1450, ventas_activas=True)
        db.session.add(config)
        db.session.commit()
    return config.ventas_activas

def get_cuenta_activa():
    return CuentaPago.query.filter_by(activo=True).first()

# ---------------------------------------------------
# RUTAS DE CONFIGURACIÓN
# ---------------------------------------------------

@app.route("/toggle_ventas", methods=["POST"])
@admin_required
def toggle_ventas():
    config = Configuracion.query.first()
    if not config:
        config = Configuracion(dolar_manual=1450, ventas_activas=True)
        db.session.add(config)
        db.session.commit()

    # Cambiar el estado
    config.ventas_activas = not config.ventas_activas
    db.session.commit()

    estado = "activadas" if config.ventas_activas else "desactivadas"
    flash(f"Las ventas fueron {estado}.", "success")
    return redirect(url_for("admin_dashboard"))

# ---------------------------------------------------
# RUTAS DE CUENTAS DE PAGO
# ---------------------------------------------------

@app.route("/admin/set_cuenta/<int:cuenta_id>", methods=["POST"])
@login_required
def set_cuenta_activa(cuenta_id):
    # Desactivar todas las cuentas
    CuentaPago.query.update({CuentaPago.activo: False})

    # Activar la cuenta seleccionada
    cuenta = CuentaPago.query.get(cuenta_id)
    if cuenta:
        cuenta.activo = True
        db.session.commit()
        flash(f"✅ {cuenta.nombre} ahora es la cuenta activa.", "success")
    else:
        flash("❌ No se encontró la cuenta seleccionada.", "error")

    return redirect(url_for("admin_dashboard"))

@app.route("/admin/cuentas/editar/<int:cuenta_id>", methods=["GET"])
@login_required
def editar_cuenta(cuenta_id):
    cuenta = CuentaPago.query.get_or_404(cuenta_id)
    return render_template("editar_cuenta.html", cuenta=cuenta)

@app.route("/admin/agregar_cuenta", methods=["POST"])
@login_required
def agregar_cuenta():
    nombre = request.form.get("nombre")
    banco = request.form.get("banco")
    alias = request.form.get("alias")
    cbu = request.form.get("cbu")
    email = request.form.get("email")
    public_key = request.form.get("public_key")
    access_token = request.form.get("access_token")

    nueva_cuenta = CuentaPago(
        nombre=nombre,
        banco=banco,
        alias=alias,
        cbu=cbu,
        email=email,
        public_key=public_key,
        access_token=access_token,
        activo=False
    )

    db.session.add(nueva_cuenta)
    db.session.commit()

    flash(f"Cuenta '{nombre}' agregada correctamente.", "success")
    return redirect(url_for("admin_dashboard"))

@app.route("/cuentas")
@login_required
def obtener_cuentas():
    cuentas = CuentaPago.query.all()
    activa = CuentaPago.query.filter_by(activo=True).first()
    return jsonify({
        "cuentas": [c.to_dict() for c in cuentas],
        "activa": activa.to_dict() if activa else None
    })

@app.route("/cuentas/activar/<int:cuenta_id>", methods=["POST"])
@login_required
def activar_cuenta(cuenta_id):
    # Desactivar todas
    CuentaPago.query.update({CuentaPago.activo: False})
    # Activar la elegida
    cuenta = CuentaPago.query.get_or_404(cuenta_id)
    cuenta.activo = True
    db.session.commit()
    return jsonify({"message": f"Cuenta '{cuenta.nombre}' activada correctamente"})

@app.route("/admin/cuentas/editar/<int:cuenta_id>", methods=["POST"])
@login_required
def guardar_edicion_cuenta(cuenta_id):
    cuenta = CuentaPago.query.get_or_404(cuenta_id)

    cuenta.nombre = request.form.get("nombre")
    cuenta.banco = request.form.get("banco")
    cuenta.alias = request.form.get("alias")
    cuenta.cbu = request.form.get("cbu")
    cuenta.email = request.form.get("email")
    cuenta.public_key = request.form.get("public_key")
    cuenta.access_token = request.form.get("access_token")

    db.session.commit()

    flash("Cuenta actualizada correctamente", "success")
    return redirect(url_for("admin_dashboard"))

@app.route("/admin/cuentas/eliminar/<int:cuenta_id>", methods=["POST"])
@login_required
def eliminar_cuenta(cuenta_id):
    cuenta = CuentaPago.query.get_or_404(cuenta_id)

    db.session.delete(cuenta)
    db.session.commit()

    flash("Cuenta eliminada correctamente", "success")
    return redirect(url_for("admin_dashboard"))

# ---------------------------------------------------
# RUTAS DE CHECKOUT Y WEBHOOKS
# ---------------------------------------------------

@app.route("/checkout/success")
def checkout_success():
    flash("Pago aprobado correctamente", "success")
    return redirect(url_for("shop"))

@app.route("/checkout/failure")
def checkout_failure():
    flash("El pago fue rechazado", "error")
    return redirect(url_for("shop"))

@app.route("/checkout/pending")
def checkout_pending():
    flash("El pago quedó pendiente", "warning")
    return redirect(url_for("shop"))

@app.route("/webhook/mp", methods=["POST"])
def mp_webhook():
    data = request.json
    print("WEBHOOK MP:", data)
    return "OK", 200

# ---------------------------------------------------
# EJECUCIÓN DE LA APLICACIÓN
# ---------------------------------------------------

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
