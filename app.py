import os
from flask import Flask, render_template, request, redirect, url_for, flash, session, g, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from models import *
from helpers import login_required
from werkzeug.utils import secure_filename
from functools import wraps
from flask import abort
from flask_migrate import Migrate
# from flask_migrate import Migrate
from mercadopago import SDK
import secrets
from datetime import datetime, timedelta
from flask import request, url_for, redirect, render_template
from flask_mail import Mail, Message
from datetime import datetime
import pytz
from uuid import uuid4
import cloudinary
import cloudinary.uploader
import cloudinary.api
from dotenv import load_dotenv


# ---------------------------------------------------
# CONFIGURACIÓN DE FLASK
# ---------------------------------------------------
app = Flask(__name__)
app.secret_key = "NewImage2025"
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

ALLOWED_HOSTS = [
    "newimagepilates.com",
    "www.newimagepilates.com",
    "newimage-9i3u.onrender.com",
]

db.init_app(app)

migrate = Migrate(app, db)

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv("MAIL_USERNAME")  # tu gmail
app.config['MAIL_PASSWORD'] = os.getenv("MAIL_PASSWORD")  # app password
app.config['MAIL_DEFAULT_SENDER'] = os.getenv("MAIL_USERNAME")

mail = Mail(app)


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

@app.after_request
def agregar_headers_no_cache(response):
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

def ahora_arg():
    return datetime.now(pytz.timezone("America/Argentina/Buenos_Aires"))

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
    config = (
        Configuracion.query
        .execution_options(populate_existing=True)
        .first()
    )
    if not config:
        config = Configuracion(dolar_manual=1450, ventas_activas=True)
        db.session.add(config)
        db.session.commit()
    return config.dolar_manual

@app.route('/update_dolar', methods=['POST'])
@login_required
def update_dolar():
    nuevo_valor = request.form.get("dolar_manual")

    if not nuevo_valor:
        flash("Debes ingresar un valor.", "error")
        return redirect(url_for('admin_dashboard'))

    config = (
        Configuracion.query
        .execution_options(populate_existing=True)
        .first()
    )

    if not config:
        config = Configuracion(dolar_manual=float(nuevo_valor), ventas_activas=True)
        db.session.add(config)
    else:
        config.dolar_manual = float(nuevo_valor)

    db.session.commit()

    # 🔥 Fuerza a leer desde la DB, NO desde caché
    db.session.refresh(config)

    flash("Valor del dólar actualizado correctamente.", "success")
    return redirect(url_for('admin_dashboard'))



def serializar_producto(product):
    return {
        "id": product.id,
        "nombre": product.nombre,
        "precio": product.precio,
        "descripcion": product.descripcion,
        "stock": product.stock,
        "observacion": product.observacion,
        "imagenes": [
            img.filename for img in product.imagenes
        ]
    }

def send_email(to, link):
    print(f"Enviar email a {to} con link: {link}")


load_dotenv()

cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
    secure=True
)

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
            return redirect(url_for("login"))

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

@app.route("/historial_ventas")
@admin_required
def historial_ventas():
    ventas = Venta.query.order_by(Venta.fecha.desc()).all()
    zona_ar = pytz.timezone("America/Argentina/Buenos_Aires")

    for v in ventas:
        if v.fecha:
            # Si viene en UTC
            v.fecha = v.fecha.replace(tzinfo=pytz.utc).astimezone(zona_ar)

    return render_template("historial_ventas.html", ventas=ventas)
# ---------------------------------------------------
# RUTAS DE CHECKOUT Y SESIÓN
# ---------------------------------------------------

# Ruta checkout
@app.route("/check")
@login_required
def check():
    cuenta = get_cuenta_activa()
    print("DEBUG cuenta:", cuenta)
    print("DEBUG cuentas:", CuentaPago.query.all())
    print("DEBUG activa:", get_cuenta_activa())

    # if not cuenta:
    #     return "No hay cuenta activa configurada en la base de datos", 500

    return render_template("CheckOut.html", cuenta=cuenta, public_key=cuenta.public_key)

# Logout
@app.route("/logout", methods=["POST"])
def logout():
    session.pop("user_id", None)
    session.pop("username", None)
    return redirect(url_for("index"))

@app.route('/contraseña_olvidada', methods=['GET', 'POST'])
def contraseña_olvidada():
    if request.method == 'POST':
        email = request.form['email']

        user = User.query.filter_by(email=email).first()
        if not user:
            flash("Si el email existe, recibirás un correo", "info")
            return redirect(url_for('contraseña_olvidada'))

        token = secrets.token_urlsafe(32)

        reset = PasswordReset(
            email=email,
            token=token,
            expires_at=datetime.utcnow() + timedelta(hours=1)
        )

        db.session.add(reset)
        db.session.commit()

        link = url_for('reset_password', token=token, _external=True)
        send_email(email, link)

        flash("Revisá tu email para restablecer la contraseña", "success")
        return redirect(url_for('login'))

    return render_template('contraseña_olvidada.html')

