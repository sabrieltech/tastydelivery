<template>
  <div class="refund-page">
    <div class="container">
      <div class="refund-header">
        <h1>Request a Refund</h1>
        <p>Select an order to request a refund. Refunds are available for orders placed within the last 7 days.</p>
      </div>

      <div v-if="loading" class="loading-state">
        <div class="spinner"></div>
        <p>Loading your eligible orders...</p>
      </div>

      <div v-else-if="error" class="error-state">
        <i class="fas fa-exclamation-circle error-icon"></i>
        <h3>Something went wrong</h3>
        <p>{{ error }}</p>
        <button class="btn btn-primary" @click="loadEligibleOrders">Try Again</button>
      </div>

      <div v-else-if="eligibleOrders.length === 0" class="no-orders-state">
        <i class="fas fa-search empty-icon"></i>
        <h3>No Eligible Orders Found</h3>
        <p>You don't have any orders eligible for refund. Only orders from the past 7 days can be refunded.</p>
        <router-link to="/app/home" class="btn btn-primary">Return to Home</router-link>
      </div>

      <div v-else class="refund-content">
        <!-- Step 1: Select Order -->
        <div v-if="currentStep === 1" class="step-container">
          <div class="step-header">
            <h2>Step 1: Select an Order</h2>
          </div>
          
          <div class="orders-list">
            <div 
              v-for="order in eligibleOrders" 
              :key="order.transaction_id" 
              class="order-card"
              :class="{ 'selected': selectedOrder && selectedOrder.transaction_id === order.transaction_id }"
              @click="selectOrder(order)"
            >
              <div class="order-header">
                <div class="order-id">
                  <span class="label">Order ID:</span>
                  <span class="value">{{ order.transaction_id }}</span>
                </div>
                <div class="order-date">{{ formatDate(order.created_at) }}</div>
              </div>
              
              <div class="order-items">
                <div v-for="(item, index) in order.items" :key="index" class="order-item">
                  <span class="item-quantity">{{ item.quantity }}x</span>
                  <span class="item-name">Item #{{ item.item_id }}</span>
                  <span class="item-price">${{ (item.price_per_item * item.quantity).toFixed(2) }}</span>
                </div>
              </div>
              
              <div class="order-footer">
                <div class="order-total">
                  <span class="label">Total:</span>
                  <span class="value">${{ order.total_price_after_discount.toFixed(2) }}</span>
                </div>
                
                <div class="select-indicator">
                  <i class="fas fa-check-circle" v-if="selectedOrder && selectedOrder.transaction_id === order.transaction_id"></i>
                  <span v-else>Select</span>
                </div>
              </div>
            </div>
          </div>
          
          <div class="step-buttons">
            <button 
              class="btn btn-primary next-btn" 
              :disabled="!selectedOrder" 
              @click="goToStep(2)"
            >
              Continue
            </button>
          </div>
        </div>
        
        <!-- Step 2: Refund Details -->
        <div v-if="currentStep === 2" class="step-container">
          <div class="step-header">
            <h2>Step 2: Refund Details</h2>
          </div>
          
          <div class="order-summary">
            <h3>Order Summary</h3>
            <div class="summary-row">
              <span class="label">Order ID:</span>
              <span class="value">{{ selectedOrder.transaction_id }}</span>
            </div>
            <div class="summary-row">
              <span class="label">Date:</span>
              <span class="value">{{ formatDate(selectedOrder.created_at) }}</span>
            </div>
            <div class="summary-row">
              <span class="label">Total Amount:</span>
              <span class="value">${{ selectedOrder.total_price_after_discount.toFixed(2) }}</span>
            </div>
          </div>
          
          <div class="refund-details">
            <h3>Refund Information</h3>
            
            <div class="form-group">
              <label for="refund-amount">Refund Amount</label>
              <div class="input-group">
                <span class="input-group-text">$</span>
                <input 
                  type="number" 
                  id="refund-amount" 
                  v-model="refundAmount" 
                  :max="selectedOrder.total_price_after_discount" 
                  min="0.01" 
                  step="0.01"
                  class="form-control"
                >
              </div>
              <p class="input-hint" v-if="refundAmount > selectedOrder.total_price_after_discount">
                <i class="fas fa-exclamation-circle"></i>
                Refund amount cannot exceed the order total.
              </p>
            </div>
            
            <div class="form-group">
              <label for="refund-reason">Reason for Refund</label>
              <select id="refund-reason" v-model="refundReason" class="form-control">
                <option value="">-- Select a reason --</option>
                <option value="Order not received">Order not received</option>
                <option value="Incorrect or missing items">Incorrect or missing items</option>
                <option value="Quality issues">Quality issues</option>
                <option value="Late delivery">Late delivery</option>
                <option value="Other">Other</option>
              </select>
            </div>
            
            <div class="form-group" v-if="refundReason === 'Other'">
              <label for="refund-reason-other">Please specify</label>
              <textarea 
                id="refund-reason-other" 
                v-model="refundReasonOther"
                class="form-control"
                rows="3"
                placeholder="Please provide details..."
              ></textarea>
            </div>
          </div>
          
          <div class="step-buttons">
            <button class="btn btn-secondary back-btn" @click="goToStep(1)">
              Back
            </button>
            <button 
              class="btn btn-primary next-btn" 
              :disabled="!isRefundFormValid" 
              @click="goToStep(3)"
            >
              Review Refund
            </button>
          </div>
        </div>
        
        <!-- Step 3: Review and Confirm -->
        <div v-if="currentStep === 3" class="step-container">
          <div class="step-header">
            <h2>Step 3: Review and Confirm</h2>
          </div>
          
          <div class="review-details">
            <div class="review-section">
              <h3>Order Information</h3>
              <div class="review-row">
                <span class="label">Order ID:</span>
                <span class="value">{{ selectedOrder.transaction_id }}</span>
              </div>
              <div class="review-row">
                <span class="label">Date:</span>
                <span class="value">{{ formatDate(selectedOrder.created_at) }}</span>
              </div>
              <div class="review-row">
                <span class="label">Original Total:</span>
                <span class="value">${{ selectedOrder.total_price_after_discount.toFixed(2) }}</span>
              </div>
            </div>
            
            <div class="review-section">
              <h3>Refund Information</h3>
              <div class="review-row highlight">
                <span class="label">Refund Amount:</span>
                <span class="value">${{ refundAmount.toFixed(2) }}</span>
              </div>
              <div class="review-row">
                <span class="label">Reason:</span>
                <span class="value">{{ refundReason }}</span>
              </div>
              <div class="review-row" v-if="refundReason === 'Other'">
                <span class="label">Details:</span>
                <span class="value">{{ refundReasonOther }}</span>
              </div>
              <div class="review-row highlight">
                <span class="label">Loyalty Points Affected:</span>
                <span class="value">-{{ Math.floor(refundAmount) }} points</span>
              </div>
            </div>
            
            <div class="review-section important-notice">
              <h3><i class="fas fa-exclamation-triangle"></i> Important Information</h3>
              <ul>
                <li>Refunds typically process within 5-7 business days.</li>
                <li>Loyalty points earned from this purchase will be deducted.</li>
                <li>Refund will be issued to your original payment method.</li>
                <li>Once submitted, this refund request cannot be modified.</li>
              </ul>
            </div>
          </div>
          
          <div class="step-buttons">
            <button class="btn btn-secondary back-btn" @click="goToStep(2)">
              Back
            </button>
            <button 
              class="btn btn-primary submit-btn" 
              :disabled="isProcessing" 
              @click="submitRefund"
            >
              <span v-if="isProcessing">
                <i class="fas fa-spinner fa-spin"></i>
                Processing...
              </span>
              <span v-else>
                Submit Refund Request
              </span>
            </button>
          </div>
        </div>
        
        <!-- Step 4: Confirmation -->
        <div v-if="currentStep === 4" class="step-container confirmation">
          <div class="confirmation-icon">
            <i class="fas fa-check-circle"></i>
          </div>
          
          <h2>Refund Request Submitted</h2>
          <p class="confirmation-message">
            Your refund request for <strong>${{ refundAmount.toFixed(2) }}</strong> has been successfully submitted.
          </p>
          
          <div class="confirmation-details">
            <div class="details-row">
              <span class="label">Refund ID:</span>
              <span class="value">{{ refundResult.refund_id }}</span>
            </div>
            <div class="details-row">
              <span class="label">Order ID:</span>
              <span class="value">{{ selectedOrder.transaction_id }}</span>
            </div>
            <div class="details-row">
              <span class="label">Status:</span>
              <span class="value status-badge">{{ refundResult.refund_status }}</span>
            </div>
          </div>
          
          <p class="follow-up-instructions">
            You'll receive an email confirmation shortly. Your refund will be processed within 5-7 business days.
          </p>
          
          <div class="action-buttons">
            <router-link to="/app/home" class="btn btn-primary">
              Return to Home
            </router-link>
            <router-link to="/app/orders" class="btn btn-secondary">
              View My Orders
            </router-link>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'RefundPage',
  data() {
    return {
      loading: true,
      error: null,
      currentStep: 1,
      eligibleOrders: [],
      selectedOrder: null,
      refundAmount: 0,
      refundReason: '',
      refundReasonOther: '',
      isProcessing: false,
      refundResult: null
    }
  },
  computed: {
    isRefundFormValid() {
      return (
        this.refundAmount > 0 && 
        this.refundAmount <= (this.selectedOrder?.total_price_after_discount || 0) &&
        this.refundReason &&
        (this.refundReason !== 'Other' || this.refundReasonOther.trim().length > 0)
      );
    }
  },
  methods: {
    formatDate(dateString) {
      const options = { year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit' };
      return new Date(dateString).toLocaleDateString(undefined, options);
    },
    
    // Handle direct refund from order page
    async handleDirectRefund() {
      this.loading = true;
      this.error = null;
      
      try {
        const transactionId = this.$route.query.transaction_id;
        
        // Get the current user data from localStorage
        const userData = localStorage.getItem('currentUser');
        if (!userData) {
          throw new Error('User not logged in. Please log in to process refund.');
        }
        
        // Removed unused variable:
        // const user = JSON.parse(userData);
        
        // Fetch the specific transaction details
        const response = await fetch(`http://localhost:5009/transaction/${transactionId}`, {
          method: 'GET'
        });
        
        if (!response.ok) {
          throw new Error('Failed to fetch transaction details. Please try loading all eligible refunds.');
        }
        
        const result = await response.json();
        
        if (result.code === 200 && result.data) {
          // Create a transaction object with the required structure
          const transaction = result.data;
          
          // Manually set the refund amount to the full amount by default
          this.refundAmount = transaction.total_price_after_discount;
          
          // Set a default reason
          this.refundReason = 'Order not received';
          
          // Get transaction items
          const itemsResponse = await fetch(`http://localhost:5010/transaction_item/transaction/${transactionId}`, {
            method: 'GET'
          });
          
          let items = [];
          if (itemsResponse.ok) {
            const itemsResult = await itemsResponse.json();
            if (itemsResult.code === 200 && itemsResult.data && itemsResult.data.transaction_items) {
              items = itemsResult.data.transaction_items;
            }
          }
          
          // Add items to the transaction
          transaction.items = items;
          
          // Set as selected order and move to step 2 directly
          this.selectedOrder = transaction;
          this.eligibleOrders = [transaction]; // Add to the list as well
          this.goToStep(2);
        } else {
          throw new Error('Invalid transaction data received');
        }
      } catch (error) {
        console.error('Error handling direct refund:', error);
        this.error = error.message || 'Failed to process direct refund. Please try loading all eligible refunds.';
        
        // Fall back to loading all eligible orders
        this.loadEligibleOrders();
      } finally {
        this.loading = false;
      }
    },
    
    async loadEligibleOrders() {
      this.loading = true;
      this.error = null;
      
      try {
        // Get the current user data from localStorage
        const userData = localStorage.getItem('currentUser');
        if (!userData) {
          throw new Error('User not logged in. Please log in to view eligible refunds.');
        }
        
        const user = JSON.parse(userData);
        const customer_id = user.customer_id;
        
        // Call the microservice to get eligible refunds
        const response = await fetch(`http://localhost:5022/eligible_refunds/${customer_id}`);
        
        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.message || 'Failed to load eligible orders');
        }
        
        const result = await response.json();
        
        if (result.code === 200) {
          this.eligibleOrders = result.data.eligible_transactions;
        } else {
          throw new Error(result.message || 'Failed to load eligible orders');
        }
      } catch (error) {
        console.error('Error loading eligible refunds:', error);
        this.error = error.message || 'Could not load eligible orders. Please try again.';
      } finally {
        this.loading = false;
      }
    },
    
    selectOrder(order) {
      this.selectedOrder = order;
      this.refundAmount = order.total_price_after_discount;
    },
    
    goToStep(step) {
      this.currentStep = step;
      
      // Reset error in case there was one from previous attempt
      if (step === 3) {
        this.error = null;
      }
      
      // Scroll to top of page for better UX
      window.scrollTo(0, 0);
    },
    
    async submitRefund() {
      this.isProcessing = true;
      this.error = null;
      
      try {
        // Get the current user data
        const userData = localStorage.getItem('currentUser');
        if (!userData) {
          throw new Error('User not logged in. Please log in to submit a refund.');
        }
        
        const user = JSON.parse(userData);
        const customer_id = user.customer_id;
        
        // Prepare the refund data
        const refundData = {
          transaction_id: this.selectedOrder.transaction_id,
          customer_id: customer_id,
          refund_amount: parseFloat(this.refundAmount),
          refund_reason: this.refundReason === 'Other' ? this.refundReasonOther : this.refundReason
        };
        
        // Call the process_refund microservice
        const response = await fetch('http://localhost:5022/process_refund', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(refundData)
        });
        
        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.message || 'Failed to process refund');
        }
        
        const result = await response.json();
        
        if (result.code === 200) {
          this.refundResult = result.data;
          
          // Move to confirmation step
          this.goToStep(4);
          
          // Update user's loyalty points in localStorage
          if (result.data.loyalty_points_deducted > 0) {
            try {
              const currentUserData = JSON.parse(localStorage.getItem('currentUser'));
              if (currentUserData && currentUserData.loyalty_points) {
                currentUserData.loyalty_points = Math.max(0, currentUserData.loyalty_points - result.data.loyalty_points_deducted);
                localStorage.setItem('currentUser', JSON.stringify(currentUserData));
              }
            } catch (e) {
              console.error('Error updating local loyalty points:', e);
            }
          }
        } else {
          throw new Error(result.message || 'Failed to process refund');
        }
      } catch (error) {
        console.error('Error processing refund:', error);
        this.error = error.message || 'Could not process your refund. Please try again.';
        
        // Scroll to error message
        setTimeout(() => {
          const errorElement = document.querySelector('.error-state');
          if (errorElement) {
            errorElement.scrollIntoView({ behavior: 'smooth' });
          }
        }, 100);
      } finally {
        this.isProcessing = false;
      }
    }
  },
  mounted() {
    // Check if we were redirected from the order page with specific transaction data
    const fromOrderPage = this.$route.query.from_order_page === 'true';
    const transactionId = this.$route.query.transaction_id;
    
    if (fromOrderPage && transactionId) {
      // Handle direct refund from order page
      this.handleDirectRefund();
    } else {
      // Normal flow - load all eligible orders
      this.loadEligibleOrders();
    }
  }
}
</script>

