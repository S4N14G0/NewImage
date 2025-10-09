// Carrito global
let cart = JSON.parse(localStorage.getItem("cart")) || [];
let currentStep = 1;

// Función para mostrar resumen del pedido (paso 3)
function renderCheckoutSummary() {
    const summary = document.getElementById("checkoutSummary");
    if (!summary) return;

    summary.innerHTML = "";
    let subtotal = 0;

    cart.forEach(item => {
        const itemTotal = item.price * item.quantity;
        subtotal += itemTotal;
        const div = document.createElement("div");
        div.className = "flex justify-between mb-2";
        div.innerHTML = `<span>${item.name} x ${item.quantity}</span> <span>$${itemTotal.toFixed(2)}</span>`;
        summary.appendChild(div);
    });

    document.getElementById("checkoutTotal").textContent = `$${subtotal.toFixed(2)}`;
    document.getElementById("finalTotal").textContent = `$${subtotal.toFixed(2)}`;
}

// // Validar campos de cada paso
function validateStep(step) {
    let valid = true;

    if(step === 1) {
        const firstName = document.getElementById("firstName").value.trim();
        const lastName = document.getElementById("lastName").value.trim();
        const email = document.getElementById("email").value.trim();
        const phone = document.getElementById("phone").value.trim();
        if (!firstName || !lastName || !email || !phone) {
            alert("Por favor completa todos los campos de contacto.");
            valid = false;
        }
    } else if(step === 2) {
        const address = document.getElementById("address").value.trim();
        const city = document.getElementById("city").value.trim();
        const zip = document.getElementById("zip").value.trim();
        const country = document.getElementById("country").value;
        if (!address || !city || !zip || country === "Seleccionar") {
            alert("Por favor completa todos los campos de dirección.");
            valid = false;
        }
    } else if(step === 4) {
        const paymentSelected = document.querySelector('input[name="payment"]:checked');
        if(!paymentSelected) {
            alert("Por favor selecciona un método de pago.");
            valid = false;
        }
    }

    return valid;
}

function goToStep(step) {
    document.querySelector(`#step${currentStep}`).classList.add("hidden");
    currentStep = step;
    document.querySelector(`#step${currentStep}`).classList.remove("hidden");
    renderCheckoutSummary();
}


// Botones siguiente
function NextStep2() {
    if(validateStep(1)) goToStep(2);
}

function NextStep3() {
    if(validateStep(2)) goToStep(3);
}

function NextStep4() {
    goToStep(4);
}

function NextStep5() {
    if(validateStep(4)) {
        goToStep(5);
        renderFinalSummary();
    }
}

// Botones atrás
function BackStep2() { goToStep(1); }
function BackStep3() { goToStep(2); }
function BackStep4() { goToStep(3); }
// Resumen final (paso 5)
function renderFinalSummary() {
    // Número de orden aleatorio
    document.getElementById("orderNumber").textContent = "OR-" + Math.floor(Math.random() * 1000000);

    // Copiar contenido del paso 3 al final
    const finalSummary = document.getElementById("finalSummary");
    finalSummary.innerHTML = document.getElementById("checkoutSummary").innerHTML;

    // Copiar total
    document.getElementById("finalTotal").textContent = document.getElementById("checkoutTotal").textContent;

    // Vaciar carrito después de confirmar
    localStorage.removeItem("cart");
    cart = [];
    updateCart();
}

// Inicializar resumen al cargar la página
document.addEventListener("DOMContentLoaded", renderCheckoutSummary);
