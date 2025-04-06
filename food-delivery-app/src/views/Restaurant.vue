<template>
  <div class="restaurant-dashboard">
    <div class="container">
      <div class="dashboard-header">
        <h1>Restaurant Dashboard</h1>
        <p class="subtitle">Manage incoming orders and delivery requests</p>
      </div>

      <!-- Stats overview -->
      <div class="stats-overview">
        <div class="stat-card">
          <div class="stat-icon pending">
            <i class="fas fa-hourglass-half"></i>
          </div>
          <div class="stat-info">
            <h3>{{ pendingOrdersCount }}</h3>
            <p>Pending Orders</p>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon completed">
            <i class="fas fa-check-circle"></i>
          </div>
          <div class="stat-info">
            <h3>{{ completedOrdersCount }}</h3>
            <p>Completed Today</p>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon revenue">
            <i class="fas fa-dollar-sign"></i>
          </div>
          <div class="stat-info">
            <h3>${{ todaysRevenue.toFixed(2) }}</h3>
            <p>Today's Revenue</p>
          </div>
        </div>
      </div>

      <!-- New Orders Section -->
      <div class="orders-section">
        <div class="section-header">
          <h2>
            <i class="fas fa-bell"></i> New Orders
            <span v-if="newOrders.length > 0" class="orders-count">{{ newOrders.length }}</span>
          </h2>
          <div class="refresh-control">
            <button @click="fetchOrders" class="refresh-btn" :class="{ 'refreshing': isRefreshing }">
              <i class="fas fa-sync-alt"></i>
              <span>Refresh</span>
            </button>
            <div class="auto-refresh">
              <input type="checkbox" id="auto-refresh" v-model="autoRefresh">
              <label for="auto-refresh">Auto-refresh</label>
            </div>
          </div>
        </div>

        <div v-if="isLoading" class="loading-container">
          <div class="spinner"></div>
          <p>Loading orders...</p>
        </div>

        <div v-else-if="error" class="error-container">
          <i class="fas fa-exclamation-circle"></i>
          <p>{{ error }}</p>
          <button @click="fetchOrders" class="btn btn-primary">Try Again</button>
        </div>

        <div v-else-if="newOrders.length === 0" class="empty-state">
          <i class="fas fa-bell-slash"></i>
          <p>No new orders at the moment</p>
          <p class="empty-hint">New orders will appear here when customers place them</p>
        </div>

        <div v-else class="orders-list">
          <div v-for="order in newOrders" :key="order.notification_id" class="order-card">
            <div class="order-header">
              <div class="order-type" :class="getOrderTypeClass(order)">
                <i :class="getOrderTypeIcon(order)"></i>
                <span>{{ getOrderTypeText(order) }}</span>
              </div>
              <div class="order-time">{{ formatTime(order.created_at) }}</div>
            </div>

            <div class="order-content">
              <div v-if="order.transaction_id" class="order-number">
                <span class="label">Order ID:</span>
                <span class="value">{{ order.transaction_id }}</span>
              </div>

              <div class="order-customer" v-if="customerDetails[order.customer_id]">
                <span class="label">Customer:</span>
                <span class="value">{{ customerDetails[order.customer_id].name }}</span>
              </div>

              <div class="order-items" v-if="orderItems[order.transaction_id]">
                <span class="label">Items:</span>
                <ul class="items-list">
                  <li v-for="(item, index) in orderItems[order.transaction_id]" :key="index">
                    {{ item.quantity }}x {{ getItemName(item.item_id) }} 
                    <span class="item-price">${{ (item.price_per_item * item.quantity).toFixed(2) }}</span>
                  </li>
                </ul>
              </div>

              <div class="order-total" v-if="transactionDetails[order.transaction_id]">
                <span class="label">Total:</span>
                <span class="value">${{ transactionDetails[order.transaction_id].total_price_after_discount.toFixed(2) }}</span>
              </div>
            </div>

            <div class="order-actions">
              <button 
                @click="acceptOrder(order)" 
                class="btn btn-success"
                :disabled="isProcessingAction[order.notification_id]"
              >
                <i class="fas fa-check"></i> Accept Order
              </button>
              <button 
                @click="rejectOrder(order)" 
                class="btn btn-danger"
                :disabled="isProcessingAction[order.notification_id]"
              >
                <i class="fas fa-times"></i> Reject Order
              </button>
            </div>

            <div v-if="isProcessingAction[order.notification_id]" class="processing-overlay">
              <div class="spinner"></div>
              <p>Processing...</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Processing Orders Section -->
      <div class="orders-section">
        <div class="section-header">
          <h2>
            <i class="fas fa-clock"></i> Processing Orders
            <span v-if="processingOrders.length > 0" class="orders-count">{{ processingOrders.length }}</span>
          </h2>
        </div>

        <div v-if="processingOrders.length === 0" class="empty-state">
          <i class="fas fa-hourglass-empty"></i>
          <p>No orders being processed</p>
        </div>

        <div v-else class="orders-list">
          <div v-for="order in processingOrders" :key="order.transaction_id" class="order-card">
            <div class="order-header">
              <div class="order-type processing">
                <i class="fas fa-hourglass-half"></i>
                <span>Processing</span>
              </div>
              <div class="order-time">{{ formatTime(order.created_at) }}</div>
            </div>

            <div class="order-content">
              <div class="order-number">
                <span class="label">Order ID:</span>
                <span class="value">{{ order.transaction_id }}</span>
              </div>

              <div class="order-customer" v-if="customerDetails[order.customer_id]">
                <span class="label">Customer:</span>
                <span class="value">{{ customerDetails[order.customer_id].name }}</span>
              </div>

              <div class="order-items" v-if="orderItems[order.transaction_id]">
                <span class="label">Items:</span>
                <ul class="items-list">
                  <li v-for="(item, index) in orderItems[order.transaction_id]" :key="index">
                    {{ item.quantity }}x {{ getItemName(item.item_id) }} 
                    <span class="item-price">${{ (item.price_per_item * item.quantity).toFixed(2) }}</span>
                  </li>
                </ul>
              </div>

              <div class="order-total">
                <span class="label">Total:</span>
                <span class="value">${{ order.total_price_after_discount.toFixed(2) }}</span>
              </div>
            </div>

            <div class="order-actions">
              <button 
                @click="completeOrder(order)" 
                class="btn btn-primary"
                :disabled="processingAction === order.transaction_id"
              >
                <i class="fas fa-check-double"></i> Mark as Completed
              </button>
            </div>

            <div v-if="processingAction === order.transaction_id" class="processing-overlay">
              <div class="spinner"></div>
              <p>Processing...</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Action Confirmation Modal -->
      <div v-if="showModal" class="modal-overlay">
        <div class="modal-content">
          <div class="modal-header">
            <h3>{{ modalTitle }}</h3>
            <button class="close-btn" @click="closeModal">
              <i class="fas fa-times"></i>
            </button>
          </div>
          <div class="modal-body">
            <p>{{ modalMessage }}</p>
            <p v-if="modalActionType === 'reject'" class="rejection-warning">
              <i class="fas fa-exclamation-triangle"></i> 
              This will refund the customer and cancel the order.
            </p>
          </div>
          <div class="modal-footer">
            <button class="btn btn-secondary" @click="closeModal">Cancel</button>
            <button 
              class="btn" 
              :class="{'btn-success': modalActionType === 'accept', 'btn-danger': modalActionType === 'reject', 'btn-primary': modalActionType === 'complete'}"
              @click="confirmAction"
            >
              {{ modalActionType === 'accept' ? 'Accept Order' : modalActionType === 'reject' ? 'Reject Order' : 'Complete Order' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'RestaurantDashboard',
  data() {
    return {
      newOrders: [],
      processingOrders: [],
      completedOrders: [],
      isLoading: true,
      isRefreshing: false,
      error: null,
      autoRefresh: true,
      refreshInterval: null,
      customerDetails: {},  // Store customer details by customer_id
      transactionDetails: {}, // Store transaction details by transaction_id
      orderItems: {}, // Store order items by transaction_id
      inventoryItems: {}, // Store inventory details by item_id
      showModal: false,
      modalActionType: '', // 'accept', 'reject', or 'complete'
      modalTitle: '',
      modalMessage: '',
      selectedOrder: null,
      isProcessingAction: {}, // Track processing state by notification_id
      processingAction: null, // Track processing for completed orders
      restaurantId: 'REST001', // Default restaurant ID - would come from authentication
      refreshRate: 30000 // 30 seconds
    }
  },
  computed: {
    pendingOrdersCount() {
      return this.newOrders.length;
    },
    completedOrdersCount() {
      return this.completedOrders.length;
    },
    todaysRevenue() {
      return this.completedOrders.reduce((total, order) => {
        return total + parseFloat(order.total_price_after_discount || 0);
      }, 0);
    }
  },
  methods: {
    async fetchOrders() {
      if (this.isRefreshing) return;
      
      this.isRefreshing = true;
      if (!this.isLoading) {
        this.error = null;
      }
      
      try {
        // 1. Fetch all new notifications (Payment_Success type) for the restaurant
        const notificationsResponse = await fetch('http://localhost:5011/notification');
        if (!notificationsResponse.ok) {
          throw new Error('Failed to fetch notifications');
        }
        
        const notificationsResult = await notificationsResponse.json();
        
        if (notificationsResult.code === 200) {
          // Filter for Payment_Success notifications that are unread
          const paymentNotifications = notificationsResult.data.notifications.filter(
            notification => notification.message_type === 'Payment_Success' && notification.status === 'Unread'
          );
          
          // Store the filtered notifications
          this.newOrders = paymentNotifications;
          
          // For each notification, fetch additional data
          await this.fetchAdditionalData(paymentNotifications);
          
          // Fetch processing orders (transactions with "Paid" status)
          await this.fetchProcessingOrders();
          
          // Fetch completed orders for today
          await this.fetchCompletedOrders();
          
        } else {
          throw new Error('Invalid response from notifications service');
        }
      } catch (error) {
        console.error('Error fetching orders:', error);
        this.error = 'Failed to load orders. Please try again.';
      } finally {
        this.isLoading = false;
        this.isRefreshing = false;
      }
    },
    
    async fetchAdditionalData(notifications) {
      try {
        // Create arrays of unique IDs
        const transactionIds = [...new Set(notifications.map(n => n.transaction_id).filter(Boolean))];
        const customerIds = [...new Set(notifications.map(n => n.customer_id).filter(Boolean))];
        
        // Fetch transactions details
        for (const transactionId of transactionIds) {
          if (!this.transactionDetails[transactionId]) {
            const transactionResponse = await fetch(`http://localhost:5009/transaction/${transactionId}`);
            if (transactionResponse.ok) {
              const transactionResult = await transactionResponse.json();
              if (transactionResult.code === 200) {
                this.transactionDetails[transactionId] = transactionResult.data;
                
                // Also fetch items for this transaction
                await this.fetchTransactionItems(transactionId);
              }
            }
          }
        }
        
        // Fetch customer details
        for (const customerId of customerIds) {
          if (!this.customerDetails[customerId]) {
            const customerResponse = await fetch(`http://localhost:5006/customer/${customerId}`);
            if (customerResponse.ok) {
              const customerResult = await customerResponse.json();
              if (customerResult.code === 200) {
                this.customerDetails[customerId] = customerResult.data;
              }
            }
          }
        }
        
      } catch (error) {
        console.error('Error fetching additional data:', error);
      }
    },
    
    async fetchTransactionItems(transactionId) {
      try {
        const itemsResponse = await fetch(`http://localhost:5010/transaction_item/transaction/${transactionId}`);
        if (itemsResponse.ok) {
          const itemsResult = await itemsResponse.json();
          if (itemsResult.code === 200 && itemsResult.data.transaction_items) {
            this.orderItems[transactionId] = itemsResult.data.transaction_items;
            
            // For each item, fetch inventory details if needed
            for (const item of itemsResult.data.transaction_items) {
              if (!this.inventoryItems[item.item_id]) {
                await this.fetchInventoryItem(item.item_id);
              }
            }
          }
        }
      } catch (error) {
        console.error(`Error fetching items for transaction ${transactionId}:`, error);
      }
    },
    
    async fetchInventoryItem(itemId) {
      try {
        const itemResponse = await fetch(`http://localhost:5008/restaurant_inventory/${itemId}`);
        if (itemResponse.ok) {
          const itemResult = await itemResponse.json();
          if (itemResult.code === 200) {
            this.inventoryItems[itemId] = itemResult.data;
          }
        }
      } catch (error) {
        console.error(`Error fetching inventory item ${itemId}:`, error);
      }
    },
    
    async fetchProcessingOrders() {
      try {
        // Fetch transactions with "Paid" status 
        const transactionsResponse = await fetch(`http://localhost:5009/transaction/status/Paid`);
        if (transactionsResponse.ok) {
          const transactionsResult = await transactionsResponse.json();
          
          if (transactionsResult.code === 200 && transactionsResult.data.transactions) {
            // Filter for transactions related to this restaurant
            // In a real app, you would have a proper way to filter transactions for the current restaurant
            this.processingOrders = transactionsResult.data.transactions.filter(
              transaction => this.isTransactionForRestaurant(transaction)
            );
            
            // Fetch additional data for these orders if needed
            for (const order of this.processingOrders) {
              if (!this.orderItems[order.transaction_id]) {
                await this.fetchTransactionItems(order.transaction_id);
              }
              
              if (!this.customerDetails[order.customer_id]) {
                const customerResponse = await fetch(`http://localhost:5006/customer/${order.customer_id}`);
                if (customerResponse.ok) {
                  const customerResult = await customerResponse.json();
                  if (customerResult.code === 200) {
                    this.customerDetails[order.customer_id] = customerResult.data;
                  }
                }
              }
            }
          }
        }
      } catch (error) {
        console.error('Error fetching processing orders:', error);
      }
    },
    
    async fetchCompletedOrders() {
      try {
        // Fetch transactions with "Completed" status
        const completedResponse = await fetch(`http://localhost:5009/transaction/status/Delivered`);
        if (completedResponse.ok) {
          const completedResult = await completedResponse.json();
          
          if (completedResult.code === 200 && completedResult.data.transactions) {
            // Filter for today's orders and for this restaurant
            const today = new Date().toISOString().split('T')[0]; // YYYY-MM-DD
            
            this.completedOrders = completedResult.data.transactions.filter(
              transaction => {
                const transactionDate = transaction.created_at.split(' ')[0]; // Extract YYYY-MM-DD
                return transactionDate === today && this.isTransactionForRestaurant(transaction);
              }
            );
          }
        }
      } catch (error) {
        console.error('Error fetching completed orders:', error);
      }
    },
    
    isTransactionForRestaurant(transaction) {
      // In a real app, you would check if the transaction is for the current restaurant
      // For this example, we'll assume that transactions with items for restaurant_id matching
      // this.restaurantId are relevant
      if (transaction.transaction_id in this.orderItems) {
        return this.orderItems[transaction.transaction_id].some(
          item => item.restaurant_id === this.restaurantId
        );
      }
      
      // If we don't have the items yet, assume it's for this restaurant
      // In a real app, you'd have a proper way to filter
      return true;
    },
    
    getItemName(itemId) {
      if (this.inventoryItems[itemId]) {
        return this.inventoryItems[itemId].item_name;
      }
      return `Item #${itemId}`;
    },
    
    formatTime(timestamp) {
      if (!timestamp) return '';
      
      const date = new Date(timestamp);
      return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    },
    
    // eslint-disable-next-line no-unused-vars
    getOrderTypeClass(order) {
      return 'new-order';
    },
    
    // eslint-disable-next-line no-unused-vars
    getOrderTypeIcon(order) {
      return 'fas fa-shopping-bag';
    },
    
    // eslint-disable-next-line no-unused-vars
    getOrderTypeText(order) {
      return 'New Order';
    },
    
    acceptOrder(order) {
      // eslint-disable-next-line no-unused-vars
      this.selectedOrder = order;
      this.modalActionType = 'accept';
      this.modalTitle = 'Accept Order';
      this.modalMessage = `Are you sure you want to accept order ${order.transaction_id}?`;
      this.showModal = true;
    },
    
    rejectOrder(order) {
      // eslint-disable-next-line no-unused-vars
      this.selectedOrder = order;
      this.modalActionType = 'reject';
      this.modalTitle = 'Reject Order';
      this.modalMessage = `Are you sure you want to reject order ${order.transaction_id}?`;
      this.showModal = true;
    },
    
    completeOrder(order) {
      // eslint-disable-next-line no-unused-vars
      this.selectedOrder = order;
      this.modalActionType = 'complete';
      this.modalTitle = 'Complete Order';
      this.modalMessage = `Mark order ${order.transaction_id} as completed?`;
      this.showModal = true;
    },
    
    closeModal() {
      this.showModal = false;
      this.selectedOrder = null;
    },
    
    async confirmAction() {
      if (!this.selectedOrder) {
        this.closeModal();
        return;
      }
      
      if (this.modalActionType === 'accept') {
        await this.processAcceptOrder();
      } else if (this.modalActionType === 'reject') {
        await this.processRejectOrder();
      } else if (this.modalActionType === 'complete') {
        await this.processCompleteOrder();
      }
      
      this.closeModal();
    },
    
    async processAcceptOrder() {
      const order = this.selectedOrder;
      
      // Set processing state for this order
      this.$set(this.isProcessingAction, order.notification_id, true);
      
      try {
        // 1. Mark notification as read
        const notificationResponse = await fetch(`http://localhost:5011/notification/${order.notification_id}/read`, {
          method: 'PUT'
        });
        
        if (!notificationResponse.ok) {
          throw new Error('Failed to update notification status');
        }
        
        // 2. Update transaction status to "In Progress"
        const transactionResponse = await fetch(`http://localhost:5009/transaction/${order.transaction_id}/status`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            status: 'Paid'  // Move to "Paid" status to indicate acceptance
          })
        });
        
        if (!transactionResponse.ok) {
          throw new Error('Failed to update transaction status');
        }
        
        // 3. Remove from new orders list
        this.newOrders = this.newOrders.filter(o => o.notification_id !== order.notification_id);
        
        // 4. Refresh processing orders
        await this.fetchProcessingOrders();
        
      } catch (error) {
        console.error('Error accepting order:', error);
        alert('Failed to accept order. Please try again.');
      } finally {
        // Clear processing state
        this.$delete(this.isProcessingAction, order.notification_id);
      }
    },
    
    async processRejectOrder() {
      const order = this.selectedOrder;
      
      // Set processing state for this order
      this.$set(this.isProcessingAction, order.notification_id, true);
      
      try {
        // 1. Mark notification as read
        const notificationResponse = await fetch(`http://localhost:5011/notification/${order.notification_id}/read`, {
          method: 'PUT'
        });
        
        if (!notificationResponse.ok) {
          throw new Error('Failed to update notification status');
        }
        
        // 2. Process refund via processCustomerRefund service
        const transactionData = this.transactionDetails[order.transaction_id];
        
        if (!transactionData) {
          throw new Error('Transaction details not found');
        }
        
        const refundData = {
          transaction_id: order.transaction_id,
          customer_id: order.customer_id,
          refund_amount: parseFloat(transactionData.total_price_after_discount),
          refund_reason: 'Order rejected by restaurant'
        };
        
        const refundResponse = await fetch('http://localhost:5022/process_refund', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(refundData)
        });
        
        if (!refundResponse.ok) {
          throw new Error('Failed to process refund');
        }
        
        // 3. Remove from new orders list
        this.newOrders = this.newOrders.filter(o => o.notification_id !== order.notification_id);
        
      } catch (error) {
        console.error('Error rejecting order:', error);
        alert('Failed to reject order. Please try again.');
      } finally {
        // Clear processing state
        this.$delete(this.isProcessingAction, order.notification_id);
      }
    },
    
    async processCompleteOrder() {
      const order = this.selectedOrder;
      this.processingAction = order.transaction_id;
      
      try {
        // Update transaction status to "Delivered"
        const transactionResponse = await fetch(`http://localhost:5009/transaction/${order.transaction_id}/status`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            status: 'Delivered'
          })
        });
        
        if (!transactionResponse.ok) {
          throw new Error('Failed to update transaction status');
        }
        
        // Create a notification for the customer about delivery
        const notificationId = `NOTIF${Math.random().toString(36).substring(2, 10).toUpperCase()}`;
        const notificationData = {
          notification_id: notificationId,
          customer_id: order.customer_id,
          message_type: 'Order_Delivered',
          transaction_id: order.transaction_id
        };
        
        const notificationResponse = await fetch(`http://localhost:5011/notification/${notificationId}`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(notificationData)
        });
        
        if (!notificationResponse.ok) {
          console.warn('Failed to create delivery notification, but order was completed');
        }
        
        // Remove from processing orders list
        this.processingOrders = this.processingOrders.filter(o => o.transaction_id !== order.transaction_id);
        
        // Refresh completed orders
        await this.fetchCompletedOrders();
        
      } catch (error) {
        console.error('Error completing order:', error);
        alert('Failed to complete order. Please try again.');
      } finally {
        this.processingAction = null;
      }
    },
    
    setupAutoRefresh() {
      // Clear any existing interval
      if (this.refreshInterval) {
        clearInterval(this.refreshInterval);
      }
      
      // Set up new interval if auto-refresh is enabled
      if (this.autoRefresh) {
        this.refreshInterval = setInterval(() => {
          this.fetchOrders();
        }, this.refreshRate);
      }
    }
  },
  watch: {
    autoRefresh() {
      this.setupAutoRefresh();
    }
  },
  mounted() {
    this.fetchOrders();
    this.setupAutoRefresh();
  },
  beforeDestroy() {
    // Clean up interval
    if (this.refreshInterval) {
      clearInterval(this.refreshInterval);
    }
  }
}
</script>

