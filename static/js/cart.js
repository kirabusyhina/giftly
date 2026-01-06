function getCart() {
    return JSON.parse(localStorage.getItem("cart")) || [];
}

function saveCart(items) {
    localStorage.setItem("cart", JSON.stringify(items));
}

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

function clearCart() {
    localStorage.removeItem("cart");

    const list = document.getElementById("cart-items");
    if (list) list.innerHTML = "";

    const total = document.getElementById("cart-total");
    if (total) total.textContent = "Total: $0.00";

    updateCartCount();
}

function showCartToast(message) {
    const toast = document.getElementById("cart-toast");
    if (!toast) return;

    toast.textContent = message;
    toast.classList.add("show");
    setTimeout(() => toast.classList.remove("show"), 2000);
}

function addToCart(title, price) {
    const cart = getCart();
    cart.push({ title, price });
    saveCart(cart);
    updateCartCount();
    showCartToast("Added to cart 🛒");
}

document.addEventListener("DOMContentLoaded", () => {
    updateCartCount();
});
