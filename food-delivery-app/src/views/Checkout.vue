<template>
  <div class="checkout-page">
    <div class="container">
      <div class="checkout-header">
        <h1>Checkout</h1>
      </div>

      <div v-if="loading" class="loading-state">
        <div class="spinner"></div>
        <p>Loading your order details...</p>
      </div>

      <div v-else-if="error" class="error-state">
        <i class="fas fa-exclamation-circle error-icon"></i>
        <h3>Something went wrong</h3>
        <p>{{ error }}</p>
        <button class="btn btn-primary" @click="reloadPage">Try Again</button>
      </div>

      <div v-else class="checkout-content">
        <!-- Order Summary -->
        <div class="order-summary">
          <div class="summary-header">
            <h2>Order Summary</h2>
          </div>
          <div class="summary-content">
            <div class="cart-items">
              <h3>Items ({{ cartItems.length }})</h3>
              <div v-for="(item, index) in cartItems" :key="index" class="cart-item">
                <div class="item-image">
                  <img :src="item.image_url || 'https://dummyimage.com/100x100/cccccc/000000&text=Food'" :alt="item.item_name">
                </div>
                <div class="item-details">
                  <span class="item-quantity">{{ item.quantity }}x</span>
                  <span class="item-name">{{ item.item_name }}</span>
                </div>
                <span class="item-price">${{ (item.price * item.quantity).toFixed(2) }}</span>
              </div>
            </div>

            <!-- Loyalty Status Section -->
            <div class="loyalty-status-section">
              <h3>Your Loyalty Benefits</h3>
              <div class="loyalty-status-info">
                <div class="loyalty-status-badge" :class="loyaltyStatusClass">
                  <i class="fas fa-crown"></i>
                  <span>{{ loyaltyStatus }}</span>
                </div>
                <div class="loyalty-status-details">
                  <p>Status discount: <span class="discount-value">{{ loyaltyStatusDiscount }}% off</span></p>
                  <p>Available points: <strong>{{ loyaltyPoints }}</strong></p>
                </div>
              </div>
            </div>

            <!-- Loyalty Points Section moved here -->
            <div v-if="loyaltyEnabled" class="loyalty-section">
              <h3>Use Loyalty Points</h3>
              <div class="loyalty-info">
                <p>You have <strong>{{ loyaltyPoints }}</strong> points available</p>
                <div class="loyalty-control">
                  <label for="loyalty-points-input">Points to use:</label>
                  <div class="input-with-controls">
                    <button 
                      class="btn-control" 
                      @click="decrementPoints" 
                      :disabled="loyaltyPointsUsed <= 0"
                    >
                      <i class="fas fa-minus"></i>
                    </button>
                    <input 
                      type="number" 
                      id="loyalty-points-input" 
                      v-model.number="loyaltyPointsUsed" 
                      :max="loyaltyPoints"
                      min="0"
                      step="1"
                      class="points-input"
                    >
                    <button 
                      class="btn-control" 
                      @click="incrementPoints" 
                      :disabled="loyaltyPointsUsed >= loyaltyPoints"
                    >
                      <i class="fas fa-plus"></i>
                    </button>
                  </div>
                </div>
                <p class="loyalty-value">Value: -${{ (loyaltyPointsUsed * 0.1).toFixed(2) }}</p>
              </div>
            </div>

            <div class="cost-summary">
              <div class="summary-row">
                <span>Subtotal</span>
                <span>${{ subtotal.toFixed(2) }}</span>
              </div>
              <div class="summary-row">
                <span>Delivery Fee</span>
                <span>${{ deliveryInfo.delivery_fee ? deliveryInfo.delivery_fee.toFixed(2) : '0.00' }}</span>
              </div>
              <div v-if="loyaltyStatusDiscountAmount > 0" class="summary-row discount">
                <span>{{ loyaltyStatus }} Status Discount ({{ loyaltyStatusDiscount }}%)</span>
                <span>-${{ loyaltyStatusDiscountAmount.toFixed(2) }}</span>
              </div>
              <div v-if="discountAmount > 0" class="summary-row discount">
                <span>Voucher Discount</span>
                <span>-${{ discountAmount.toFixed(2) }}</span>
              </div>
              <div v-if="loyaltyPointsUsed > 0" class="summary-row discount">
                <span>Loyalty Discount ({{ loyaltyPointsUsed }} points)</span>
                <span>-${{ (loyaltyPointsUsed * 0.1).toFixed(2) }}</span>
              </div>
              <div class="summary-row total">
                <span>Total</span>
                <span>${{ totalAmount.toFixed(2) }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Delivery Info (now beside Order Summary) -->
        <div class="delivery-info">
          <div class="info-header">
            <h2>Delivery Information</h2>
          </div>
          <div class="info-content">
            <div v-if="deliveryInfo.restaurant" class="info-section">
              <h3>Restaurant</h3>
              <p class="info-item">
                <i class="fas fa-utensils info-icon"></i>
                <span>{{ deliveryInfo.restaurant.name }}</span>
              </p>
            </div>

            <div v-if="deliveryInfo.rider" class="info-section">
              <h3>Your Rider</h3>
              <p class="info-item">
                <i class="fas fa-user info-icon"></i>
                <span>{{ deliveryInfo.rider.name }}</span>
              </p>
              <p v-if="deliveryInfo.rider.phone_number" class="info-item">
                <i class="fas fa-phone info-icon"></i>
                <span>{{ deliveryInfo.rider.phone_number }}</span>
              </p>
              <p v-if="deliveryInfo.rider.vehicle_type" class="info-item">
                <i class="fas fa-motorcycle info-icon"></i>
                <span>Vehicle: {{ deliveryInfo.rider.vehicle_type }}</span>
              </p>
              <p v-if="deliveryInfo.rider.distance_to_restaurant_km" class="info-item">
                <i class="fas fa-map-marker-alt info-icon"></i>
                <span>Currently {{ typeof deliveryInfo.rider.distance_to_restaurant_km === 'number' ? 
                  deliveryInfo.rider.distance_to_restaurant_km.toFixed(1) + ' km' : 
                  deliveryInfo.rider.distance_to_restaurant_km }} from restaurant</span>
              </p>
            </div>

            <div v-if="deliveryInfo.travel_info" class="info-section">
              <h3>Delivery Estimate</h3>
              <p class="info-item">
                <i class="fas fa-clock info-icon"></i>
                <span>Time: {{ deliveryInfo.travel_info.duration }}</span>
              </p>
              <p class="info-item">
                <i class="fas fa-road info-icon"></i>
                <span>Distance: {{ deliveryInfo.travel_info.distance }}</span>
              </p>
            </div>
            
            <div v-if="deliveryInfo.price_info" class="info-section">
              <h3>Delivery Fee Breakdown</h3>
              <p class="info-item">
                <span>Base Fare:</span>
                <span>${{ deliveryInfo.price_info.base_fare.toFixed(2) }}</span>
              </p>
              <p class="info-item">
                <span>Time Charge:</span>
                <span>${{ deliveryInfo.price_info.time_charge.toFixed(2) }}</span>
              </p>
              <p class="info-item">
                <span>Distance Surcharge:</span>
                <span>${{ deliveryInfo.price_info.distance_surcharge.toFixed(2) }}</span>
              </p>
            </div>
            
            <!-- Static Map Image -->
            <div v-if="deliveryInfo.static_map_url" class="info-section">
              <h3>Delivery Route</h3>
              <img :src="deliveryInfo.static_map_url" alt="Delivery Route Map" style="width: 100%; border-radius: 8px;">
            </div>
          </div>
        </div>

        <!-- Payment Section (still spans full width) -->
        <div class="payment-section">
          <div class="payment-header">
            <h2>Payment Details</h2>
          </div>
          <div class="payment-content">
            <div class="payment-methods">
              <h3>Payment Method</h3>
              <p class="payment-info">We use Stripe for secure payments. You'll be redirected to their payment page.</p>
              <div class="payment-logos">
                <i class="fab fa-cc-visa"></i>
                <i class="fab fa-cc-mastercard"></i>
                <i class="fab fa-cc-amex"></i>
              </div>
            </div>

            <button 
              class="btn btn-primary place-order-btn" 
              @click="placeOrder"
              :disabled="isProcessing"
            >
              <span v-if="isProcessing">
                <i class="fas fa-spinner fa-spin"></i>
                Processing...
              </span>
              <span v-else>
                Complete Order
              </span>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'CheckoutPage',
  data() {
    return {
      loading: true,
      error: null,
      cartItems: [],
      subtotal: 0,
      discountAmount: 0,
      deliveryInfo: {
        restaurant: null,
        rider: null,
        travel_info: null,
        price_info: null,
        delivery_fee: 0
      },
      isProcessing: false,
      loyaltyEnabled: false,
      loyaltyPoints: 0,
      loyaltyPointsUsed: 0,
      loyaltyStatus: 'Bronze',
      loyaltyStatusDiscount: 0
    }
  },
  computed: {
    loyaltyStatusClass() {
      return {
        'bronze': this.loyaltyStatus === 'Bronze',
        'silver': this.loyaltyStatus === 'Silver',
        'gold': this.loyaltyStatus === 'Gold'
      };
    },
    loyaltyStatusDiscountAmount() {
      // Calculate the loyalty status discount amount
      const subtotalWithDelivery = this.subtotal + (this.deliveryInfo.delivery_fee || 0);
      return subtotalWithDelivery * (this.loyaltyStatusDiscount / 100);
    },
    totalAmount() {
      // Calculate total = subtotal + delivery fee - status discount - voucher discount - loyalty points value
      const loyaltyDiscount = this.loyaltyPointsUsed * 0.1; // Each point is worth $0.10
      return this.subtotal + 
             (this.deliveryInfo.delivery_fee || 0) - 
             this.loyaltyStatusDiscountAmount -
             this.discountAmount - 
             loyaltyDiscount;
    }
  },
  methods: {
    incrementPoints() {
      if (this.loyaltyPointsUsed < this.loyaltyPoints) {
        this.loyaltyPointsUsed++;
      }
    },
    
    decrementPoints() {
      if (this.loyaltyPointsUsed > 0) {
        this.loyaltyPointsUsed--;
      }
    },
    
    loadCartItems() {
      // Load cart items from local storage
      const cartData = localStorage.getItem('cart');
      if (cartData) {
        try {
          this.cartItems = JSON.parse(cartData);
          this.subtotal = this.cartItems.reduce((total, item) => total + (item.price * item.quantity), 0);
          
          // Load discount amount if any
          const discountData = localStorage.getItem('cartDiscount');
          if (discountData) {
            this.discountAmount = JSON.parse(discountData).amount || 0;
          }
          
        } catch (error) {
          console.error('Error parsing cart data:', error);
          this.error = 'Could not load your cart. Please try again.';
          this.cartItems = [];
        }
      } else {
        // Redirect to cart if no items found
        this.$router.push('/app/cart');
      }
    },
    
    loadUserLoyalty() {
      const userData = localStorage.getItem('currentUser');
      if (userData) {
        try {
          const user = JSON.parse(userData);
          this.loyaltyPoints = user.loyalty_points || 0;
          this.loyaltyStatus = user.loyalty_status || 'Bronze';
          this.loyaltyEnabled = this.loyaltyPoints > 0;
          
          // Set discount percentage based on loyalty status
          if (this.loyaltyStatus === 'Bronze') {
            this.loyaltyStatusDiscount = 0;
          } else if (this.loyaltyStatus === 'Silver') {
            this.loyaltyStatusDiscount = 5;  // 5% discount for Silver members
          } else if (this.loyaltyStatus === 'Gold') {
            this.loyaltyStatusDiscount = 10; // 10% discount for Gold members
          }
          
        } catch (error) {
          console.error('Error parsing user data:', error);
        }
      }
    },
    
    async fetchDeliveryInfo() {
      try {
        // Extract restaurant information from cart items
        let restaurantId = null;
        let restaurantName = null;
        
        if (this.cartItems.length > 0) {
          // Get the restaurant ID and name from the first cart item
          // Assuming all items are from the same restaurant
          restaurantId = this.cartItems[0].restaurant_id;
          restaurantName = this.cartItems[0].restaurant_name || 'Restaurant';
        } else {
          throw new Error('No items in cart');
        }
        
        // Use "auto" parameter to get the closest available rider
        const autoAssignRider = "auto";
        
        // Call the dynamic pricing microservice with "auto" to get closest rider
        const response = await fetch(`http://localhost:5016/calculate_delivery_fee/${restaurantId}/${autoAssignRider}`);
        
        if (!response.ok) {
          throw new Error('Failed to fetch delivery information');
        }
        
        const result = await response.json();
        
        if (result.code === 200 && result.data) {
          // Store delivery information
          this.deliveryInfo = {
            restaurant: {
              id: restaurantId,
              name: restaurantName
            },
            rider: result.data.rider || { name: 'Assigned Rider' },
            delivery_fee: result.data.delivery_fee || 5.00,
            travel_info: result.data.travel_info || {
              duration: '30-45 min',
              distance: '3.5 km'
            },
            price_info: result.data.price_info || {
              base_fare: 3.00,
              time_charge: 1.00,
              distance_surcharge: 1.00
            },
            static_map_url: result.data.static_map_url
          };
        } else {
          // If the service fails, use default values
          this.deliveryInfo = {
            restaurant: {
              id: restaurantId,
              name: restaurantName
            },
            rider: { name: 'Assigned Rider' },
            delivery_fee: 5.00,
            travel_info: {
              duration: '30-45 min',
              distance: '3.5 km'
            },
            price_info: {
              base_fare: 3.00,
              time_charge: 1.00,
              distance_surcharge: 1.00
            }
          };
        }
      } catch (error) {
        console.error('Error fetching delivery info:', error);
        this.error = 'Could not calculate delivery fee. Using default pricing.';
        
        // Set default delivery information
        this.deliveryInfo = {
          delivery_fee: 5.00
        };
      }
    },
    
    async placeOrder() {
      this.isProcessing = true;
      this.error = null;

      try {
        // Get the current user data from localStorage
        const userData = localStorage.getItem('currentUser');
        if (!userData) {
          throw new Error('User not logged in. Please log in to complete checkout.');
        }
        
        const user = JSON.parse(userData);
        const customer_id = user.customer_id;
        
        // Get voucher information if available
        const voucherData = localStorage.getItem('cartDiscount');
        let voucher_id = null;
        let voucher_code = null;
        
        if (voucherData) {
          const voucher = JSON.parse(voucherData);
          voucher_id = voucher.voucher_id || null;
          voucher_code = voucher.code || null;
        }
        
        // Prepare payload for the processCustomerPayment service
        const payload = {
          customer_id: customer_id,
          cart_items: this.cartItems, 
          voucher_id: voucher_id,
          voucher_code: voucher_code,
          loyalty_points_used: this.loyaltyPointsUsed,
          loyalty_status_discount: this.loyaltyStatusDiscountAmount,
          loyalty_status: this.loyaltyStatus,
          subtotal: this.subtotal,
          delivery_fee: this.deliveryInfo.delivery_fee || 0,
          discount_amount: this.discountAmount,
          total_amount: this.totalAmount
        };
        console.log('Sending payload:', JSON.stringify(payload, null, 2));


        // Call the processCustomerPayment microservice
        const response = await fetch('http://localhost:5020/process_payment', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(payload)
        });

        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.message || 'Payment processing failed');
        }

        const result = await response.json();

        if (result.code === 200 && result.data && result.data.checkout_url) {
      // Store order summary in localStorage for confirmation page
          localStorage.setItem('orderSummary', JSON.stringify(result.data.order_summary));
          localStorage.setItem('orderId', result.data.order_id);
          // Add this line to store the transaction ID
          localStorage.setItem('transactionId', result.data.transaction_id);
          
          // Clear cart as we're redirecting to payment
          localStorage.removeItem('cart');
          localStorage.removeItem('cartDiscount');
          
          // Redirect to the Stripe checkout page
          window.location.href = result.data.checkout_url;
        } else {
          throw new Error(result.message || 'Failed to create checkout session');
        }
      } catch (error) {
        console.error('Error placing order:', error);
        this.error = error.message || 'Could not place your order. Please try again.';
        this.isProcessing = false;
      }
    },
    
    reloadPage() {
      window.location.reload();
    }
  },
  async mounted() {
    try {
      this.loading = true;
      
      // Load cart items first
      this.loadCartItems();
      
      // Load user loyalty information
      this.loadUserLoyalty();
      
      // Then fetch delivery info
      if (this.cartItems.length > 0) {
        await this.fetchDeliveryInfo();
      }
      
    } catch (error) {
      console.error('Error initializing checkout:', error);
      this.error = 'Could not load checkout information. Please try again.';
    } finally {
      this.loading = false;
    }
  }
}
</script>