<style scoped>
.refund-page {
  padding: 2rem 0;
}

.refund-header {
  margin-bottom: 2rem;
  text-align: center;
}

.refund-header h1 {
  font-size: 2rem;
  color: var(--secondary-color);
  margin-bottom: 0.5rem;
}

/* Loading state styling */
.loading-state, .error-state, .no-orders-state {
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

.error-icon, .empty-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.error-icon {
  color: var(--danger-color, #dc3545);
}

.empty-icon {
  color: #999;
}

/* Step container styling */
.step-container {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  padding: 2rem;
  margin-bottom: 2rem;
}

.step-header {
  margin-bottom: 1.5rem;
  border-bottom: 1px solid #eee;
  padding-bottom: 1rem;
}

.step-header h2 {
  font-size: 1.5rem;
  color: var(--secondary-color);
  margin: 0;
}

/* Orders list styling */
.orders-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.5rem;
  margin-bottom: 1.5rem;
}

.order-card {
  background-color: #f8f9fa;
  border-radius: 8px;
  padding: 1.5rem;
  cursor: pointer;
  transition: all 0.2s ease;
  border: 2px solid transparent;
}

.order-card:hover {
  background-color: #f0f0f0;
  transform: translateY(-3px);
}

.order-card.selected {
  border-color: var(--primary-color);
  background-color: #fff3f4;
}

.order-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 1rem;
  font-size: 0.9rem;
}

