import requests
from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, url_for, flash, session, g
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Product, Order, OrderItem, ProductImage
from app import db
from helpers import login_required
import os
from werkzeug.utils import secure_filename
from functools import wraps
from flask import abort
from flask_migrate import Migrate

app = Flask(__name__)
app.secret_key = "NewImage" 
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///tienda.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
migrate = Migrate(app, db)

db.init_app(app)

# Crea tablas
with app.app_context():
    db.create_all()

#Ruta Index
@app.route("/")
def index():
    user = None
    if "user_id" in session:
        user = User.query.get(session["user_id"]) # Recupera el usuario logueado
    return render_template("index.html", user=user)

#Ruta Login
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


# Funcion de dolar
# --- Obtener Dólar Blue con cache simple ---
DOLAR_CACHE = {
    "value": None,
    "fetched_at": None
}
DOLAR_TTL = timedelta(minutes=60)   # cache por 60 minutos
DEFAULT_DOLAR = 1450                # fallback si la API falla

def obtener_dolar_blue():
    """Devuelve el valor promedio del dólar blue.
       Usa cache en memoria (TTL). Si falla, devuelve DEFAULT_DOLAR.
    """
    now = datetime.utcnow()

    # si hay valor en cache y no expiró, retornarlo
    if DOLAR_CACHE["value"] is not None and DOLAR_CACHE["fetched_at"] is not None:
        if now - DOLAR_CACHE["fetched_at"] < DOLAR_TTL:
            return DOLAR_CACHE["value"]

    # intentar pedir a la API
    try:
        res = requests.get("https://api.bluelytics.com.ar/v2/latest", timeout=5)
        res.raise_for_status()
        data = res.json()
        # la estructura típica: data["blue"]["value_avg"]
        valor = None
        if isinstance(data, dict):
            # varios posibles campos; priorizamos value_avg si existe
            blue = data.get("blue") or {}
            valor = blue.get("value_avg") or blue.get("value") or blue.get("value_sell") or None

        if valor is None:
            raise ValueError("Respuesta inesperada de Bluelytics")

        # cachear y devolver
        DOLAR_CACHE["value"] = float(valor)
        DOLAR_CACHE["fetched_at"] = now
        return DOLAR_CACHE["value"]

    except Exception as e:
        # loguear error en consola para debug
        print("Error al obtener dólar blue:", e)
        # si hay valor cacheado devolverlo, sino fallback
        if DOLAR_CACHE["value"] is not None:
            return DOLAR_CACHE["value"]
        return DEFAULT_DOLAR

@app.template_filter("ars")
def usd_a_pesos(value):
    try:
        dolar = obtener_dolar_blue()
        valor_en_pesos = value * dolar
        return f"${valor_en_pesos:,.0f} ARS"
    except Exception as e:
        print("Errpr al convertir a ARS:", e)
        return f"USD {value:.2f}"

# Ruta tienda (protegida, requiere login)
@app.route("/shop")

def shop():
    dolar_blue = obtener_dolar_blue()
    if "user_id" not in session:
        return redirect(url_for("login"))
    products = Product.query.filter_by(tipo="principal").all()
    for p in products:
        # si p.precio está en USD:
        p.precio_pesos = round((p.precio or 0) * dolar_blue, 2)
    print(products)
    return render_template("Shop.html", products=products, dolar_blue=dolar_blue)




# Ruta de los repuestos
@app.route("/repuestos")

def repuestos():
    dolar_blue = obtener_dolar_blue()
    productos  = Product.query.filter_by(tipo="repuesto").all()
    for p in productos:
        # si p.precio está en USD:
        p.precio_pesos = round((p.precio or 0) * dolar_blue, 2)
    print("Productos repuestos:", [p.nombre for p in productos])
    return render_template("repuestos.html", products=productos, dolar_blue=dolar_blue)





# Ruta checkout
@app.route("/check")
@login_required
def check():
    return render_template("CheckOut.html")



@app.route("/checkout_repuestos")
def checkout_repuestos():
    return render_template("checkout_repuestos.html")

# Logout
@app.route("/logout", methods=["POST"])
def logout():
    session.pop("user_id", None)
    session.pop("username", None)
    return redirect(url_for("index"))


#Ruta de perfiles
@app.route("/profile")
@login_required
def profile():
    user = User.query.get(session["user_id"])
    return render_template("profile.html", user=user)

#Ruta de admin
@app.route("/admin")
@admin_required
def admin_dashboard():
    filtro = request.args.get("filtro", "todo")
    
    if filtro == "principal":
        productos = Product.query.filter_by(tipo="principal").all()
    elif filtro == "repuesto":
        productos = Product.query.filter_by(tipo="repuesto").all()
    else: 
        productos = Product.query.all()
        
    return render_template("admin_dashboard.html", products=productos, filtro=filtro)


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



#----------------------------------------------------------------------------
# Carpeta donde se guardarán las imágenes
UPLOAD_FOLDER = os.path.join("static", "uploads")
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # Crea la carpeta si no existe

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


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

        product = Product(
            nombre=nombre,
            categoria=categoria,
            precio=precio,
            descripcion=descripcion,
            en_stock=(stock > 0),
            stock=stock,
            tipo=tipo
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

#Editar un producto
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
        product.tipo = request.form.get("tipo", "principal")  # nuevo campo “tipo”

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


#Eliminar un producto
@app.route("/product/delete/<int:product_id>", methods=["POST"])
@admin_required
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    flash("Producto eliminado con éxito", "success")
    return redirect(url_for("admin_dashboard"))

#----------------------------------------------------------------------------

@app.route("/checkout", methods=["POST"])
@login_required
def checkout():
    cart = request.json.get("cart", [])  # Recibimos carrito desde frontend

    if not cart:
        return {"error": "El carrito está vacío"}, 400

    # Calcular total
    total = sum(item["price"] * item["quantity"] for item in cart)

    # Crear orden
    order = Order(user_id=session["user_id"], total=total)
    db.session.add(order)
    db.session.commit()

    # Guardar items
    for item in cart:
        order_item = OrderItem(
            order_id=order.id,
            product_id=item["id"],
            quantity=item["quantity"],
            price=item["price"]
        )
        db.session.add(order_item)

    db.session.commit()

    return {"message": "Compra realizada con éxito", "order_id": order.id}, 201

# Página de detalle de un producto
@app.route("/product/<int:product_id>")
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)
    return render_template("product_detail.html", product=product)
    
    

if __name__ == "__main__":
    app.run(debug=True)
    