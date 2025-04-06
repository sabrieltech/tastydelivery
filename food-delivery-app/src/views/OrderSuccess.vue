<template>
  <div class="order-success">
    <div class="container">
      <div class="success-card">
        <div class="success-icon">
          <i class="fas fa-check-circle"></i>
        </div>
        
        <h1>Order Confirmed!</h1>
        <p class="success-message">Thank you for your order. Your payment has been successfully processed.</p>
        
        <div v-if="loading" class="loading-state">
          <div class="spinner"></div>
          <p>Loading your order details...</p>
        </div>
        
        <div v-else-if="error" class="error-state">
          <i class="fas fa-exclamation-circle error-icon"></i>
          <p>{{ error }}</p>
          <button class="btn btn-primary" @click="reloadPage">Try Again</button>
        </div>
        
        <div v-else class="order-details">
          <div class="detail-row">
            <span class="detail-label">Order ID:</span>
            <span class="detail-value">{{ orderId }}</span>
          </div>
          
          <div v-if="paymentInfo" class="payment-section">
            <h3>Payment Details</h3>
            <div class="detail-row">
              <span class="detail-label">Amount Paid:</span>
              <span class="detail-value">${{ paymentInfo.amount_paid }}</span>
            </div>
            <div class="detail-row">
              <span class="detail-label">Payment ID:</span>
              <span class="detail-value">{{ paymentInfo.payment_intent_id }}</span>
            </div>
          </div>
          
          <div v-if="orderSummary" class="summary-section">
            <h3>Order Summary</h3>
            <div class="detail-row">
              <span class="detail-label">Food Cost:</span>
              <span class="detail-value">${{ orderSummary.food_cost.toFixed(2) }}</span>
            </div>
            <div class="detail-row">
              <span class="detail-label">Delivery Fee:</span>
              <span class="detail-value">${{ orderSummary.delivery_fee.toFixed(2) }}</span>
            </div>
            <div v-if="orderSummary.loyalty_discount > 0" class="detail-row">
              <span class="detail-label">Loyalty Discount:</span>
              <span class="detail-value">-${{ orderSummary.loyalty_discount.toFixed(2) }}</span>
            </div>
            <div v-if="orderSummary.voucher_discount > 0" class="detail-row">
              <span class="detail-label">Voucher Discount:</span>
              <span class="detail-value">-${{ orderSummary.voucher_discount.toFixed(2) }}</span>
            </div>
            <div class="detail-row total">
              <span class="detail-label">Total:</span>
              <span class="detail-value">${{ orderSummary.total_price.toFixed(2) }}</span>
            </div>
          </div>
          
          <div v-if="loyaltyInfo" class="loyalty-section">
            <h3>Loyalty Points</h3>
            <div class="detail-row">
              <span class="detail-label">Points Earned:</span>
              <span class="detail-value">+{{ loyaltyInfo.points_earned }}</span>
            </div>
            <div v-if="loyaltyInfo.points_used > 0" class="detail-row">
              <span class="detail-label">Points Used:</span>
              <span class="detail-value">-{{ loyaltyInfo.points_used }}</span>
            </div>
            <div class="detail-row">
              <span class="detail-label">New Points Balance:</span>
              <span class="detail-value">{{ loyaltyInfo.new_total_points }}</span>
            </div>
            <div class="detail-row">
              <span class="detail-label">Loyalty Status:</span>
              <span class="detail-value loyalty-status">{{ loyaltyInfo.status }}</span>
            </div>
          </div>
        </div>
        
        <div class="action-buttons">
          <router-link to="/app/home" class="btn btn-primary">
            <i class="fas fa-home"></i> Go to Home
          </router-link>
          <router-link to="/app/orders" class="btn btn-secondary">
            <i class="fas fa-list"></i> View All Orders
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'OrderSuccessPage',
  data() {
    return {
      orderId: '',
      sessionId: '',
      orderSummary: null,
      paymentInfo: null,
      loyaltyInfo: null,
      deliveryEstimate: '30-45 minutes',
      loading: true,
      error: null
    }
  },
  methods: {
    getQueryParams() {
      const urlParams = new URLSearchParams(window.location.search);
      this.sessionId = urlParams.get('session_id');
    },
    
    loadOrderSummary() {
      // Load order summary from localStorage (saved during checkout)
      const orderSummaryData = localStorage.getItem('orderSummary');
      if (orderSummaryData) {
        try {
          this.orderSummary = JSON.parse(orderSummaryData);
        } catch (error) {
          console.error('Error parsing order summary:', error);
        }
      }
      
      // Load order ID from localStorage
      this.orderId = localStorage.getItem('orderId') || 'Unknown';
    },
    
    async fetchPaymentStatus() {
      if (!this.sessionId) {
        return;
      }

      // Get the transaction ID from localStorage
      const transactionId = localStorage.getItem('transactionId');
      
      // Log the values being sent to help with debugging
      console.log("Sending to payment_success:", {
        session_id: this.sessionId,
        order_id: this.orderId,
        customer_id: this.getCustomerId(),
        transaction_id: transactionId
      });
      
      try {
        // Call the payment success endpoint to process the successful payment
        const response = await fetch(`http://localhost:5020/payment_success`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            session_id: this.sessionId,
            order_id: this.orderId,
            customer_id: this.getCustomerId(),
            transaction_id: transactionId
          })
        });

        
        if (!response.ok) {
          throw new Error('Failed to process payment status');
        }
        
        const result = await response.json();
        
        if (result.code === 200 && result.data) {
          // Update order ID if returned from API
          if (result.data.order_id) {
            this.orderId = result.data.order_id;
          }
          
          // Set loyalty info
          if (result.data.loyalty) {
            this.loyaltyInfo = result.data.loyalty;
          }
          
          // Update the user's loyalty information in localStorage
          this.updateUserLoyalty();
        }
      } catch (error) {
        console.error('Error fetching payment status:', error);
        this.error = 'Could not verify payment status. Your order might still be processing.';
      }
    },
    
    getCustomerId() {
      const userData = localStorage.getItem('currentUser');
      if (userData) {
        try {
          const user = JSON.parse(userData);
          return user.customer_id;
        } catch (error) {
          console.error('Error parsing user data:', error);
        }
      }
      return null;
    },
    
    updateUserLoyalty() {
      if (!this.loyaltyInfo) return;
      
      const userData = localStorage.getItem('currentUser');
      if (userData) {
        try {
          let user = JSON.parse(userData);
          
          // Update loyalty points and status
          user.loyalty_points = this.loyaltyInfo.new_total_points;
          user.loyalty_status = this.loyaltyInfo.status;
          
          // Save updated user data
          localStorage.setItem('currentUser', JSON.stringify(user));
        } catch (error) {
          console.error('Error updating user loyalty:', error);
        }
      }
    },
    
    clearOrderData() {
      // Clear order data from localStorage after successful order
      setTimeout(() => {
        localStorage.removeItem('orderSummary');
        localStorage.removeItem('orderId');
        localStorage.removeItem('transactionId');
        localStorage.removeItem('cart');
      }, 3000);
    },
    
    reloadPage() {
      window.location.reload();
    }
  },
  async mounted() {
    this.loading = true;
    
    try {
      // Get query parameters
      this.getQueryParams();
      
      // Load order summary from localStorage
      this.loadOrderSummary();
      
      // Fetch payment status if session ID is available
      if (this.sessionId) {
        await this.fetchPaymentStatus();
      }
      
      // Clear order data after a delay
      this.clearOrderData();
    } catch (error) {
      console.error('Error in OrderSuccess mounted:', error);
      this.error = 'An error occurred while loading your order details.';
    } finally {
      this.loading = false;
    }
  }
}
</script>

