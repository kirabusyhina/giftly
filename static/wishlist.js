function getWishlist() {
    return JSON.parse(localStorage.getItem("wishlist")) || [];
}

function saveWishlist(items) {
    localStorage.setItem("wishlist", JSON.stringify(items));
}

function getCart() {
    return JSON.parse(localStorage.getItem("cart")) || [];
}

function saveCart(items) {
    localStorage.setItem("cart", JSON.stringify(items));
}

function addToWishlist(title, price) {
    const wishlist = getWishlist();

    const exists = wishlist.some(item => item.title === title);
    if (exists) {
        showToast("Already in wishlist ❤️");
        return;
    }

    wishlist.push({ title, price });
    saveWishlist(wishlist);

    updateWishlistCount();
    showToast("Added to wishlist ❤️");
}

function showToast(message) {
    const toast = document.getElementById("wishlist-toast");
    toast.textContent = message;
    toast.classList.add("show");

    setTimeout(() => {
        toast.classList.remove("show");
    }, 2000);
}

function openWishlist() {
    const panel = document.getElementById("wishlist-panel");
    const list = document.getElementById("wishlist-items");

    list.innerHTML = "";

    const wishlist = getWishlist();
    wishlist.forEach(item => {
        const li = document.createElement("li");
        li.textContent = `${item.title} – $${Number(item.price).toFixed(2)}`;
        list.appendChild(li);
    });

    updateTotalPrice();
    panel.style.display = "block";
}

function closeWishlist() {
    document.getElementById("wishlist-panel").style.display = "none";
}

function clearWishlist() {
    localStorage.removeItem("wishlist");
    document.getElementById("wishlist-items").innerHTML = "";
    document.getElementById("wishlist-total").textContent = "Total: $0.00";
    updateWishlistCount();
}

function updateTotalPrice() {
    const wishlist = getWishlist();
    const total = wishlist.reduce((sum, item) => sum + Number(item.price), 0);

    document.getElementById("wishlist-total").textContent =
        `Total: $${total.toFixed(2)}`;
}

function updateWishlistCount() {
    const count = getWishlist().length;
    const badge = document.getElementById("wishlist-count");

    if (badge) {
        badge.textContent = count;
    }
}

function moveWishlistToCart() {
    const wishlist = getWishlist();

    if (wishlist.length === 0) {
        alert("Wishlist is empty");
        return;
    }

    saveCart(wishlist);
    localStorage.removeItem("wishlist");

    document.getElementById("wishlist-items").innerHTML = "";
    document.getElementById("wishlist-total").textContent = "Total: $0.00";
    updateWishlistCount();

    alert("Items moved to cart 🛒");
}

document.addEventListener("DOMContentLoaded", () => {
    updateWishlistCount();
});