<style scoped>
.checkout-page {
  padding: 2rem 0;
}

.checkout-header {
  margin-bottom: 2rem;
  text-align: center;
}

.checkout-header h1 {
  font-size: 2rem;
  color: var(--secondary-color);
}

/* Loading state styling */
.loading-state {
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

.spinner {
  border: 4px solid rgba(0, 0, 0, 0.1);
  border-left-color: var(--primary-color);
  border-radius: 50%;
  width: 40px;
  height: 40px;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Error state styling */
.error-state {
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

.error-icon {
  font-size: 3rem;
  color: var(--danger-color, #dc3545);
  margin-bottom: 1rem;
}

/* Checkout content layout */
.checkout-content {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
}

@media (max-width: 992px) {
  .checkout-content {
    grid-template-columns: 1fr;
  }
  
  .payment-section {
    grid-column: span 1;
  }
  
  .loyalty-status-info {
    flex-direction: column;
    text-align: center;
  }
};

/* Order summary styling */
.order-summary, .delivery-info, .payment-section {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  margin-bottom: 2rem;
}

.summary-header, .info-header, .payment-header {
  padding: 1.5rem;
  border-bottom: 1px solid #eee;
}

.summary-header h2, .info-header h2, .payment-header h2 {
  font-size: 1.5rem;
  color: var(--secondary-color);
  margin: 0;
}

.summary-content, .info-content, .payment-content {
  padding: 1.5rem;
}

.cart-items {
  margin-bottom: 2rem;
}

.cart-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.75rem 0;
  border-bottom: 1px solid #eee;
}

.item-image {
  width: 50px;
  height: 50px;
  border-radius: 8px;
  overflow: hidden;
  margin-right: 1rem;
}

.item-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.item-details {
  display: flex;
  align-items: center;
  flex: 1;
}

.item-quantity {
  background-color: var(--primary-color);
  color: white;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  margin-right: 0.75rem;
  font-size: 0.9rem;
}

.cost-summary .summary-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.75rem;
}

.summary-row.total {
  margin-top: 1.5rem;
  padding-top: 1rem;
  border-top: 1px solid #eee;
  font-size: 1.2rem;
  font-weight: bold;
}

/* Add background and shadow to card sections */
.order-summary, .delivery-info, .payment-section, .loyalty-section, .loyalty-status-section {
  background-color: #ffffff; /* White background for cards */
  border-radius: 8px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1); /* Subtle shadow for depth */
  overflow: hidden;
  margin-bottom: 2rem;
}

.summary-row.discount {
  color: var(--success-color, #28a745);
}

/* Delivery info styling */
.info-section {
  margin-bottom: 1.5rem;
}

.info-section h3 {
  font-size: 1.2rem;
  margin-bottom: 1rem;
  color: var(--secondary-color);
}

.info-item {
  display: flex;
  align-items: center;
  margin-bottom: 0.5rem;
}

.info-icon {
  margin-right: 0.75rem;
  color: var(--primary-color);
  width: 18px;
  text-align: center;
}

/* Payment section styling */
.payment-section {
  grid-column: span 2;
}

.payment-methods, .loyalty-section {
  margin-bottom: 2rem;
}

.payment-methods h3, .loyalty-section h3 {
  font-size: 1.2rem;
  margin-bottom: 1rem;
  color: var(--secondary-color);
}

.payment-info {
  margin-bottom: 1rem;
}

.payment-logos {
  display: flex;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.payment-logos i {
  font-size: 2rem;
  color: #6c757d;
}

/* Loyalty section styling */
.loyalty-section {
  background-color: #f8f9fa;
  border-radius: 8px;
  padding: 1rem;
  margin-bottom: 2rem;
}

.loyalty-info {
  padding: 0.5rem;
}

.loyalty-control {
  margin: 1rem 0;
}

.loyalty-control label {
  display: block;
  margin-bottom: 0.5rem;
}

.input-with-controls {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  margin: 0.5rem 0;
}

.btn-control {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background-color: var(--primary-color);
  color: white;
  border: none;
  font-size: 0.8rem;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: background-color 0.2s;
}

.btn-control:hover:not(:disabled) {
  background-color: #e84853;
}

.btn-control:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

.points-input {
  width: 80px;
  text-align: center;
  padding: 0.5rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
}

.loyalty-value {
  font-weight: bold;
  color: var(--success-color, #28a745);
  margin-top: 1rem;
}

/* Loyalty Status Section Styling */
.loyalty-status-section {
  background-color: #f8f9fa;
  border-radius: 8px;
  padding: 1rem;
  margin-bottom: 2rem;
}

.loyalty-status-info {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0.5rem;
}

.loyalty-status-badge {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 1rem;
  border-radius: 50%;
  width: 80px;
  height: 80px;
  color: white;
  font-weight: bold;
}

.loyalty-status-badge.bronze {
  background: linear-gradient(135deg, #CD7F32, #b36a1b);
}

.loyalty-status-badge.silver {
  background: linear-gradient(135deg, #C0C0C0, #a0a0a0);
}

.loyalty-status-badge.gold {
  background: linear-gradient(135deg, #FFD700, #d4af37);
}

.loyalty-status-badge i {
  font-size: 1.5rem;
  margin-bottom: 0.25rem;
}

.loyalty-status-details {
  flex: 1;
}

.loyalty-status-details p {
  margin: 0.5rem 0;
}

.discount-value {
  font-weight: bold;
  color: var(--success-color, #28a745);
}

.place-order-btn {
  width: 100%;
  padding: 1rem;
  font-size: 1.1rem;
}

@media (max-width: 992px) {
  .checkout-content {
    grid-template-columns: 1fr;
  }
  
  .payment-section {
    grid-column: span 1;
  }
}
</style>