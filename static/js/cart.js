/**
 * CART & CHECKOUT MANAGEMENT
 */

async function removeFromCart(itemId) {
  if (!confirm('Are you sure you want to remove this customized frame from your cart?')) return;

  try {
    const res = await fetch(`/api/cart/remove/${itemId}`, { method: 'POST' });
    const data = await res.json();
    if (data.success) {
      window.location.reload();
    }
  } catch (err) {
    console.error('Error removing item:', err);
    alert('Failed to remove item. Please try again.');
  }
}

async function clearCart() {
  if (!confirm('Are you sure you want to empty your shopping cart?')) return;
  try {
    const res = await fetch('/api/cart/clear', { method: 'POST' });
    const data = await res.json();
    if (data.success) {
      window.location.reload();
    }
  } catch (err) {
    console.error('Error clearing cart:', err);
  }
}
