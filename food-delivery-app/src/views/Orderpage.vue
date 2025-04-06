<template>
  <div class="order-detail-page">
    <div class="container">
      <div v-if="isLoading" class="loading-container">
        <p><i class="fas fa-spinner fa-spin"></i> Loading Order Details...</p>
      </div>
      <div v-else-if="error" class="error-container">
        <p>{{ error }}</p>
        <button @click="$router.go(-1)" class="btn btn-secondary">
          <i class="fas fa-arrow-left"></i> Go Back
        </button>
      </div>
      <div v-else class="order-detail-container">
        <div class="order-header">
          <div class="header-left">
            <h1>Order #{{ orderId }}</h1>
            <p class="order-date">{{ formatDate(orderDetails.transaction_date) }}</p>
          </div>
          <div class="order-status" :class="orderStatusClass">
            {{ orderDetails.status || 'Completed' }}
          </div>
        </div>
        
        <div class="order-content">
          <!-- Left column - Order details -->
          <div class="order-summary-card">
            <div class="restaurant-info">
              <div class="restaurant-image" v-if="orderDetails.restaurant_image">
                <img :src="orderDetails.restaurant_image" :alt="orderDetails.restaurant_name">
              </div>
              <div class="restaurant-details">
                <h2>{{ orderDetails.restaurant_name || 'Restaurant' }}</h2>
                <p v-if="orderDetails.restaurant_phone">
                  <i class="fas fa-phone"></i> {{ orderDetails.restaurant_phone }}
                </p>
                <p v-if="orderDetails.restaurant_address">
                  <i class="fas fa-map-marker-alt"></i> {{ orderDetails.restaurant_address }}
                </p>
              </div>
            </div>
            
            <div class="items-list">
              <h3><i class="fas fa-utensils"></i> Order Items</h3>
              <div class="item" v-for="(item, index) in orderDetails.items" :key="index">
                <div class="item-image" v-if="item.image_url">
                  <img :src="item.image_url" :alt="item.item_name">
                </div>
                <div class="item-quantity">{{ item.quantity }}x</div>
                <div class="item-details">
                  <div class="item-name">{{ item.item_name }}</div>
                  <div class="item-description" v-if="item.description">{{ item.description }}</div>
                  <div class="item-options" v-if="item.options && item.options.length">
                    <small>{{ formatOptions(item.options) }}</small>
                  </div>
                </div>
                <div class="item-price">${{ (item.price * item.quantity).toFixed(2) }}</div>
              </div>
            </div>
            
            <div class="order-pricing">
              <div class="price-row">
                <span>Subtotal:</span>
                <span>${{ orderDetails.subtotal?.toFixed(2) }}</span>
              </div>
              <div class="price-row">
                <span>Delivery Fee:</span>
                <span>${{ orderDetails.delivery_fee?.toFixed(2) }}</span>
              </div>
              <div class="price-row discount" v-if="orderDetails.loyalty_discount > 0">
                <span>Loyalty Discount ({{ orderDetails.loyalty_status }}):</span>
                <span>-${{ orderDetails.loyalty_discount?.toFixed(2) }}</span>
              </div>
              <div class="price-row discount" v-if="orderDetails.voucher_discount > 0">
                <span>Voucher Discount
                  <span v-if="orderDetails.voucher_code">({{ orderDetails.voucher_code }})</span>:
                </span>
                <span>-${{ orderDetails.voucher_discount?.toFixed(2) }}</span>
              </div>
              <div class="price-row discount" v-if="orderDetails.loyalty_points_used > 0">
                <span>Loyalty Points ({{ orderDetails.loyalty_points_used }} pts):</span>
                <span>-${{ (orderDetails.loyalty_points_used * 0.1).toFixed(2) }}</span>
              </div>
              <div class="price-row" v-if="orderDetails.tax">
                <span>Tax:</span>
                <span>${{ orderDetails.tax?.toFixed(2) }}</span>
              </div>
              <div class="price-row total">
                <span>Total:</span>
                <span>${{ orderDetails.total_price?.toFixed(2) }}</span>
              </div>
              <div class="payment-info">
                <p><i class="fas fa-credit-card"></i> {{ orderDetails.payment_method || 'Credit Card' }}</p>
                <p v-if="orderDetails.loyalty_points_earned">
                  <i class="fas fa-crown"></i> {{ orderDetails.loyalty_points_earned }} points earned
                </p>
              </div>
            </div>
          </div>
          
          <!-- Right column - Delivery details -->
          <div class="delivery-details-card">
            <h3><i class="fas fa-truck"></i> Delivery Information</h3>
            
            <div class="detail-section">
              <h4>Delivery Address</h4>
              <p>{{ orderDetails.delivery_details?.address || 'No address provided' }}</p>
            </div>
            


            <div class="detail-section" v-if="orderDetails.customer_name">
              <h4>Customer Information</h4>
              <p><strong>Name:</strong> {{ orderDetails.customer_name }}</p>
              <p v-if="orderDetails.customer_phone"><strong>Phone:</strong> {{ orderDetails.customer_phone }}</p>
            </div>
            
            <!-- Loyalty Status Section -->
            <div class="detail-section loyalty-section">
              <h4>Loyalty Status</h4>
              <div class="loyalty-badge" :class="loyaltyClass">
                <i class="fas fa-crown"></i>
                <span>{{ orderDetails.loyalty_status }}</span>
              </div>
            </div>
          </div>
        </div>
        
        <div class="actions">
          <button class="btn btn-secondary" @click="$router.go(-1)">
            <i class="fas fa-arrow-left"></i> Back
          </button>
          <button class="btn btn-primary" @click="reorder">
            <i class="fas fa-redo"></i> Reorder
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'OrderPage',
  data() {
    return {
      orderId: this.$route.params.id,
      orderDetails: {},
      isLoading: true,
      error: null
    }
  },
  computed: {
    orderStatusClass() {
      const status = (this.orderDetails.status || '').toLowerCase();
      if (status === 'delivered' || status === 'completed' || status === 'paid') {
        return 'status-completed';
      } else if (status === 'cancelled' || status === 'refunded') {
        return 'status-cancelled';
      } else if (status === 'pending' || status === 'submitted') {
        return 'status-pending';
      }
      return '';
    },
    loyaltyClass() {
      const status = this.orderDetails.loyalty_status || 'Bronze';
      return `loyalty-${status.toLowerCase()}`;
    }
  },
  methods: {
    async fetchOrderDetails() {
      this.isLoading = true;
      this.error = null;
      
      try {
        const response = await fetch(`http://localhost:5014/order/${this.orderId}`);
        
        if (!response.ok) {
          throw new Error(`Error ${response.status}: ${response.statusText}`);
        }
        
        const result = await response.json();
        
        if (result.code === 200 && result.data) {
          this.orderDetails = result.data;
          console.log("Order details:", this.orderDetails);
        } else {
          throw new Error(result.message || 'Could not load order details');
        }
      } catch (error) {
        console.error('Error fetching order details:', error);
        this.error = `Failed to load order details: ${error.message}`;
      } finally {
        this.isLoading = false;
      }
    },
    formatDate(dateString) {
      if (!dateString) return '';
      const options = { 
        year: 'numeric', 
        month: 'long', 
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      };
      return new Date(dateString).toLocaleString(undefined, options);
    },
    formatOptions(options) {
      if (!options || !options.length) return '';
      return options.map(opt => `${opt.name}: ${opt.value}`).join(', ');
    },
    reorder() {
      if (!this.orderDetails || !this.orderDetails.items) {
        alert('Cannot reorder: No items found in this order');
        return;
      }
      
      try {
        // Get current cart items
        const currentCartData = localStorage.getItem('cart');
        let cartItems = currentCartData ? JSON.parse(currentCartData) : [];
        
        // Add items from this order to cart
        const orderItems = this.orderDetails.items.map(item => ({
          item_id: item.item_id,
          restaurant_id: item.restaurant_id,
          restaurant_name: this.orderDetails.restaurant_name,
          item_name: item.item_name,
          price: item.price,
          quantity: item.quantity,
          image_url: item.image_url,
          totalPrice: item.price * item.quantity
        }));
        
        // Combine with existing cart
        cartItems = [...cartItems, ...orderItems];
        
        // Save to localStorage
        localStorage.setItem('cart', JSON.stringify(cartItems));
        
        // Show success message and redirect to cart
        alert('Items have been added to your cart!');
        this.$router.push('/cart');
      } catch (error) {
        console.error('Error reordering:', error);
        alert('Failed to add items to cart. Please try again.');
      }
    },
    cancelOrder() {
      if (confirm('Are you sure you want to cancel this order?')) {
        // Add direct cancellation logic here instead of redirecting to refund page
        alert('Your order has been cancelled.');
        // You may want to update the order status locally or make an API call to cancel
        this.orderDetails.status = 'Cancelled';
      }
    }
  },
  mounted() {
    this.fetchOrderDetails();
  }
}
</script>