.order-id .label, .order-total .label {
  color: #666;
  margin-right: 0.5rem;
}

.order-date {
  color: #666;
}

.order-items {
  padding: 0.75rem 0;
  border-top: 1px solid #eee;
  border-bottom: 1px solid #eee;
  margin-bottom: 1rem;
  max-height: 150px;
  overflow-y: auto;
}

.order-item {
  display: flex;
  align-items: center;
  margin-bottom: 0.5rem;
}

.item-quantity {
  background-color: var(--primary-color);
  color: white;
  padding: 0.2rem 0.4rem;
  border-radius: 3px;
  margin-right: 0.75rem;
  font-size: 0.8rem;
}

.item-name {
  flex: 1;
}

.item-price {
  font-weight: bold;
}

.order-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.order-total {
  font-weight: bold;
  font-size: 1.1rem;
}

.select-indicator {
  color: var(--primary-color);
}

.select-indicator i {
  font-size: 1.2rem;
}

/* Button controls */
.step-buttons {
  display: flex;
  justify-content: space-between;
  margin-top: 2rem;
  padding-top: 1.5rem;
  border-top: 1px solid #eee;
}

.back-btn, .next-btn, .submit-btn {
  padding: 0.75rem 1.5rem;
  font-size: 1rem;
}

/* Form styling */
.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
}

