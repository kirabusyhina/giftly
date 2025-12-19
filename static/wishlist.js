function getWishlist() {
    return JSON.parse(localStorage.getItem("wishlist")) || [];
}

function saveWishlist(items) {
    localStorage.setItem("wishlist", JSON.stringify(items));
}

function addToWishlist(title, price) {
    const wishlist = getWishlist();
    wishlist.push({ title, price });
    saveWishlist(wishlist);
    showToast();
}

function showToast() {
    const toast = document.getElementById("wishlist-toast");
    toast.classList.add("show");
    setTimeout(() => toast.classList.remove("show"), 2000);
}

function openWishlist() {
    const panel = document.getElementById("wishlist-panel");
    const list = document.getElementById("wishlist-items");
    list.innerHTML = "";

    const wishlist = getWishlist();
    wishlist.forEach(item => {
        const li = document.createElement("li");
        li.textContent = `${item.title} – $${item.price}`;
        list.appendChild(li);
    });

    panel.classList.add("open");
}

function closeWishlist() {
    document.getElementById("wishlist-panel").classList.remove("open");
}
