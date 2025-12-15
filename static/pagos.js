document.addEventListener("DOMContentLoaded", () => {
    const mpButton = document.getElementById("mpButtonContainer");
    const bankInfo = document.getElementById("transferenciaInfo");

    const radios = document.querySelectorAll("input[name='payment']");

    radios.forEach(radio => {
        radio.addEventListener("change", () => {
            if (radio.checked && radio.value === "mp") {
                mpButton.classList.remove("hidden");
                bankInfo.classList.add("hidden");
            }
            if (radio.checked && radio.value === "bank") {
                mpButton.classList.add("hidden");
                bankInfo.classList.remove("hidden");
            }
        });
    });
});

async function pagarConMP() {
    // Combinar carritos
    const cartPrincipal = JSON.parse(localStorage.getItem("cart_principal")) || [];
    const cartRepuestos = JSON.parse(localStorage.getItem("cart_repuestos")) || [];
    const carrito = [...cartPrincipal, ...cartRepuestos];

    // Datos del formulario del checkout
    const firstName = document.getElementById("firstName")?.value ?? "";
    const lastName = document.getElementById("lastName")?.value ?? "";
    const email = document.getElementById("email")?.value ?? "";
    const telefono = document.getElementById("phone")?.value ?? "";
    const comprador_nombre = `${firstName} ${lastName}`;

    // Método de pago fijo (Mercado Pago)
    const metodo_pago = "mercado_pago";

    // Total final mostrado en el checkout
    const totalTexto = document.getElementById("checkoutTotal").innerText.replace("$", "").trim();
    const monto_total = parseFloat(totalTexto.replace(".", "").replace(",", "."));

    console.log("🧾 Enviando a MP:", {
        comprador_nombre,
        email,
        telefono,
        metodo_pago,
        monto_total,
        carrito
    });

    // Enviar datos al backend
    const response = await fetch("/crear_pago", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            comprador_nombre,
            comprador_telefono: telefono,
            comprador_email: email,
            metodo_pago,
            monto_total,
            carrito
        })
    });

    const data = await response.json();
    console.log("Respuesta MP:", data);

    if (data.init_point) {
        window.location.href = data.init_point; // redirige al checkout MP
    } else {
        alert("Error al iniciar el pago con Mercado Pago.");
    }
}