@app.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    reset = PasswordReset.query.filter_by(token=token).first_or_404()

    if reset.expires_at < datetime.utcnow():
        flash("Token expirado", "danger")
        return redirect(url_for('forgot_password'))

    if request.method == 'POST':
        user = User.query.filter_by(email=reset.email).first()
        user.set_password(request.form['password'])

        db.session.delete(reset)
        db.session.commit()

        flash("Contraseña actualizada", "success")
        return redirect(url_for('login'))

    return render_template('reset_password.html')

def send_email(to, link):
    msg = Message(
        subject="Restablecer contraseña",
        recipients=[to]
    )

    msg.html = f"""
    <div style="font-family: Arial, Helvetica, sans-serif; max-width: 600px; margin: auto; color: #333;">
        <h2 style="color: #1f2937;">Restablecimiento de contraseña</h2>

        <p>Hola,</p>

        <p>
            Recibimos una solicitud para restablecer la contraseña de tu cuenta en 
            <strong>NewImage</strong>, fabricantes de equipamiento profesional para Pilates.
        </p>

        <p>
            Para crear una nueva contraseña, hacé clic en el siguiente botón:
        </p>

        <p style="text-align: center; margin: 30px 0;">
            <a href="{link}"
            style="
                    background-color: #4f46e5;
                    color: #ffffff;
                    padding: 12px 24px;
                    text-decoration: none;
                    border-radius: 6px;
                    font-weight: bold;
            ">
            Restablecer contraseña
            </a>
        </p>

        <p>
            Este enlace es válido por <strong>1 hora</strong>.  
            Si no realizás el cambio dentro de ese tiempo, deberás solicitar uno nuevo.
        </p>

        <hr style="margin: 30px 0;">

        <p style="font-size: 12px; color: #6b7280;">
            © {datetime.utcnow().year} NewImage · Equipamiento profesional para Pilates<br>
            Este es un mensaje automático, por favor no respondas a este correo.
        </p>
    </div>
    """

    mail.send(msg)

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
    if config:
        db.session.refresh(config)   # ← Fuerza a recargar desde la DB

    ventas_activas = config.ventas_activas if config else True
    dolar = config.dolar_manual if config else 1450

    if filtro == "principal":
        productos = Product.query.filter_by(tipo="principal").all()
    elif filtro == "repuesto":
        productos = Product.query.filter_by(tipo="repuesto").all()
    else:
        productos = Product.query.all()

    return render_template(
        "admin_dashboard.html",
        cuentas=cuentas,
        products=productos,
        filtro=filtro,
        dolar=dolar,
        ventas_activas=ventas_activas
    )
@app.route("/admin_cuentas")
@admin_required
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
            if allowed_file(file.filename):
                ext = file.filename.rsplit(".", 1)[1].lower()
                unique_name = f"{uuid4().hex}.{ext}"

                if product.tipo == "repuesto":
                    subfolder = "uploads/repuestos"
                else:
                    subfolder = "uploads"

                upload_path = os.path.join("static", subfolder)
                os.makedirs(upload_path, exist_ok=True)
                
                upload = cloudinary.uploader.upload(
                    file,
                    folder=f"newimage/{product.tipo}"
                )

                new_image = ProductImage(
                    filename=upload["secure_url"],  # URL completa
                    product_id=product.id
                )
                
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
                    ext = file.filename.rsplit(".", 1)[1].lower()
                    unique_name = f"{uuid4().hex}.{ext}"

                    if product.tipo == "repuesto":
                        subfolder = "uploads/repuestos"
                    else:
                        subfolder = "uploads"

                    upload_path = os.path.join("static", subfolder)
                    os.makedirs(upload_path, exist_ok=True)
                    
                    upload = cloudinary.uploader.upload(
                        file,
                        folder=f"newimage/{product.tipo}"
                    )

                    new_image = ProductImage(
                        filename=upload["secure_url"],  # URL completa
                        product_id=product.id
                    )
                    
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
    data = request.json
    cart = data.get("cart", [])
    cuenta_id = data.get("cuenta_id")
    
    cuenta = CuentaPago.query.get(cuenta_id) if cuenta_id else None
    
    if not cart:
        return {"error": "El carrito está vacío"}, 400

    total = 0
    items_validos = []
    
    dolar = obtener_dolar_manual()

    for item in cart:
        product = Product.query.get(item["id"])

        if not product:
            return {"error": "Producto inexistente"}, 400
        
        cantidad = int(item.get("quantity", 1))

        if product.stock < cantidad:
            return {"error": f"Stock insuficiente para {product.nombre}"}, 400

        precio_ars = product.precio * dolar
        subtotal = precio_ars * cantidad
        total += subtotal

        items_validos.append({
            "product": product,
            "cantidad": cantidad,                
            "precio": precio_ars
        })

    venta = Venta(
        comprador_nombre=data.get("comprador_nombre"),
        comprador_telefono=data.get("telefono"),
        comprador_email=data.get("email"),
        metodo_pago="transferencia",
        cuenta_destino=cuenta.alias if cuenta else None,
        monto_total=total,
        estado="pendiente"
    )

    db.session.add(venta)
    db.session.commit()

    for i in items_validos:
        db.session.add(VentaItem(
            venta_id=venta.id,
            producto_nombre=i["product"].nombre,
            cantidad=i["cantidad"],
            precio_unitario=i["precio"]
        ))

    db.session.commit()

    return {
        "success": True,
        "order_id": venta.id,
        "total": total,
        "items": [
            {
                "nombre": i["product"].nombre,
                "cantidad": i["cantidad"],
                "precio_unitario": i["precio"],
                "subtotal": i["precio"] * i["cantidad"]
            }
            for i in items_validos
        ]
    }, 201
        

