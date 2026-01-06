/* ===============================
   CART HELPERS
=============================== */

function getCart() {
    return JSON.parse(localStorage.getItem("cart")) || [];
}

function saveCart(items) {
    localStorage.setItem("cart", JSON.stringify(items));
}

/* ===============================
   CART COUNT (HIDE WHEN 0)
=============================== */

function updateCartCount() {
    const count = getCart().length;
    const badge = document.getElementById("cart-count");
    if (!badge) return;

    if (count <= 0) {
        badge.style.display = "none";
        badge.textContent = "";
        return;
    }

    badge.style.display = "inline-block";
    badge.textContent = count;
}

/* ===============================
   CART TOTAL
=============================== */

function updateCartTotal() {
    const cart = getCart();
    const total = cart.reduce((sum, item) => sum + Number(item.price), 0);
    const el = document.getElementById("cart-total");
    if (el) el.textContent = `Total: $${total.toFixed(2)}`;
}

/* ===============================
   TOAST
=============================== */

function showCartToast(message) {
    const toast = document.getElementById("cart-toast");
    if (!toast) return;

    toast.textContent = message;
    toast.classList.add("show");
    setTimeout(() => toast.classList.remove("show"), 2000);
}

/* ===============================
   OPEN / CLOSE CART
=============================== */

function openCart() {
    updateCartCount();

    const panel = document.getElementById("cart-panel");
    const list = document.getElementById("cart-items");
    if (!panel || !list) return;

    list.innerHTML = "";

    const cart = getCart();
    cart.forEach(item => {
        const li = document.createElement("li");
        li.textContent = `${item.title} – $${Number(item.price).toFixed(2)}`;
        list.appendChild(li);
    });

    updateCartTotal();
    panel.style.display = "block";
}

function closeCart() {
    const panel = document.getElementById("cart-panel");
    if (panel) panel.style.display = "none";
}

/* ===============================
   CLEAR CART
=============================== */

function clearCart() {
    localStorage.removeItem("cart");

    const list = document.getElementById("cart-items");
    if (list) list.innerHTML = "";

    const total = document.getElementById("cart-total");
    if (total) total.textContent = "Total: $0.00";

    updateCartCount();
}

/* ===============================
   PLACE ORDER
=============================== */

function placeOrder() {
    const cart = getCart();

    if (cart.length === 0) {
        showCartToast("Cart is empty");
        return;
    }

    // Optional: save order history
    const orders = JSON.parse(localStorage.getItem("orders")) || [];
    orders.push({
        items: cart,
        total: cart.reduce((sum, item) => sum + Number(item.price), 0),
        createdAt: new Date().toISOString()
    });
    localStorage.setItem("orders", JSON.stringify(orders));

    // Clear cart
    clearCart();

    showCartToast("Order placed ✅ Thank you!");
    setTimeout(() => closeCart(), 1000);
}

/* ===============================
   OPTIONAL: ADD TO CART BUTTON
=============================== */

function addToCart(title, price) {
    const cart = getCart();
    cart.push({ title, price });
    saveCart(cart);

    updateCartCount();
    showCartToast("Added to cart 🛒");
}

/* ===============================
   INIT
=============================== */

document.addEventListener("DOMContentLoaded", () => {
    updateCartCount();
});