.form-control {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
}

.input-group {
  display: flex;
  align-items: center;
}

.input-group-text {
  background-color: #f8f9fa;
  border: 1px solid #ddd;
  border-right: none;
  padding: 0.75rem;
  border-radius: 4px 0 0 4px;
}

.input-group .form-control {
  border-radius: 0 4px 4px 0;
}

.input-hint {
  color: var(--danger-color, #dc3545);
  font-size: 0.85rem;
  margin-top: 0.5rem;
}

.input-hint i {
  margin-right: 0.25rem;
}

/* Section styling */
.order-summary, .refund-details, .review-section {
  margin-bottom: 2rem;
  padding: 1.5rem;
  background-color: #f8f9fa;
  border-radius: 8px;
}

.order-summary h3, .refund-details h3, .review-section h3 {
  font-size: 1.2rem;
  margin-bottom: 1rem;
  color: var(--secondary-color);
}

.summary-row, .review-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.75rem;
}

.review-row.highlight {
  font-weight: bold;
  color: var(--primary-color);
}

.review-section.important-notice {
  background-color: #fff8e5;
  border-left: 4px solid #ffc107;
}

.important-notice h3 {
  color: #856404;
}

.important-notice h3 i {
  margin-right: 0.5rem;
}

.important-notice ul {
  padding-left: 1.5rem;
}

