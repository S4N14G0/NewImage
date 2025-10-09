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

function addToCart(productId) {
  const product = products.find(p => p.id === productId);
  if (!product) return;

  let cart = JSON.parse(localStorage.getItem("cart")) || [];

  const existing = cart.find(item => item.id === productId);
  if (existing) {
    existing.quantity++;
  } else {
    cart.push({ ...product, quantity: 1 });
  }

  // Guardar en localStorage
  localStorage.setItem("cart", JSON.stringify(cart));

  updateCart();
}




























