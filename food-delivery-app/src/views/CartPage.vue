<template>
  <div class="cart-page">
    <div class="container">
      <div class="cart-header">
        <h1>Your Cart</h1>
      </div>

      <div v-if="cartItems.length === 0" class="empty-cart">
        <i class="fas fa-shopping-cart empty-cart-icon"></i>
        <h2>Your cart is empty</h2>
        <p>Add some items to your cart to proceed with checkout.</p>
        <router-link to="/app/home" class="btn btn-primary browse-btn">
          Browse Restaurants
        </router-link>
      </div>

      <div v-else class="cart-content">
        <!-- Cart Items -->
        <div class="cart-items">
          <div class="cart-items-header">
            <h2>Cart Items ({{ cartItems.length }})</h2>
          </div>
          
          <div v-for="(item, index) in cartItems" :key="index" class="cart-item">
            <div class="item-image">
              <img :src="item.image_url || 'https://dummyimage.com/100x100/cccccc/000000&text=Food'" :alt="item.item_name">
            </div>
            <div class="item-details">
              <h3>{{ item.item_name }}</h3>
              <p v-if="item.restaurant_name" class="restaurant-name">{{ item.restaurant_name }}</p>
              <p v-if="item.description" class="item-description">{{ item.description }}</p>
              <p class="item-price">${{ item.price.toFixed(2) }}</p>
            </div>
            <div class="item-quantity">
              <button 
                class="quantity-btn" 
                @click="decreaseQuantity(index)"
                :disabled="item.quantity <= 1"
              >
                <i class="fas fa-minus"></i>
              </button>
              <span class="quantity-value">{{ item.quantity }}</span>
              <button 
                class="quantity-btn" 
                @click="increaseQuantity(index)"
              >
                <i class="fas fa-plus"></i>
              </button>
            </div>
            <div class="item-total">
              <p>${{ (item.price * item.quantity).toFixed(2) }}</p>
              <button class="remove-btn" @click="removeItem(index)">
                <i class="fas fa-trash"></i>
              </button>
            </div>
          </div>

          <div class="cart-actions">
            <button class="btn btn-secondary clear-btn" @click="clearCart">
              <i class="fas fa-trash"></i> Clear Cart
            </button>
            <router-link to="/app/home" class="btn btn-secondary continue-shopping">
              <i class="fas fa-arrow-left"></i> Continue Shopping
            </router-link>
          </div>
        </div>

        <!-- Order Summary -->
        <div class="order-summary">
          <div class="summary-header">
            <h2>Order Summary</h2>
          </div>
          <div class="summary-content">
            <div class="summary-row">
              <span>Subtotal</span>
              <span>${{ subtotal.toFixed(2) }}</span>
            </div>
            <!-- Delivery Fee row removed -->
            <div v-if="discountAmount > 0" class="summary-row discount">
              <span>Discount</span>
              <span>-${{ discountAmount.toFixed(2) }}</span>
            </div>
            <div class="summary-row total">
              <span>Total</span>
              <span>${{ total.toFixed(2) }}</span>
            </div>

            <!-- Promotion Code Input -->
            <div class="promo-section">
              <div class="promo-input">
                <input 
                  type="text" 
                  v-model="promoCode" 
                  placeholder="Enter promo code" 
                  :disabled="promoApplied"
                />
                <button 
                  class="btn" 
                  :class="promoApplied ? 'btn-danger' : 'btn-primary'" 
                  @click="promoApplied ? removePromo() : applyPromo()"
                >
                  {{ promoApplied ? 'Remove' : 'Apply' }}
                </button>
              </div>
              <p v-if="promoError" class="promo-error">{{ promoError }}</p>
              <p v-if="promoSuccess" class="promo-success">{{ promoSuccess }}</p>
            </div>

            <!-- Checkout Button -->
            <button 
              class="btn btn-primary checkout-btn" 
              @click="placeOrder"
            >
              Place Order
            </button>

            <!-- Payment Methods -->
            <div class="payment-methods">
              <p>We Accept</p>
              <div class="payment-icons">
                <i class="fab fa-cc-visa"></i>
                <i class="fab fa-cc-mastercard"></i>
                <i class="fab fa-cc-amex"></i>
                <i class="fab fa-cc-paypal"></i>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'CartPage',
  data() {
    return {
      cartItems: [],
      // deliveryFee removed
      promoCode: '',
      promoApplied: false,
      discountAmount: 0,
      promoError: '',
      promoSuccess: '',
      isProcessing: false
    }
  },
  computed: {
    subtotal() {
      return this.cartItems.reduce((total, item) => total + (item.price * item.quantity), 0);
    },
    total() {
      return this.subtotal - this.discountAmount; // deliveryFee removed from total calculation
    }
  },
  methods: {
    loadCartItems() {
      // In a real app, you might get this from Vuex or localStorage
      const cartData = localStorage.getItem('cart');
      if (cartData) {
        try {
          this.cartItems = JSON.parse(cartData);
        } catch (error) {
          console.error('Error parsing cart data:', error);
          this.cartItems = [];
        }
      }
    },
    saveCartItems() {
      localStorage.setItem('cart', JSON.stringify(this.cartItems));
    },
    increaseQuantity(index) {
      this.cartItems[index].quantity += 1;
      this.cartItems[index].totalPrice = this.cartItems[index].price * this.cartItems[index].quantity;
      this.saveCartItems();
    },
    decreaseQuantity(index) {
      if (this.cartItems[index].quantity > 1) {
        this.cartItems[index].quantity -= 1;
        this.cartItems[index].totalPrice = this.cartItems[index].price * this.cartItems[index].quantity;
        this.saveCartItems();
      }
    },
    removeItem(index) {
      // Remove the item at the specified index
      this.cartItems.splice(index, 1);
      this.saveCartItems();
      
      // Reset promo code if cart becomes empty
      if (this.cartItems.length === 0) {
        this.removePromo();
      }
    },
    clearCart() {
      if (confirm('Are you sure you want to clear your cart?')) {
        this.cartItems = [];
        this.saveCartItems();
        this.removePromo();
      }
    },
    async applyPromo() {
      // Reset messages
      this.promoError = '';
      this.promoSuccess = '';
      this.isProcessing = true;
      
      // Simple promo code validation
      if (!this.promoCode) {
        this.promoError = 'Please enter a promo code';
        return;
      }

      // Get user ID from localStorage if available
      const userData = localStorage.getItem('currentUser');
      let customerId = null;
      if (userData) {
        try {
          const user = JSON.parse(userData);
          customerId = user.customer_id;
        } catch (error) {
          console.error('Error parsing user data:', error);
        }
      }
      
      try {
        // First, try to fetch the voucher by code
        const response = await fetch(`http://localhost:5012/voucher/code/${this.promoCode}`);
        const result = await response.json();
        
        if (result.code === 200 && result.data) {
          const voucher = result.data;
          
          // Check if voucher is expired
          const currentDate = new Date();
          const expiryDate = new Date(voucher.expiry_date);
          
          if (expiryDate < currentDate) {
            this.promoError = 'This voucher has expired';
            return;
          }
          
          // Check if voucher is already used
          if (voucher.status === 'Used') {
            this.promoError = 'This voucher has already been used';
            return;
          }
          
          // Check if voucher belongs to this customer
          if (voucher.customer_id && customerId && voucher.customer_id !== customerId) {
            this.promoError = 'This voucher does not belong to your account';
            return;
          }
          
          // Voucher is valid, apply discount
          const discountPercentage = voucher.discount_percentage;
          const maxDiscountAmount = voucher.max_discount_amount;
          
          // Calculate discount amount
          let calculatedDiscount = (this.subtotal * (discountPercentage / 100));
          
          // Cap discount at max_discount_amount
          if (calculatedDiscount > maxDiscountAmount) {
            calculatedDiscount = maxDiscountAmount;
          }
          
          this.discountAmount = calculatedDiscount;
          this.promoSuccess = `${discountPercentage}% discount applied! (up to $${maxDiscountAmount})`;
          this.promoApplied = true;
          
          // Store voucher details for later use
          this.activeVoucher = voucher;
          
        } else {
          // Use the validate endpoint as fallback
          const validateResponse = await fetch('http://localhost:5012/voucher/validate', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              code: this.promoCode,
              customer_id: customerId
            }),
          });
          
          const validateResult = await validateResponse.json();
          
          if (validateResult.code === 200 && validateResult.data) {
            const voucher = validateResult.data;
            
            // Voucher is valid, apply discount
            const discountPercentage = voucher.discount_percentage;
            const maxDiscountAmount = voucher.max_discount_amount;
            
            // Calculate discount amount
            let calculatedDiscount = (this.subtotal * (discountPercentage / 100));
            
            // Cap discount at max_discount_amount
            if (calculatedDiscount > maxDiscountAmount) {
              calculatedDiscount = maxDiscountAmount;
            }
            
            this.discountAmount = calculatedDiscount;
            this.promoSuccess = `${discountPercentage}% discount applied! (up to $${maxDiscountAmount})`;
            this.promoApplied = true;
            
            // Store voucher details for later use
            this.activeVoucher = voucher;
          } else {
            this.promoError = validateResult.message || 'Invalid promo code';
          }
        }
      } catch (error) {
        console.error('Error validating voucher:', error);
        this.promoError = 'Could not validate promo code. Please try again.';
      } finally {
        this.isProcessing = false;
      }
    },
    removePromo() {
      this.promoCode = '';
      this.promoApplied = false;
      this.discountAmount = 0;
      this.promoError = '';
      this.promoSuccess = '';
    },
    placeOrder() {
      if (this.cartItems.length === 0) {
        alert('Your cart is empty. Please add items before checking out.');
        return;
      }
      
      // In a real app, you would redirect to a checkout page or show a checkout form
      this.$router.push('/checkout');
    }
  },
  mounted() {
    this.loadCartItems();
  }
}
</script>

