// Guardar sesión al iniciar sesión
function login() {
    userLoggedIn = true;
    localStorage.setItem('userLoggedIn', 'true');
    updateLoginState();
    showSection('home');
}

// Cargar estado de sesión al iniciar
function init() {
    const storedLogin = localStorage.getItem('userLoggedIn');
    userLoggedIn = storedLogin === 'true';
    showSection('home');
    updateCartCount();
    updateLoginState(); 
}

// Logout y limpiar
function logout() {
    userLoggedIn = false;
    localStorage.removeItem('userLoggedIn');
    updateLoginState();
    showSection('home');
}
let cart = [];

// DOM Elements
const sections = {
    home: document.getElementById('home-section'),
    products: document.getElementById('products-section'),
    cart: document.getElementById('cart-section'),
    checkout: document.getElementById('checkout-section'),
    login: document.getElementById('login-section')
};

// Initialize the page
function init() {
    showSection('home');
    updateCartCount();
}

// Show specific section and hide others
function showSection(sectionId) {
    // Hide all sections
    Object.values(sections).forEach(section => {
        if (section) section.classList.add('hidden');
    });
    
    // Show the requested section
    if (sections[sectionId]) {
        sections[sectionId].classList.remove('hidden');
    }
    
    // Update UI based on login state
    updateLoginState();
}

// Toggle cart visibility
function toggleCart() {
    showSection('cart');
}

// Add product to cart
function addToCart(productId) {
    const product = getProductById(productId);
    if (product) {
        cart.push(product);
        updateCartCount();
        
        // For demo purposes, show an alert
        alert(`${product.name} añadido al carrito`);
    }
}

// Get product by ID
function getProductById(id) {
    const products = [
        { id: 1, name: 'Medio trapecio para reformer', price: "Consutlar disponibilidad"},
        { id: 2, name: 'Reformer metalico', price: "Constular disponibiliad" },
        { id: 3, name: 'Cinta abdominal', price: "Constular disponibiliad" }
    ];
    
    return products.find(p => p.id === id);
}

// Update cart count in navbar
function updateCartCount() {
    const cartCountElement = document.getElementById('cart-count');
    if (cartCountElement) {
        cartCountElement.textContent = cart.length;
    }
}

// Update UI based on login state
function updateLoginState() {
    const loginBtn = document.getElementById('login-btn');
    const accountBtn = document.getElementById('account-btn');
    const logoutBtn = document.getElementById('logout-btn');

    if (userLoggedIn) {
        loginBtn?.classList.add('hidden');
        accountBtn?.classList.remove('hidden');
        logoutBtn?.classList.remove('hidden');
    } else {
        loginBtn?.classList.remove('hidden');
        accountBtn?.classList.add('hidden');
        logoutBtn?.classList.add('hidden');
    }
}
// Logout function
function logout() {
    userLoggedIn = false;
    updateLoginState();
    showSection('home');
}

// Show product details
function showProductDetails(productId) {
    // In a real app, this would show a detailed view
    const product = getProductById(productId);
    if (product) {
        alert(`Detalles del producto: ${product.name}\nPrecio: $${product.price.toFixed(2)}`);
    }
}

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', init);