<style scoped>
.order-success {
  padding: 3rem 0;
}

.success-card {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
  padding: 2.5rem;
  text-align: center;
  max-width: 800px;
  margin: 0 auto;
}

.success-icon {
  font-size: 5rem;
  color: var(--success-color, #28a745);
  margin-bottom: 1.5rem;
}

.success-card h1 {
  color: var(--secondary-color);
  margin-bottom: 1rem;
  font-size: 2.2rem;
}

.success-message {
  font-size: 1.2rem;
  color: #6c757d;
  margin-bottom: 2rem;
}

.loading-state {
  text-align: center;
  margin: 2rem 0;
}

.spinner {
  display: inline-block;
  width: 40px;
  height: 40px;
  border: 4px solid rgba(0, 0, 0, 0.1);
  border-radius: 50%;
  border-top-color: var(--primary-color);
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.error-state {
  color: var(--danger-color, #dc3545);
  margin: 2rem 0;
}

.error-icon {
  font-size: 2rem;
  margin-bottom: 1rem;
}

.order-details {
  text-align: left;
  margin-bottom: 2rem;
}

.payment-section, .summary-section, .loyalty-section {
  margin-top: 1.5rem;
  padding-top: 1.5rem;
  border-top: 1px solid #eee;
}

.payment-section h3, .summary-section h3, .loyalty-section h3, .delivery-info h3 {
  font-size: 1.3rem;
  margin-bottom: 1rem;
  color: var(--secondary-color);
}

.detail-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.5rem;
}

.detail-label {
  color: #6c757d;
}

.detail-value {
  font-weight: 500;
}

.detail-row.total {
  margin-top: 1rem;
  padding-top: 0.5rem;
  border-top: 1px solid #eee;
  font-weight: bold;
  font-size: 1.1rem;
}

.loyalty-status {
  color: var(--primary-color);
  font-weight: bold;
}

.delivery-info {
  background-color: #f8f9fa;
  border-radius: 8px;
  padding: 1.5rem;
  margin-bottom: 2rem;
  text-align: left;
}

.info-text {
  margin-bottom: 0.5rem;
}

.info-text i {
  color: var(--primary-color);
  margin-right: 0.5rem;
}

.action-buttons {
  display: flex;
  justify-content: center;
  gap: 1rem;
}

.btn {
  padding: 0.75rem 1.5rem;
  border-radius: 50px;
  display: inline-flex;
  align-items: center;
  font-weight: 500;
  transition: all 0.3s ease;
}

.btn i {
  margin-right: 0.5rem;
}

.btn-primary {
  background-color: var(--primary-color);
  color: white;
}

.btn-primary:hover {
  background-color: #e84853;
  transform: translateY(-2px);
}

.btn-secondary {
  background-color: white;
  color: var(--primary-color);
  border: 1px solid var(--primary-color);
}

.btn-secondary:hover {
  background-color: #f8f9fa;
  transform: translateY(-2px);
}

@media (max-width: 768px) {
  .success-card {
    padding: 1.5rem;
  }
  
  .action-buttons {
    flex-direction: column;
    gap: 0.75rem;
  }
  
  .btn {
    width: 100%;
    justify-content: center;
  }
}
</style>