@app.route("/ventas/<int:id>/confirmar", methods=["POST"])
@login_required
def confirmar_transferencia(id):
    venta = Venta.query.get_or_404(id)

    if venta.estado == "pagado":
        return {"error": "Venta ya confirmada"}, 400

    for item in venta.items:
        product = Product.query.filter_by(nombre=item.producto_nombre).first()

        if not product:
            return {"error": f"{item.producto_nombre} no existe"}, 400

        if product.stock < item.cantidad:
            return {"error": f"Stock insuficiente para {product.nombre}"}, 400

    for item in venta.items:
        product = Product.query.filter_by(nombre=item.producto_nombre).first()
        product.stock -= item.cantidad
        product.en_stock = product.stock > 0

    venta.estado = "pagado"
    db.session.commit()

    return {"success": True}

@app.route("/crear_pago", methods=["POST"])
def crear_pago():
    try:
        cuenta = get_cuenta_activa()
        if not cuenta or not cuenta.access_token:
            return jsonify({"error": "No hay cuenta activa configurada"}), 400

        data = request.get_json()
        cart = data.get("cart", [])
        email = data.get("email")

        if not cart:
            return jsonify({"error": "El carrito está vacío"}), 400

        dolar = obtener_dolar_manual()
        items_mp = []
        total = 0
        items_validos = []

        for item in cart:
            product = Product.query.get(item["id"])
            cantidad = int(item.get("quantity", 1))

            if not product:
                return jsonify({"error": "Producto inexistente"}), 400

            if product.stock < cantidad:
                return jsonify({"error": f"Stock insuficiente para {product.nombre}"}), 400

            precio_ars = product.precio * dolar
            total += precio_ars * cantidad

            items_mp.append({
                "title": product.nombre,
                "quantity": cantidad,
                "currency_id": "ARS",
                "unit_price": float(precio_ars)
            })

            items_validos.append((product, cantidad, precio_ars))

        sdk = SDK(cuenta.access_token)

        preference_data = {
            "items": items_mp,
            "payer": {"email": email},
            "external_reference": str(venta.id),
            "back_urls": {
                "success": url_for("pago_exitoso", _external=True),
                "failure": url_for("pago_fallido", _external=True),
                "pending": url_for("pago_pendiente", _external=True)
            },
            "auto_return": "approved"
        }

        preference = sdk.preference().create(preference_data)

        venta = Venta(
            comprador_nombre=data.get("comprador_nombre"),
            comprador_telefono=data.get("telefono"),
            comprador_email=email,
            metodo_pago="mercado_pago",
            cuenta_destino=cuenta.alias or cuenta.cbu,
            monto_total=total
        )

        db.session.add(venta)
        db.session.commit()

        for product, cantidad, precio in items_validos:
            db.session.add(VentaItem(
                venta_id=venta.id,
                producto_nombre=product.nombre,
                cantidad=cantidad,
                precio_unitario=precio
            ))

        db.session.commit()

        return jsonify(preference["response"])

    except Exception as e:
        print("🔥 ERROR crear_pago:", e)
        return jsonify({"error": str(e)}), 500





@app.route('/pago_exitoso')
def pago_exitoso():
    venta_id = request.args.get("external_reference")
    venta = Venta.query.get(venta_id)

    if venta and venta.estado != "pagado":
        for item in venta.items:
            product = Product.query.filter_by(nombre=item.producto_nombre).first()
            product.stock -= item.cantidad
            product.en_stock = product.stock > 0

        venta.estado = "pagado"
        db.session.commit()

    return render_template("pago_exitoso.html")

@app.route('/pago_pendiente')
def pago_pendiente():
    return render_template("pago_pendiente.html")

@app.route('/pago_fallido')
def pago_fallido():
    return render_template("pago_fallido.html")


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
    cuenta.public_key = request.form.get("public_key").strip()
    cuenta.access_token = request.form.get("access_token").strip()
    
    print("PUBLIC_KEY RECIBIDA:", request.form.get("public_key"))
    print("ACCESS_TOKEN RECIBIDO:", request.form.get("access_token"))

    print("PUBLIC_KEY GUARDADA:", cuenta.public_key)
    print("ACCESS_TOKEN GUARDADO:", cuenta.access_token)
    
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
