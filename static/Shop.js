const CART_TTL = 2 * 60 * 60 * 1000;
 
function mostrarToastExpiracion() {
  if (document.getElementById("cartExpiredToast")) return;
 
  const toast = document.createElement("div");
  toast.id = "cartExpiredToast";
  toast.style.cssText = `
    position: fixed;
    bottom: 24px;
    left: 50%;
    transform: translateX(-50%);
    background: #1f2937;
    color: white;
    font-size: 14px;
    padding: 12px 20px;
    border-radius: 12px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.2);
    z-index: 9999;
    display: flex;
    align-items: center;
    gap: 8px;
    opacity: 1;
    transition: opacity 0.5s ease;
  `;
  toast.innerHTML = `<i class="fas fa-clock"></i> Tu carrito expiró y fue vaciado automáticamente.`;
  document.body.appendChild(toast);
 
  setTimeout(() => {
    toast.style.opacity = "0";
    setTimeout(() => toast.remove(), 500);
  }, 4000);
}

// Inicializar carrito desde localStorage, descartando formato viejo o mezclado
function cargarCarrito(key) {
  const raw = JSON.parse(localStorage.getItem(key)) || [];
  const esFormatoViejo = raw.some(item => item.priceARS === undefined);
  if (esFormatoViejo) {
    localStorage.removeItem(key);
    return [];
  }
  return raw;
}

// Inicializar carrito desde localStorage
let cart = JSON.parse(localStorage.getItem("cart_principal")) || [];
let cartRepuestos = JSON.parse(localStorage.getItem("cart_repuestos")) || [];


// 🖼️ Renderizar productos en la tienda
function renderProducts(products) {
  const container = document.getElementById("productGrid");
  container.innerHTML = "";

  if (!products || products.length === 0) {
    container.innerHTML = `<p class="text-center text-gray-500">No hay productos disponibles.</p>`;
    return;
  }

  products.forEach(p => {
    const priceARS = p.precio_lista;

    container.innerHTML += `
      <div class="border rounded-lg p-4 shadow hover:shadow-lg transition bg-white">
        <div class="gallery flex justify-center mb-4">
          <img src="/static/uploads/${p.imagenes?.[0]|| 'images/no-image.png'}"
               alt="${p.nombre}"
               class="w-48 h-48 object-cover rounded shadow">
        </div>

        <h3 class="text-lg font-semibold text-gray-900">${p.nombre}</h3>
        <p class="text-gray-600 text-sm h-12 overflow-hidden line-clamp-2">${p.descripcion}</p>

        <div class="mt-3">
          <p class="text-xl font-bold text-indigo-600">
            $${priceARS.toLocaleString("es-AR")}ARS 
            <span class="text-gray-500 text-sm">(USD ${priceARS.toLocaleString("es-AR")})</span>
          </p>
        </div>

        <a href="/product/${p.id}" 
           class="inline-block mt-4 bg-indigo-600 text-white py-2 px-4 rounded hover:bg-indigo-700 transition">
           Ver detalles
        </a>
      </div>
    `;
  });
}


async function showDolarInAdmin() {
  document.getElementById("dolarValue").textContent = `$${dolarBlue.toFixed(2)} ARS`;
}

// Agregar producto al carrito
function addToCart(button) {
  const id = parseInt(button.dataset.id);
  const name = button.dataset.name;
  const priceARS = parseFloat(button.dataset.priceArs);
  const stock = parseInt(button.dataset.stock);

  let qtyInput = document.getElementById(`qty-${id}`);
  let qty = qtyInput ? parseInt(qtyInput.value) || 1 : 1;

  let existing = cart.find(p => p.id === id);

  if (existing) {
    if (existing.quantity + qty > stock) {
      alert("No hay suficiente stock disponible");
      return;
    }
    existing.quantity += qty;
  } else {
    if (qty > stock) {
      alert("Cantidad supera el stock disponible");
      return;
    }

    cart.push({
      id,
      name,
      priceARS,
      quantity: qty,
      stock // 🔐 guardar stock en el item
    });
  }

  localStorage.setItem("cart_principal", JSON.stringify(cart));
  updateCart();
}


// 🧺 Mostrar u ocultar el modal del carrito
function toggleCart() {
  const cartModal = document.getElementById("cartModal");
  if (cartModal) cartModal.classList.toggle("hidden");
}

