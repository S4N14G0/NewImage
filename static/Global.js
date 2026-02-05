function toggleUserMenu() {
    document.getElementById("userMenu").classList.toggle("hidden");
}

document.addEventListener("click", function(e) {
    let menu = document.getElementById("userMenu");
    if (!menu) return;

    if (!e.target.closest(".nav-actions")) {
        menu.classList.add("hidden");
    }
});

function toggleMobileUserMenu() {
    document.getElementById("mobileUserMenu").classList.toggle("hidden");
}