<style scoped>
.restaurant-dashboard {
  padding: 2rem 0;
}

.dashboard-header {
  margin-bottom: 2rem;
  text-align: center;
}

.dashboard-header h1 {
  font-size: 2.5rem;
  color: var(--secondary-color);
  margin-bottom: 0.5rem;
}

.subtitle {
  color: #6c757d;
  font-size: 1.1rem;
}

/* Stats overview */
.stats-overview {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.stat-card {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  padding: 1.5rem;
  display: flex;
  align-items: center;
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  margin-right: 1rem;
}

.stat-icon.pending {
  background-color: #fff3cd;
  color: #856404;
}

.stat-icon.completed {
  background-color: #d4edda;
  color: #155724;
}

.stat-icon.revenue {
  background-color: #cce5ff;
  color: #004085;
}

.stat-info h3 {
  font-size: 1.8rem;
  margin-bottom: 0.25rem;
}

.stat-info p {
  margin: 0;
  color: #6c757d;
}

/* Orders sections */
.orders-section {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  margin-bottom: 2rem;
  overflow: hidden;
}

.section-header {
  background-color: #f8f9fa;
  padding: 1rem 1.5rem;
  border-bottom: 1px solid #dee2e6;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.section-header h2 {
  font-size: 1.25rem;
  color: var(--secondary-color);
  margin: 0;
  display: flex;
  align-items: center;
}

.section-header h2 i {
  margin-right: 0.5rem;
}

.orders-count {
  background-color: var(--primary-color);
  color: white;
  padding: 0.25rem 0.5rem;
  border-radius: 50%;
  font-size: 0.8rem;
  margin-left: 0.5rem;
}

.refresh-control {
  display: flex;
  align-items: center;
}

.refresh-btn {
  background: none;
  border: none;
  color: #6c757d;
  display: flex;
  align-items: center;
  cursor: pointer;
  transition: color 0.3s ease;
  margin-right: 1rem;
}

.refresh-btn:hover {
  color: var(--primary-color);
}

.refresh-btn i {
  margin-right: 0.5rem;
}

.refresh-btn.refreshing {
  animation: spin 1s linear infinite;
}

.auto-refresh {
  display: flex;
  align-items: center;
  font-size: 0.9rem;
  color: #6c757d;
}

.auto-refresh input {
  margin-right: 0.25rem;
}

/* Orders list styling */
.orders-list {
  padding: 1.5rem;
}

.loading-container, .error-container, .empty-state {
  padding: 3rem;
  text-align: center;
}

.loading-container .spinner {
  margin: 0 auto 1rem;
  width: 40px;
  height: 40px;
  border: 3px solid rgba(0, 0, 0, 0.1);
  border-radius: 50%;
  border-top-color: var(--primary-color);
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.error-container {
  color: var(--danger-color, #dc3545);
}

.error-container i {
  font-size: 2rem;
  margin-bottom: 1rem;
}

.empty-state {
  color: #6c757d;
}

.empty-state i {
  font-size: 3rem;
  color: #dee2e6;
  margin-bottom: 1rem;
}

.empty-hint {
  font-size: 0.9rem;
  margin-top: 0.5rem;
  color: #adb5bd;
}

.order-card {
  border: 1px solid #eee;
  border-radius: 8px;
  margin-bottom: 1.5rem;
  position: relative;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.order-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 6px 12px rgba(0, 0, 0, 0.1);
}

.order-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: #f8f9fa;
  padding: 0.75rem 1rem;
  border-radius: 8px 8px 0 0;
}

.order-type {
  display: inline-flex;
  align-items: center;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.85rem;
  font-weight: 500;
}

.order-type.new-order {
  background-color: #cce5ff;
  color: #004085;
}

.order-type.processing {
  background-color: #fff3cd;
  color: #856404;
}

.order-type i {
  margin-right: 0.5rem;
}

.order-time {
  font-size: 0.85rem;
  color: #6c757d;
}

.order-content {
  padding: 1rem;
}

.order-number, .order-customer, .order-total {
  margin-bottom: 0.75rem;
}

.label {
  font-weight: 500;
  color: #6c757d;
  margin-right: 0.5rem;
}

.value {
  font-weight: 600;
}

.order-items {
  margin: 1rem 0;
}

.items-list {
  list-style: none;
  padding: 0;
  margin: 0.5rem 0 0;
}

.items-list li {
  padding: 0.5rem;
  border-bottom: 1px solid #f2f2f2;
  display: flex;
  justify-content: space-between;
}

.items-list li:last-child {
  border-bottom: none;
}

.item-price {
  font-weight: 600;
}

.order-actions {
  padding: 1rem;
  border-top: 1px solid #eee;
  display: flex;
  gap: 1rem;
}

.btn {
  padding: 0.5rem 1rem;
  border-radius: 4px;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  border: none;
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
}

.btn-success {
  background-color: #28a745;
  color: white;
}

.btn-success:hover {
  background-color: #218838;
}

.btn-danger {
  background-color: #dc3545;
  color: white;
}

.btn-danger:hover {
  background-color: #c82333;
}

.btn-secondary {
  background-color: #6c757d;
  color: white;
}

.btn-secondary:hover {
  background-color: #5a6268;
}

.btn:disabled {
  opacity: 0.65;
  cursor: not-allowed;
}

.processing-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(255, 255, 255, 0.9);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  z-index: 10;
}

.processing-overlay .spinner {
  width: 40px;
  height: 40px;
  border: 3px solid rgba(0, 0, 0, 0.1);
  border-radius: 50%;
  border-top-color: var(--primary-color);
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

/* Modal styling */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background-color: white;
  border-radius: 8px;
  width: 100%;
  max-width: 500px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.5rem;
  border-bottom: 1px solid #eee;
}

.modal-header h3 {
  margin: 0;
  font-size: 1.25rem;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.25rem;
  cursor: pointer;
  color: #6c757d;
  transition: color 0.3s ease;
}

.close-btn:hover {
  color: var(--danger-color, #dc3545);
}

.modal-body {
  padding: 1.5rem;
}

.rejection-warning {
  color: var(--danger-color, #dc3545);
  background-color: #f8d7da;
  padding: 0.75rem;
  border-radius: 4px;
  margin-top: 1rem;
  display: flex;
  align-items: center;
}

.rejection-warning i {
  margin-right: 0.5rem;
}

.modal-footer {
  padding: 1rem 1.5rem;
  border-top: 1px solid #eee;
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
}

/* Responsive styles */
@media (max-width: 992px) {
  .stats-overview {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .stats-overview {
    grid-template-columns: 1fr;
  }
  
  .section-header {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .refresh-control {
    margin-top: 1rem;
    width: 100%;
    justify-content: space-between;
  }
  
  .order-actions {
    flex-direction: column;
  }
  
  .btn {
    width: 100%;
  }
}
</style>