<style scoped>
.order-detail-page {
  padding: 2rem 0;
}

.loading-container, .error-container {
  text-align: center;
  padding: 2rem;
  background-color: #f8f9fa;
  border-radius: 8px;
  margin-bottom: 2rem;
}

.error-container {
  color: #dc3545;
}

.order-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1.5rem;
}

.header-left {
  display: flex;
  flex-direction: column;
}

.header-left h1 {
  margin-bottom: 0.5rem;
}

.order-date {
  font-size: 0.9rem;
  color: #6c757d;
}

.order-status {
  padding: 0.5rem 1rem;
  border-radius: 20px;
  font-weight: bold;
  text-transform: uppercase;
  font-size: 0.85rem;
}

.status-completed {
  background-color: #d4edda;
  color: #155724;
}

.status-cancelled {
  background-color: #f8d7da;
  color: #721c24;
}

.status-pending {
  background-color: #fff3cd;
  color: #856404;
}

.order-content {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 1.5rem;
  margin-bottom: 2rem;
}

@media (max-width: 992px) {
  .order-content {
    grid-template-columns: 1fr;
  }
}

.order-summary-card, .delivery-details-card {
  background-color: white;
  border-radius: 8px;
  padding: 2rem;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.restaurant-info {
  display: flex;
  align-items: center;
  margin-bottom: 1.5rem;
  padding-bottom: 1.5rem;
  border-bottom: 1px solid #eee;
}

.restaurant-image {
  width: 80px;
  height: 80px;
  border-radius: 8px;
  overflow: hidden;
  margin-right: 1rem;
}

.restaurant-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.restaurant-details h2 {
  margin-bottom: 0.5rem;
}

.restaurant-details p {
  margin-bottom: 0.25rem;
  color: #6c757d;
}

.restaurant-details i {
  margin-right: 0.5rem;
}

.items-list {
  margin-bottom: 1.5rem;
  padding-bottom: 1.5rem;
  border-bottom: 1px solid #eee;
}

.items-list h3, .delivery-details-card h3 {
  margin-bottom: 1rem;
  font-size: 1.2rem;
}

.item {
  display: flex;
  align-items: flex-start;
  padding: 0.75rem 0;
  border-bottom: 1px solid #f5f5f5;
}

.item:last-child {
  border-bottom: none;
}

.item-image {
  width: 50px;
  height: 50px;
  border-radius: 8px;
  overflow: hidden;
  margin-right: 0.75rem;
}

.item-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.item-quantity {
  font-weight: bold;
  min-width: 40px;
}

.item-details {
  flex-grow: 1;
}

.item-name {
  font-weight: 500;
}

.item-description {
  font-size: 0.85rem;
  color: #6c757d;
  margin-top: 0.25rem;
}

.item-options {
  color: #6c757d;
  margin-top: 0.25rem;
}

.item-price {
  font-weight: bold;
  text-align: right;
  min-width: 80px;
}

.order-pricing {
  padding-top: 1rem;
}

.price-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.5rem;
}

