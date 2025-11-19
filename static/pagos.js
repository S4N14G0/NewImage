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
    const carrito = JSON.parse(localStorage.getItem("cart")) || [];
    const email = document.getElementById("email")?.value ?? "";

    const response = await fetch("/crear_pago", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            email: email,
            cart: carrito
        })
    });

    const data = await response.json();
    console.log("Respuesta MP:", data);
}

const mp = new MercadoPago(PUBLIC_KEY, { locale: "es-AR" });
console.log("Carrito localStorage:", carrito);