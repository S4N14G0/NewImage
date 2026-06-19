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


function cargarCarrito(key) {
  const raw = JSON.parse(localStorage.getItem(key)) || [];
  const esFormatoViejo = raw.some(item => item.priceARS === undefined);
  if (esFormatoViejo) {
    localStorage.removeItem(key);
    return [];
  }
  return raw;
}
 
 
// Carrito global (puede contener productos de ambos tipos)
let cartPrincipal = cargarCarrito("cart_principal");
let cartRepuestos = cargarCarrito("cart_repuestos");
 
let cart = [...cartPrincipal, ...cartRepuestos].map(item => ({
    id: item.id,
    name: item.name,
    priceARS: item.priceARS,
    quantity: item.quantity
}));
 
 
 
let currentStep = 1;
 
// Render resumen del pedido (sidebar)
function renderCheckoutSummary() {
    const summary = document.getElementById("checkoutSummary");
    if (!summary) return;
 
    summary.innerHTML = "";
    let subtotal = 0;
 
    cart.forEach(item => {
        const itemTotal = item.priceARS * item.quantity;
        subtotal += itemTotal;
 
        const div = document.createElement("div");
        div.className = "flex justify-between items-center mb-2 text-sm";
 
        div.innerHTML = `
            <span>${item.name} x ${item.quantity}</span>
            <span>$${itemTotal.toLocaleString("es-AR")}</span>
        `;
 
        summary.appendChild(div);
    });
 
    document.getElementById("checkoutTotal").textContent =
        `$${subtotal.toLocaleString("es-AR")}`;
}
// Validación de pasos
function validateStep(step) {
    let valid = true;
 
    if (step === 1) {
        const firstName = document.getElementById("firstName").value.trim();
        const lastName = document.getElementById("lastName").value.trim();
        const email = document.getElementById("email").value.trim();
        const phone = document.getElementById("phone").value.trim();
        if (!firstName || !lastName || !email || !phone) {
            alert("Por favor completa todos los campos de contacto.");
            valid = false;
        }
    } else if (step === 3) {
        const paymentSelected = document.querySelector('input[name="payment"]:checked');
        if (!paymentSelected) {
            alert("Por favor selecciona un método de pago.");
            valid = false;
        }
    }
 
    return valid;
}
 
// Navegación entre pasos
function goToStep(step) {
    document.querySelector(`#step${currentStep}`).classList.add("hidden");
    currentStep = step;
    document.querySelector(`#step${currentStep}`).classList.remove("hidden");
    renderCheckoutSummary();
    updateActiveStep();
    updateProgressBar();
}
 
 
function updateActiveStep() {
  document.querySelectorAll(".checkout-step").forEach(step => {
    const stepNumber = parseInt(step.dataset.step);
    if (stepNumber === currentStep) {
      step.classList.add("active");
    } else {
      step.classList.remove("active");
    }
  });
}
 
function updateProgressBar() {
  const totalSteps = 4; // step1, step2, step3, step4
  const progress = ((currentStep - 1) / (totalSteps - 1)) * 100;
  
  const bar = document.getElementById("progressBar");
  const text = document.getElementById("progressText");
 
  if (bar) bar.style.width = `${progress}%`;
  if (text) text.textContent = `Paso ${currentStep} de ${totalSteps}`;
}
 
function NextStep2() { if (validateStep(1)) goToStep(2); }
function NextStep3() { goToStep(3); }
async function NextStep4() {
    const metodoPago = document.querySelector('input[name="payment"]:checked').value;
    
    const paymentInput = document.querySelector('input[name="payment"]:checked');
 
    const cuentaId = paymentInput?.dataset.cuentaId || null;
    
    if (cart.length === 0) {
        alert("El carrito está vacío. Agrega productos antes de continuar.");
        return;
    }
 
    // Si el pago es Mercado Pago → no muestres Step 5, redirige directo
    if (metodoPago === "mp") {
        pagarConMP();
        return;
    }
 
    // Si es transferencia → continúa como siempre
    if (validateStep(4)) {
        try {
            const response = await fetch("/checkout", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    cart: cart,
                    comprador_nombre:
                        document.getElementById("firstName").value + " " +
                        document.getElementById("lastName").value,
                    telefono: document.getElementById("phone").value,
                    email: document.getElementById("email").value,
                    cuenta_id: cuentaId
                })
            });
 
            const data = await response.json();
 
            if (!response.ok) throw new Error(data.error || "Error en el checkout");
 
            console.log("✅ Pedido registrado:", data);
 
            renderFinalSummary(data.order_id, data.total);
            goToStep(4);
 
        } catch (err) {
            console.error("❌ Error al enviar checkout:", err);
        }
    }
}
 
function BackStep2() { goToStep(2); }
function BackStep3() { goToStep(3); }
 
 
// Paso final (confirmación)
function renderFinalSummary(orderId, total) {
    // Número de orden real del backend
    document.getElementById("orderNumber").textContent = "OR-" + orderId;
    
 
    // Mostrar total formateado
    const totalFormatted = total.toLocaleString("es-AR", { style: "currency", currency: "ARS" });
    document.getElementById("finalTotal").textContent = totalFormatted;
 
    // Copiar el contenido del resumen (opcional)
    const finalSummary = document.getElementById("finalSummary");
    finalSummary.innerHTML = `
        <div class="bg-green-50 p-4 rounded-lg border border-green-300">
            <h4 class="font-semibold text-green-800 mb-2">Resumen del pedido</h4>
            ${document.getElementById("checkoutSummary").innerHTML}
            <p class="mt-4 text-gray-700 font-medium">Total: ${totalFormatted}</p>
        </div>
    `;
 
    // Vaciar carrito después de confirmar
    setTimeout(() => {
        localStorage.removeItem("cart_principal");
        localStorage.removeItem("cart_repuestos");
        cartPrincipal = [];
        cartRepuestos = [];
        cart = [];
        updateCart();
    }, 1500);
}
 
 
document.addEventListener("DOMContentLoaded", () => {
    renderCheckoutSummary();
    updateProgressBar();
});