<style scoped>
.cart-page {
  padding: 2rem 0;
}

.cart-header {
  margin-bottom: 2rem;
  text-align: center;
}

.cart-header h1 {
  font-size: 2rem;
  color: var(--secondary-color);
  margin-bottom: 0.5rem;
}

/* Empty cart styling */
.empty-cart {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  text-align: center;
}

.empty-cart-icon {
  font-size: 4rem;
  color: #ccc;
  margin-bottom: 1.5rem;
}

.empty-cart h2 {
  font-size: 1.8rem;
  margin-bottom: 1rem;
  color: var(--secondary-color);
}

.empty-cart p {
  margin-bottom: 2rem;
  color: #666;
  max-width: 400px;
}

.browse-btn {
  padding: 0.75rem 1.5rem;
}

/* Cart content layout */
.cart-content {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 2rem;
}

@media (max-width: 992px) {
  .cart-content {
    grid-template-columns: 1fr;
  }
}

/* Cart items styling */
.cart-items {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.cart-items-header {
  padding: 1.5rem;
  border-bottom: 1px solid #eee;
}

.cart-items-header h2 {
  font-size: 1.5rem;
  color: var(--secondary-color);
  margin: 0;
}

.cart-item {
  display: grid;
  grid-template-columns: auto 1fr auto auto;
  gap: 1.5rem;
  padding: 1.5rem;
  border-bottom: 1px solid #eee;
  align-items: center;
}

.item-image {
  width: 100px;
  height: 100px;
  border-radius: 8px;
  overflow: hidden;
}

.item-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.item-details h3 {
  font-size: 1.2rem;
  margin-bottom: 0.5rem;
  color: var(--secondary-color);
}

.restaurant-name {
  font-size: 0.9rem;
  color: var(--primary-color);
  margin-bottom: 0.5rem;
}

.item-description {
  font-size: 0.9rem;
  color: #666;
  margin-bottom: 0.5rem;
  max-width: 300px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.item-price {
  font-size: 1rem;
  font-weight: bold;
  color: var(--secondary-color);
}

.item-quantity {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.quantity-btn {
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #f0f0f0;
  border: none;
  border-radius: 50%;
  cursor: pointer;
  transition: all 0.2s;
}

.quantity-btn:hover:not(:disabled) {
  background-color: #e0e0e0;
}

.quantity-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.quantity-value {
  font-size: 1.1rem;
  width: 30px;
  text-align: center;
}

.item-total {
  text-align: right;
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 0.5rem;
}

.item-total p {
  font-size: 1.2rem;
  font-weight: bold;
  color: var(--secondary-color);
}

.remove-btn {
  background: none;
  border: none;
  color: #999;
  cursor: pointer;
  transition: color 0.2s;
}

.remove-btn:hover {
  color: var(--danger-color, #dc3545);
}

.cart-actions {
  display: flex;
  justify-content: space-between;
  padding: 1.5rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.continue-shopping {
  background-color: var(--success-color, #28a745); /* Change box color to green */
  color: white; /* Ensure text is readable on green background */
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem; /* Optional: Add padding for better appearance */
  border: none; /* Optional: Remove border if present */
  border-radius: 4px; /* Optional: Add rounded corners */
  cursor: pointer; /* Optional: Add pointer cursor for better UX */
}

.clear-btn {
  background-color: var(--danger-color, #dc3545); /* Change box color to red */
  color: white; /* Ensure text is readable on red background */
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem; /* Optional: Add padding for better appearance */
  border: none; /* Optional: Remove border if present */
  border-radius: 4px; /* Optional: Add rounded corners */
  cursor: pointer; /* Optional: Add pointer cursor for better UX */
}

/* Order summary styling */
.order-summary {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  align-self: start;
  position: sticky;
  top: 2rem;
}

.summary-header {
  padding: 1.5rem;
  border-bottom: 1px solid #eee;
}

.summary-header h2 {
  font-size: 1.5rem;
  color: var(--secondary-color);
  margin: 0;
}

.summary-content {
  padding: 1.5rem;
}

.summary-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 1rem;
  font-size: 1rem;
}

.summary-row.total {
  margin-top: 1.5rem;
  padding-top: 1.5rem;
  border-top: 1px solid #eee;
  font-size: 1.2rem;
  font-weight: bold;
  color: var(--secondary-color);
}

.summary-row.discount {
  color: var(--success-color, #28a745);
}

.promo-section {
  margin: 1.5rem 0;
}

.promo-input {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
}

.promo-input input {
  flex: 1;
  padding: 0.75rem 1rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
}

.promo-error {
  color: var(--danger-color, #dc3545);
  font-size: 0.9rem;
  margin-top: 0.5rem;
}

.promo-success {
  color: var(--success-color, #28a745);
  font-size: 0.9rem;
  margin-top: 0.5rem;
}

.checkout-btn {
  width: 100%;
  padding: 1rem;
  font-size: 1.1rem;
  margin: 1rem 0;
}

.payment-methods {
  margin-top: 1.5rem;
  text-align: center;
}

.payment-methods p {
  font-size: 0.9rem;
  color: #666;
  margin-bottom: 0.5rem;
}

.payment-icons {
  display: flex;
  justify-content: center;
  gap: 1rem;
  font-size: 1.8rem;
  color: #999;
}

@media (max-width: 768px) {
  .cart-item {
    grid-template-columns: 1fr;
    gap: 1rem;
  }
  
  .item-image {
    width: 100%;
    height: 200px;
  }
  
  .item-quantity, .item-total {
    display: flex;
    flex-direction: row;
    justify-content: space-between;
    width: 100%;
  }
  
  .item-total {
    border-top: 1px solid #eee;
    padding-top: 1rem;
  }
}
</style>