.price-row.discount {
  color: #28a745;
}

.price-row.total {
  font-weight: bold;
  font-size: 1.25rem;
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 2px solid #eee;
  margin-bottom: 1rem;
}

.payment-info {
  margin-top: 1rem;
  color: #6c757d;
}

.payment-info p {
  margin-bottom: 0.5rem;
}

.payment-info i {
  margin-right: 0.5rem;
}

.detail-section {
  margin-bottom: 1.5rem;
}

.detail-section h4 {
  font-size: 1rem;
  margin-bottom: 0.5rem;
  color: #495057;
}

.detail-section p {
  margin-bottom: 0.5rem;
}

.loyalty-section {
  text-align: center;
}

.loyalty-badge {
  display: inline-flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 100px;
  height: 100px;
  border-radius: 50%;
  color: white;
  margin: 0 auto;
}

.loyalty-badge i {
  font-size: 2rem;
  margin-bottom: 0.5rem;
}

.loyalty-bronze {
  background: linear-gradient(135deg, #CD7F32, #b36a1b);
}

.loyalty-silver {
  background: linear-gradient(135deg, #C0C0C0, #a0a0a0);
}

.loyalty-gold {
  background: linear-gradient(135deg, #FFD700, #d4af37);
}

.actions {
  display: flex;
  justify-content: space-between;
}

.btn {
  padding: 0.75rem 1.5rem;
  border-radius: 4px;
  font-weight: 600;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
}

.btn i {
  margin-right: 0.5rem;
}

.btn-primary {
  background-color: var(--primary-color, #ff5a5f);
  color: white;
  border: none;
}

.btn-secondary {
  background-color: #f8f9fa;
  color: #212529;
  border: 1px solid #dee2e6;
}

.btn-primary:hover {
  background-color: #e24c50;
}

.btn-secondary:hover {
  background-color: #e2e6ea;
}

.btn-danger {
  background-color: #dc3545;
  color: white;
  border: none;
}

.btn-danger:hover {
  background-color: #c82333;
}

@media (max-width: 768px) {
  .order-header {
    flex-direction: column;
  }
  
  .order-status {
    margin-top: 1rem;
    align-self: flex-start;
  }
  
  .restaurant-info {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .restaurant-image {
    margin-bottom: 1rem;
  }
  
  .item {
    flex-wrap: wrap;
  }
  
  .item-price {
    width: 100%;
    text-align: left;
    margin-top: 0.5rem;
  }
}
</style>