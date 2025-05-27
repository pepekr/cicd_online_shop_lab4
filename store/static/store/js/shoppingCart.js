function getCart() {
  return JSON.parse(localStorage.getItem("cart") || "[]");
}

function saveCart(cart) {
  localStorage.setItem("cart", JSON.stringify(cart));
}
const cartEvent = new CustomEvent("cart-update-event")
function addToCart(productId) {
  const cart = getCart();
  const existing = cart.find(item => item.id === productId);
  if (existing) {
    existing.quantity += 1;
  } else {
    cart.push({ id: productId, quantity: 1 });
  }
  saveCart(cart);
  window.dispatchEvent(cartEvent)
}

function removeFromCart(productId) {
  const cart = getCart();
  const existing = cart.find(item => item.id === productId);
  if (existing) {
    existing.quantity -= 1;
    if (existing.quantity <= 0) {
      const index = cart.findIndex(item => item.id === productId);
      if (index > -1) {
        cart.splice(index, 1);
      }
    }
    saveCart(cart);

    const cartEvent = new CustomEvent("cart-update-event", { detail: cart });
    window.dispatchEvent(cartEvent);
  }
}


function updateQuantity(productId, quantity) {
  const cart = getCart();
  const item = cart.find(item => item.id === productId);
  if (item) {
    item.quantity = quantity;
    saveCart(cart);
  }
}