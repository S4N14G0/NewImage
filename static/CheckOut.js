
// Carrito global (puede contener productos de ambos tipos)
let cartPrincipal = JSON.parse(localStorage.getItem("cart_principal")) || [];
let cartRepuestos = JSON.parse(localStorage.getItem("cart_repuestos")) || [];

let cart = [...cartPrincipal, ...cartRepuestos].map(item => ({
    id: item.id,
    name: item.name,
    priceUSD: item.priceUSD, //
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
        const priceARS = item.priceUSD * dolarManual;
        const itemTotal = priceARS * item.quantity;
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
  const totalSteps = 3; // cantidad de pasos
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
                    cart: cart, // 👈 solo USD + qty
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