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
    const cart = JSON.parse(localStorage.getItem("checkoutCart") || "[]");
    const email = document.getElementById("email").value;

    const resp = await fetch("/crear_pago", {
        method: "POST",
        headers: { "Content-Type": "application/json" },                
        body: JSON.stringify({ cart, email })
    });

    const data = await resp.json();
        if (data.init_point) {
            window.location.href = data.init_point; // Ir a MercadoPago
        } else {
            alert("Error al iniciar pago: " + data.error);
        }
    }