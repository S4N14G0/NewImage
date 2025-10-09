
// Inicializar carrito desde localStorage
let cart = JSON.parse(localStorage.getItem("cart_principal")) || [];
let cartRepuestos = JSON.parse(localStorage.getItem("cart_repuestos")) || [];

// Valor por defecto
let dolarBlue = 1450;

// Obtener cotización del dólar blue desde Bluelytics
async function fetchDolarBlue() {
    try{
        const res = await fetch("https://api.bluelytics.com.ar/v2/latest");
        const data = await res.json();
        dolarBlue = data.blue.value_avg;
        console.log("💵 Cotización actual del dólar blue:", dolarBlue);
    } catch (err) {
        console.error("No se pudo obtener la cotizacion del dolar", err)
    }
}

// Renderizar productos (convierte USD a ARS)
async function renderProducts(products) {
    await fetchDolarBlue();
    
    const container = document.getElementById("productGrid");
    container.innerHTML = "";


    products.forEach(p => {
        const priceARS = (p.precio * dolarBlue).toFixed(0);
    
    
    container.innerHTML += ` 
      <div class="border rounded-lg p-4 shadow hover:shadow-lg transition">
        <div class="gallery flex justify-center mb-4">
          <img src="/static/uploads/${p.imagenes?.[0]?.filename || 'no-image.png'}"
               alt="${p.nombre}"
               class="w-48 h-48 object-cover rounded shadow">
        </div>
        <h3 class="text-lg font-semibold">${p.nombre}</h3>
        <p class="text-gray-600 truncate">${p.descripcion}</p>
        <p class="text-xl font-bold mt-2">$${priceARS} ARS 
          <span class="text-gray-500 text-sm">(USD ${p.precio})</span>
        </p>
        <a href="/product/${p.id}" 
           class="text-indigo-600 hover:underline mt-2 inline-block">Ver detalles</a>
      </div>
    `;
  });
}

// Refrescar el valor del dólar cada hora
setInterval(fetchDolarBlue, 3600000); 

async function showDolarInAdmin() {
  await fetchDolarBlue();
  document.getElementById("dolarValue").textContent = `$${dolarBlue.toFixed(2)} ARS`;
}

// Agregar producto al carrito
function addToCart(button) {

    const id = parseInt(button.dataset.id);
    const name = button.dataset.name;
    const price = parseFloat(button.dataset.price);

    // Buscar input asociado al producto
    let qtyInput = document.getElementById(`qty-${id}`);
    let qty = qtyInput ? parseInt(qtyInput.value) || 1 : 1;

    let existing = cart.find(p => p.id === id);
    if (existing) {
        existing.quantity += qty;
    } else {
        cart.push({ id, name, price, quantity: qty });
    }

    localStorage.setItem("cart_principal", JSON.stringify(cart));
    updateCart();
}

//Mostar carrito
function toggleCart() {
  const cartModal = document.getElementById('cartModal');
  if (cartModal) {
    cartModal.classList.toggle('hidden');
  }
}

// Actualizar carrito
function updateCart() {
    const cartCount = document.getElementById("cartCount");
    if (cartCount) {
        cartCount.textContent = cart.reduce((t, item) => t + item.quantity, 0);
    }
    const cartItemsContainer = document.getElementById("cartItems");

    if (!cartItemsContainer) return;

    cartItemsContainer.innerHTML = ""; // Limpiar contenido previo

    if (cart.length === 0) {
        // Mostrar mensaje carrito vacío
        const emptyLi = document.createElement("li");
        emptyLi.className = "py-6 flex justify-center";
        emptyLi.innerHTML = `<p class="text-gray-500">Tu carrito está vacío</p>`;
        cartItemsContainer.appendChild(emptyLi);

        // Actualizar totales a cero
        document.getElementById("cartSubtotal").textContent = "$0.00";
        document.getElementById("cartTotal").textContent = "$0.00";
        return;
    }

    // Si hay productos, agregarlos al carrito
    let subtotal = 0;

    cart.forEach(item => {
        const li = document.createElement("li");
        li.className = "py-2 flex justify-between items-center border-b";

        const itemTotal = item.price * item.quantity;
        subtotal += itemTotal;

        li.innerHTML = `
            <div>
                <p class="font-semibold">${item.name}</p>
                <div class="text-sm text-gray-500">
                    $${item.price.toFixed(2)} x 
                    <input type="number" min="1" value="${item.quantity}" 
                        class="w-12 border rounded text-center" 
                        onchange="updateQuantity(${item.id}, this.value)">
                </div>
            </div>
            <div class="flex items-center gap-2">
                <span class="font-bold">$${(item.price * item.quantity).toFixed(2)}</span>
                <button onclick="removeFromCart(${item.id})" class="text-red-500 hover:text-red-700">❌</button>
            </div>
        `;

        cartItemsContainer.appendChild(li);
    });

    // Actualizar subtotal y total (envío calculado después)
    document.getElementById("cartSubtotal").textContent = `$${subtotal.toFixed(2)}`;
    document.getElementById("cartTotal").textContent = `$${subtotal.toFixed(2)}`;
}

// Cambiar cantidad de un producto
function updateQuantity(productId, newQuantity) {
    const item = cart.find(p => p.id === productId);
    if (item) {
        item.quantity = parseInt(newQuantity);
        if (item.quantity <= 0) {
            cart = cart.filter(p => p.id !== productId);
        }
        localStorage.setItem("cart_principal", JSON.stringify(cart));
        updateCart();
    }
}

// Eliminar producto
function removeFromCart(productId) {
    cart = cart.filter(p => p.id !== productId);
    localStorage.setItem("cart_principal", JSON.stringify(cart));
    updateCart();
}

// Actualizar totales
function updateTotals() {
    const subtotal = cart.reduce((s, item) => s + item.price * item.quantity, 0);
    const subtotalEl = document.getElementById("subtotal");
    const totalEl = document.getElementById("total");

    if (subtotalEl) subtotalEl.textContent = `$${subtotal.toFixed(2)}`;
    if (totalEl) totalEl.textContent = `$${subtotal.toFixed(2)}`;
}





// Inicializar cuando cargue la página
document.addEventListener("DOMContentLoaded", updateCart, showDolarInAdmin);