.important-notice li {
  margin-bottom: 0.5rem;
}

/* Confirmation styling */
.confirmation {
  text-align: center;
}

.confirmation-icon {
  font-size: 5rem;
  color: var(--success-color, #28a745);
  margin-bottom: 1.5rem;
}

.confirmation h2 {
  font-size: 2rem;
  margin-bottom: 1rem;
}

.confirmation-message {
  font-size: 1.2rem;
  margin-bottom: 2rem;
}

.confirmation-details {
  display: inline-block;
  text-align: left;
  margin: 1.5rem 0;
  padding: 1.5rem;
  background-color: #f8f9fa;
  border-radius: 8px;
}

.details-row {
  margin-bottom: 0.75rem;
}

.details-row .label {
  display: inline-block;
  width: 100px;
  color: #666;
}

.status-badge {
  display: inline-block;
  background-color: var(--success-color, #28a745);
  color: white;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.9rem;
}

.follow-up-instructions {
  margin-bottom: 2rem;
  color: #666;
}

.action-buttons {
  display: flex;
  justify-content: center;
  gap: 1rem;
}

/* Responsive styles */
@media (max-width: 768px) {
  .orders-list {
    grid-template-columns: 1fr;
  }
  
  .step-buttons {
    flex-direction: column-reverse;
    gap: 1rem;
  }
  
  .back-btn, .next-btn, .submit-btn {
    width: 100%;
  }
  
  .action-buttons {
    flex-direction: column;
  }
  
  .action-buttons .btn {
    width: 100%;
  }
}
</style>