// 🧮 Actualizar carrito visual
function updateCart() {
  cart = JSON.parse(localStorage.getItem("cart_principal")) || [];

  const cartCount = document.getElementById("cartCount");
  const cartItemsContainer = document.getElementById("cartItems");
  if (!cartItemsContainer) return;

  if (cartCount) {
    cartCount.textContent = cart.reduce((t, item) => t + item.quantity, 0);
  }

  cartItemsContainer.innerHTML = "";

  if (cart.length === 0) {
    cartItemsContainer.innerHTML = `
      <li class="py-6 flex justify-center text-gray-500">Tu carrito está vacío</li>`;
    document.getElementById("cartSubtotal").textContent = "$0.00";
    document.getElementById("cartTotal").textContent = "$0.00";
    return;
  }

  let subtotal = 0;

  cart.forEach(item => {

    const itemTotal = item.priceARS * item.quantity;
    subtotal += itemTotal;

    const li = document.createElement("li");
    li.className = "py-3 flex items-center justify-between border-b hover:bg-gray-50 transition-colors duration-200 rounded-md px-2";
    
    li.innerHTML = `
      <div class="flex items-center gap-4 w-full">
        <div class="flex-1">
          <p class="font-semibold text-gray-800">${item.name}</p>
          <p class="text-sm text-gray-500">
            Precio unitario:
            <span class="font-medium text-gray-700">
              $${item.priceARS.toLocaleString("es-AR")} ARS
            </span>
          </p>
          <div class="flex items-center gap-2 mt-1">
            <label class="text-sm text-gray-600">Cantidad:</label>
            <input type="number"
                  min="1"
                  value="${item.quantity}"
                  class="w-14 text-center border border-gray-300 rounded-md"
                  onchange="updateQuantity(${item.id}, this.value)">
          </div>
        </div>
        <div class="text-right">
          <p class="font-bold text-indigo-600 text-lg">
            $${itemTotal.toLocaleString("es-AR")} ARS
          </p>
          <button onclick="removeFromCart(${item.id})"
                  class="text-red-500 hover:text-red-700 mt-1 text-sm">
            🗑 Quitar
          </button>
        </div>
      </div>
    `;

  cartItemsContainer.appendChild(li);
  });

  document.getElementById("cartSubtotal").textContent = `$${subtotal.toLocaleString("es-AR")} ARS`;
  document.getElementById("cartTotal").textContent = `$${subtotal.toLocaleString("es-AR")} ARS`;

  // 🔄 Guardar el carrito actualizado (por si había items viejos sin priceARS)
  localStorage.setItem("cart_principal", JSON.stringify(cart));
}
// 🔢 Cambiar cantidad
function updateQuantity(productId, newQuantity) {
  const item = cart.find(p => p.id === productId);
  if (!item) return;

  let qty = parseInt(newQuantity) || 1;

  if (qty > item.stock) {
    alert("Stock máximo alcanzado");
    qty = item.stock;
  }

  if (qty < 1) {
    cart = cart.filter(p => p.id !== productId);
  } else {
    item.quantity = qty;
  }

  localStorage.setItem("cart_principal", JSON.stringify(cart));
  updateCart();
}

// ❌ Eliminar producto
function removeFromCart(productId) {
  cart = cart.filter(p => p.id !== productId);
  localStorage.setItem("cart_principal", JSON.stringify(cart));
  updateCart();
}

// 💰 Actualizar totales (checkout)
function updateTotals() {
  const subtotal = cart.reduce((s, item) => s + item.priceUSD * dolarManual * item.quantity,0 );
  const subtotalEl = document.getElementById("subtotal");
  const totalEl = document.getElementById("total");

  if (subtotalEl) subtotalEl.textContent = `$${subtotal.toLocaleString("es-AR")} ARS`;
  if (totalEl) totalEl.textContent = `$${subtotal.toLocaleString("es-AR")} ARS`;
}


document.addEventListener("DOMContentLoaded", () => {
  const qtyInput = document.querySelector('[id^="qty-"]');
  if (!qtyInput) return;

  const maxStock = parseInt(qtyInput.max);

  qtyInput.addEventListener("input", () => {
    let value = parseInt(qtyInput.value) || 1;

    if (value > maxStock) {
      qtyInput.value = maxStock;
      alert("No hay más stock disponible");
    }

    if (value < 1) {
      qtyInput.value = 1;
    }
  });
});

// Inicializar cuando cargue la página
document.addEventListener("DOMContentLoaded", updateCart, showDolarInAdmin);

