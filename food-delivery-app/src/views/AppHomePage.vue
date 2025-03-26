<template>
  <div class="app-home">
    <div class="container">
      <!-- Welcome header with user information -->
      <header class="welcome-header">
        <div class="user-welcome">
          <h1>Welcome, {{ userName }}!</h1>
          <p>What would you like to order today?</p>
        </div>
        <div class="user-stats">
          <div class="loyalty-card">
            <i class="fas fa-crown"></i>
            <div class="loyalty-info">
              <h3>{{ loyaltyStatus }} Member</h3>
              <p>{{ loyaltyPoints }} points</p>
              <div class="progress-bar">
                <div class="progress" :style="{ width: progressPercentage + '%' }"></div>
              </div>
              <p class="next-tier">{{ pointsToNextTier }} points to {{ nextTier }}</p>
            </div>
          </div>
        </div>
      </header>

      <!-- Popular Restaurants - Ordered by transaction volume -->
      <section class="most-ordered-restaurants">
        <h2>Most Ordered By You</h2>
        <div v-if="isLoadingPopular" class="loading-container">
          <p><i class="fas fa-spinner fa-spin"></i> Loading Popular Restaurants...</p>
        </div>
        <div v-else-if="popularError" class="error-container">
          <p>{{ popularError }}</p>
        </div>
        <div v-else class="restaurant-carousel">
          <div v-for="restaurant in popularRestaurants" :key="restaurant.id" class="restaurant-card">
            <div class="restaurant-image">
              <img :src="restaurant.image_url || restaurant.image" :alt="restaurant.name">
              <span class="popularity-badge"><i class="fas fa-fire"></i> #{{ restaurant.popularityRank }}</span>
              <!-- Add View Menu Button -->
              <div class="menu-button-overlay">
                <router-link 
                  :to="{ name: 'RestaurantMenu', params: { id: restaurant.restaurant_id || restaurant.id } }" 
                  class="view-menu-btn"
                >
                  <i class="fas fa-utensils"></i> View Menu
                </router-link>
              </div>
            </div>
            <div class="restaurant-info">
              <h3>{{ restaurant.name }}</h3>
              <p class="cuisine">{{ restaurant.cuisine_type || restaurant.cuisine }}</p>
              <p class="orders-count"><i class="fas fa-shopping-bag"></i> {{ restaurant.transactionCount || 0 }} orders</p>
            </div>
          </div>
        </div>
      </section>

      <!-- Top-rated restaurants -->
      <section class="top-rated-restaurants">
        <h2>Top-rated Restaurants</h2>
        <div v-if="isLoading" class="loading-container">
          <p><i class="fas fa-spinner fa-spin"></i> Loading Top-rated Restaurants...</p>
        </div>
        <div v-else-if="restaurantsError" class="error-container">
          <p>{{ restaurantsError }}</p>
        </div>
        <div v-else class="restaurant-carousel">
          <div v-for="restaurant in recommendedRestaurants" :key="restaurant.id" class="restaurant-card">
            <div class="restaurant-image">
              <img :src="restaurant.image_url || restaurant.image" :alt="restaurant.name">
              <span class="rating"><i class="fas fa-star"></i> {{ restaurant.rating }}</span>
              <!-- Add View Menu Button -->
              <div class="menu-button-overlay">
                <router-link 
                  :to="{ name: 'RestaurantMenu', params: { id: restaurant.restaurant_id || restaurant.id } }" 
                  class="view-menu-btn"
                >
                  <i class="fas fa-utensils"></i> View Menu
                </router-link>
              </div>
            </div>
            <div class="restaurant-info">
              <h3>{{ restaurant.name }}</h3>
              <p class="cuisine">{{ restaurant.cuisine_type || restaurant.cuisine }}</p>
              <p class="delivery-time"><i class="fas fa-clock"></i> {{ restaurant.deliveryTime || '30-45 min' }}</p>
            </div>
          </div>
        </div>
      </section>

      <!-- Recent orders -->
      <section class="recent-orders" v-if="recentOrders.length > 0">
        <h2>Your Recent Orders</h2>
        <div class="order-list">
          <div v-for="order in displayedOrders" :key="order.id" class="order-card">
            <div class="order-header">
              <h3>{{ order.restaurantName }}</h3>
              <span class="order-date">{{ order.date }}</span>
            </div>
            <div class="order-items">
              <p>{{ order.items_text || order.items }}</p>
            </div>
            <div class="order-footer">
              <span class="order-price">${{ order.totalPrice.toFixed(2) }}</span>
              <button class="btn btn-primary btn-sm">Reorder</button>
            </div>
          </div>
        </div>
        <div v-if="recentOrders.length > ordersPerPage && !allOrdersDisplayed" class="load-more-container">
            <button @click="loadMoreOrders" class="btn btn-secondary load-more-btn">
              <i class="fas fa-chevron-down"></i> Load More Orders
            </button>
        </div>
        
      </section>

      <!-- Active Vouchers section -->
      <section class="vouchers" v-if="vouchers && vouchers.length > 0">
        <h2>Your Active Vouchers</h2>
        <div class="voucher-list">
          <div v-for="voucher in vouchers" :key="voucher.voucher_id" class="voucher-card">
            <div class="voucher-content">
              <h3>{{ voucher.code }}</h3>
              <p>{{ voucher.discount_percentage }}% off (up to ${{ voucher.max_discount_amount }})</p>
              <p class="voucher-expiry">Expires: {{ formatDate(voucher.expiry_date) }}</p>
            </div>
          </div>
        </div>
      </section>

      <!-- Notifications -->
      <section class="notifications" v-if="notifications.length > 0">
        <h2>Notifications</h2>
        <div class="notification-list">
          <div v-for="notification in notifications" :key="notification.notification_id || notification.id" class="notification-card">
            <div class="notification-icon" :class="notification.type || getNotificationType(notification.message_type)">
              <i :class="getNotificationIcon(notification.type || getNotificationType(notification.message_type))"></i>
            </div>
            <div class="notification-content">
              <h3>{{ notification.title || getNotificationTitle(notification.message_type) }}</h3>
              <p>{{ notification.message || getNotificationMessage(notification) }}</p>
              <span class="notification-time">{{ notification.time || formatNotificationTime(notification.created_at) }}</span>
            </div>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<script>
export default {
  name: 'AppHomePage',
  data() {
    return {
      userName: 'Guest',
      loyaltyStatus: 'Bronze',
      loyaltyPoints: 0,
      nextTier: 'Silver',
      pointsToNextTier: 100,
      recommendedRestaurants: [],
      recentOrders: [],
      vouchers: [],
      notifications: [],
      isLoading: true,
      restaurantsError: null,
      customerId: null,
      popularRestaurants: [],
      isLoadingPopular: true,
      popularError: null,
      displayedOrders: [],
      ordersPerPage: 6,
      currentPage: 1
    }
  },
  computed: {
    allOrdersDisplayed() {
    return this.displayedOrders.length >= this.recentOrders.length;
    },
    progressPercentage() {
      // For Bronze tier, progress towards Silver (100 points)
      if (this.loyaltyStatus === 'Bronze') {
        return Math.min(100, (this.loyaltyPoints / 100) * 100);
      }
      // For Silver tier, progress towards Gold (300 points)
      else if (this.loyaltyStatus === 'Silver') {
        return Math.min(100, ((this.loyaltyPoints - 100) / 200) * 100);
      }
      // For Gold tier, already at max
      return 100;
    }
  },
  methods: {
    loadMoreOrders() {
      const nextPage = this.currentPage + 1;
      const startIndex = this.ordersPerPage * (this.currentPage);
      const endIndex = this.ordersPerPage * nextPage;
      
      // Get the next batch of orders
      const nextBatch = this.recentOrders.slice(startIndex, endIndex);
      
      // Add the next batch to the displayed orders
      this.displayedOrders = [...this.displayedOrders, ...nextBatch];
      
      // Update the current page
      this.currentPage = nextPage;
    },
    initDisplayedOrders() {
    // Initialize displayed orders with the first page
      if (this.recentOrders.length > 0) {
        this.displayedOrders = this.recentOrders.slice(0, this.ordersPerPage);
        this.currentPage = 1;
      }
    },
    getNotificationIcon(type) {
      switch(type) {
        case 'voucher':
        case 'refund':
          return 'fas fa-tag';
        case 'loyalty':
          return 'fas fa-crown';
        case 'order':
        case 'payment':
          return 'fas fa-shopping-bag';
        default:
          return 'fas fa-bell';
      }
    },
    getNotificationType(messageType) {
      switch(messageType) {
        case 'Payment_Success':
          return 'payment';
        case 'Refund_Processed':
          return 'refund';
        case 'Loyalty_Updated':
          return 'loyalty';
        default:
          return 'order';
      }
    },
    getNotificationTitle(messageType) {
      switch(messageType) {
        case 'Payment_Success':
          return 'Payment Successful';
        case 'Refund_Processed':
          return 'Refund Processed';
        case 'Loyalty_Updated':
          return 'Loyalty Status Updated';
        default:
          return 'Notification';
      }
    },
    getNotificationMessage(notification) {
      switch(notification.message_type) {
        case 'Payment_Success':
          return `Your payment for order was successful`;
        case 'Refund_Processed':
          return 'Your refund has been processed successfully';
        case 'Loyalty_Updated':
          return `You now have ${notification.loyalty_points || 0} points`;
        default:
          return 'You have a new notification';
      }
    },
    formatNotificationTime(timestamp) {
      if (!timestamp) return '';
      
      const now = new Date();
      const notificationDate = new Date(timestamp);
      const diffMs = now - notificationDate;
      
      // Convert to minutes, hours, days
      const diffMinutes = Math.floor(diffMs / (1000 * 60));
      const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
      const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));
      
      if (diffDays > 0) {
        return `${diffDays} days ago`;
      } else if (diffHours > 0) {
        return `${diffHours} hours ago`;
      } else {
        return `${diffMinutes} minutes ago`;
      }
    },
    formatDate(dateString) {
      const options = { year: 'numeric', month: 'short', day: 'numeric' };
      return new Date(dateString).toLocaleDateString(undefined, options);
    },
    loadUserData() {
      const userData = localStorage.getItem('currentUser');
      if (userData) {
        try {
          const user = JSON.parse(userData);
          this.userName = user.name || 'Guest';
          this.loyaltyStatus = user.loyalty_status || 'Bronze';
          this.loyaltyPoints = user.loyalty_points || 0;
          this.customerId = user.customer_id || null;
          
          // Calculate points to next tier
          if (this.loyaltyStatus === 'Bronze') {
            this.nextTier = 'Silver';
            this.pointsToNextTier = Math.max(0, 100 - this.loyaltyPoints);
          } else if (this.loyaltyStatus === 'Silver') {
            this.nextTier = 'Gold';
            this.pointsToNextTier = Math.max(0, 300 - this.loyaltyPoints);
          } else {
            this.nextTier = 'Max Level';
            this.pointsToNextTier = 0;
          }
        } catch (error) {
          console.error('Error parsing user data:', error);
        }
      }
    },
    async fetchPersonalizedHomepage() {
      this.isLoading = true;
      this.restaurantsError = null;
      
      // If no customer ID, fall back to fetching all restaurants
      if (!this.customerId) {
        try {
          const response = await fetch('http://localhost:5007/restaurant');
          if (!response.ok) {
            throw new Error(`Error fetching restaurants: ${response.statusText}`);
          }
          
          const result = await response.json();
          
          if (result.code === 200 && result.data && result.data.restaurants) {
            this.recommendedRestaurants = result.data.restaurants.sort((a, b) => b.rating - a.rating);
          } else {
            this.restaurantsError = 'No restaurants found';
          }
        } catch (error) {
          console.error('Error fetching restaurants:', error);
          this.restaurantsError = 'Failed to load restaurants. Please try again later.';
        } finally {
          this.isLoading = false;
        }
        return;
      }
      
      // Use the personalized homepage microservice
      try {
        const response = await fetch(`http://localhost:5013/personalized_homepage/${this.customerId}`);
        if (!response.ok) {
          throw new Error(`Error fetching personalized data: ${response.statusText}`);
        }
        
        const result = await response.json();
        
        if (result.code === 200 && result.data) {
          // Update customer info if available
          if (result.data.customerInfo) {
            const customerInfo = result.data.customerInfo;
            this.userName = customerInfo.name || this.userName;
            this.loyaltyStatus = customerInfo.loyalty_status || this.loyaltyStatus;
            this.loyaltyPoints = customerInfo.loyalty_points || this.loyaltyPoints;
            
            // Recalculate points to next tier
            if (this.loyaltyStatus === 'Bronze') {
              this.nextTier = 'Silver';
              this.pointsToNextTier = Math.max(0, 100 - this.loyaltyPoints);
            } else if (this.loyaltyStatus === 'Silver') {
              this.nextTier = 'Gold';
              this.pointsToNextTier = Math.max(0, 300 - this.loyaltyPoints);
            } else {
              this.nextTier = 'Max Level';
              this.pointsToNextTier = 0;
            }
          }
          
          // Update recommended restaurants
          if (result.data.recommendedRestaurants) {
            this.recommendedRestaurants = result.data.recommendedRestaurants;
          }
          
          // Update recent orders
          if (result.data.recentOrders) {
            this.recentOrders = result.data.recentOrders;
            this.displayedOrders = this.recentOrders.slice(0, this.ordersPerPage);
          }
          
          // Update vouchers
          if (result.data.vouchers) {
            this.vouchers = result.data.vouchers;
          }
          
          // Update notifications
          if (result.data.notifications) {
            this.notifications = result.data.notifications;
          }
        } else {
          this.restaurantsError = 'Could not load personalized data';
        }
      } catch (error) {
        console.error('Error fetching personalized homepage data:', error);
        this.restaurantsError = 'Failed to load personalized data. Please try again later.';
        
        // Fallback to fetching just restaurants
        try {
          const response = await fetch('http://localhost:5007/restaurant');
          if (response.ok) {
            const result = await response.json();
            if (result.code === 200 && result.data && result.data.restaurants) {
              this.recommendedRestaurants = result.data.restaurants.sort((a, b) => b.rating - a.rating);
              this.restaurantsError = null; // Clear error if we at least have restaurants
            }
          }
        } catch (fallbackError) {
          console.error('Fallback restaurant fetch also failed:', fallbackError);
        }
      } finally {
        this.isLoading = false;
      }
    },
    async fetchPopularRestaurants() {
      this.isLoadingPopular = true;
      this.popularError = null;
      
      // Only proceed if user is logged in with a customer ID
      if (!this.customerId) {
        this.isLoadingPopular = false;
        this.popularError = "Please log in to see your ordering history";
        return;
      }
      
      try {
        // Get all restaurants
        const restaurantsResponse = await fetch('http://localhost:5007/restaurant');
        
        // Get user's transactions
        const userTransactionsResponse = await fetch(`http://localhost:5009/transaction/customer/${this.customerId}`);
        
        // Get all transaction items
        const transactionItemsResponse = await fetch('http://localhost:5010/transaction_item');
        
        if (!restaurantsResponse.ok || !userTransactionsResponse.ok || !transactionItemsResponse.ok) {
          throw new Error("Error fetching data from one or more services");
        }
        
        const restaurantsResult = await restaurantsResponse.json();
        const userTransactionsResult = await userTransactionsResponse.json();
        const transactionItemsResult = await transactionItemsResponse.json();
        
        if (restaurantsResult.code === 200 && restaurantsResult.data && 
            userTransactionsResult.code === 200 && userTransactionsResult.data &&
            transactionItemsResult.code === 200 && transactionItemsResult.data) {
          
          // Get restaurant and transaction data
          const restaurants = restaurantsResult.data.restaurants;
          const userTransactions = userTransactionsResult.data.transactions;
          const allTransactionItems = transactionItemsResult.data.transaction_items;
          
          // Get the transaction IDs for this user
          const userTransactionIds = userTransactions.map(transaction => transaction.transaction_id);
          
          // Filter transaction items to only include user's transactions
          const userTransactionItems = allTransactionItems.filter(item => 
            userTransactionIds.includes(item.transaction_id)
          );
          
          // Count orders per restaurant
          const restaurantOrderCounts = {};
          userTransactionItems.forEach(item => {
            const restaurantId = item.restaurant_id;
            if (!restaurantOrderCounts[restaurantId]) {
              restaurantOrderCounts[restaurantId] = 0;
            }
            restaurantOrderCounts[restaurantId]++;
          });
          
          // Add order counts to restaurants and filter to only include ones ordered from
          const userOrderedRestaurants = restaurants
            .map(restaurant => ({
              ...restaurant,
              transactionCount: restaurantOrderCounts[restaurant.restaurant_id] || 0
            }))
            .filter(restaurant => restaurant.transactionCount > 0);
          
          // Sort by order count (highest first)
          const sortedRestaurants = userOrderedRestaurants.sort((a, b) => 
            b.transactionCount - a.transactionCount
          );
          
          // Add popularity rank
          sortedRestaurants.forEach((restaurant, index) => {
            restaurant.popularityRank = index + 1;
          });
          
          // Update the title of the section (can be done in the template)
          this.popularRestaurants = sortedRestaurants;
          
          if (sortedRestaurants.length === 0) {
            this.popularError = "You haven't ordered from any restaurants yet";
          }
        } else {
          this.popularError = 'Could not load your order history';
        }
      } catch (error) {
        console.error('Error fetching user ordered restaurants:', error);
        this.popularError = 'Failed to load your order history. Please try again later.';
      } finally {
        this.isLoadingPopular = false;
      }
    },
  },
  mounted() {
    this.loadUserData();
    this.fetchPersonalizedHomepage();
    this.fetchPopularRestaurants();
  }
}
</script>

<style scoped>
.app-home {
  padding: 2rem 0;
}

.welcome-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.user-welcome h1 {
  font-size: 2rem;
  margin-bottom: 0.5rem;
  color: var(--secondary-color);
}

.user-welcome p {
  font-size: 1.1rem;
  color: #666;
}

.loyalty-card {
  display: flex;
  align-items: center;
  background: linear-gradient(135deg, #f5f5f5, #e8e8e8);
  padding: 1rem;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.loyalty-card i {
  font-size: 2rem;
  margin-right: 1rem;
  color: #FFD700;
}

.loyalty-info h3 {
  font-size: 1.2rem;
  margin-bottom: 0.25rem;
}

.progress-bar {
  height: 8px;
  background-color: #ddd;
  border-radius: 4px;
  margin: 0.5rem 0;
  overflow: hidden;
  width: 150px;
}

.progress {
  height: 100%;
  background: linear-gradient(90deg, var(--primary-color), var(--accent-color));
}

.next-tier {
  font-size: 0.8rem;
  color: #666;
}

.top-rated-restaurants, .recent-orders, .notifications, .vouchers {
  margin-bottom: 3rem;
}

.top-rated-restaurants h2, .recent-orders h2, .notifications h2, .vouchers h2 {
  font-size: 1.5rem;
  margin-bottom: 1.5rem;
  color: var(--secondary-color);
}

/* Add these styles to the <style> section */
.most-ordered-restaurants {
  margin-bottom: 3rem;
}

.most-ordered-restaurants h2 {
  font-size: 1.5rem;
  margin-bottom: 1.5rem;
  color: var(--secondary-color);
}

.popularity-badge {
  position: absolute;
  top: 10px;
  left: 10px;
  background-color: rgba(255, 90, 95, 0.9);
  color: white;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.9rem;
}

.orders-count {
  font-size: 0.9rem;
  color: #666;
}

.orders-count i {
  color: var(--primary-color);
  margin-right: 0.25rem;
}

.loading-container, .error-container {
  text-align: center;
  padding: 1.5rem;
  background-color: #f8f9fa;
  border-radius: 8px;
  margin-bottom: 1.5rem;
}

.load-more-container {
  display: flex;
  justify-content: center;
  margin-top: 1.5rem;
}

.load-more-btn {
  padding: 0.75rem 1.5rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  transition: transform 0.2s;
  background-color: #f0f0f0;
  color: var(--secondary-color);
  border: 1px solid #ddd;
}

.load-more-btn:hover {
  transform: translateY(-2px);
  background-color: #e0e0e0;
}

.error-container {
  color: var(--danger-color, #dc3545);
}

.restaurant-carousel {
  display: grid;
  grid-template-columns: repeat(5, 280px); /* Fixed width for 5 columns */
  grid-auto-flow: column; /* Force horizontal flow */
  grid-auto-columns: 280px; /* Set width for overflow columns */
  gap: 1.5rem;
  overflow-x: auto; /* Enable horizontal scrolling */
  
  /* Increase padding significantly */
  padding: 2rem; /* Larger padding all around */
  
  
  /* Background and shadow for better definition */
  background-color: #f9f9f9;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  
  scrollbar-width: thin; /* For Firefox */
  -ms-overflow-style: none; /* For IE and Edge */
  scroll-behavior: smooth; /* Smooth scrolling */
  margin-bottom: 1rem; /* Space between carousel and next section */
}

/* For modern browsers to hide scrollbar but keep functionality */
.restaurant-carousel::-webkit-scrollbar {
  height: 6px;
}

.restaurant-carousel::-webkit-scrollbar-thumb {
  background-color: rgba(0,0,0,0.2);
  border-radius: 3px;
}

.restaurant-carousel::-webkit-scrollbar-track {
  background: rgba(0,0,0,0.05);
}

@media (max-width: 1200px) {
  .restaurant-carousel {
    grid-template-columns: repeat(3, 250px); /* Show 3 items at a time on medium screens */
    grid-auto-columns: 250px; /* Set width for overflow columns */
  }
}

@media (max-width: 768px) {
  .restaurant-carousel {
    grid-template-columns: repeat(2, 200px); /* Show 2 items at a time on small screens */
    grid-auto-columns: 200px; /* Set width for overflow columns */
  }
}
.menu-button-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.6);
  display: flex;
  justify-content: center;
  align-items: center;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.restaurant-card:hover .menu-button-overlay {
  opacity: 1;
}

.view-menu-btn {
  display: inline-block;
  padding: 0.5rem 1rem;
  background-color: var(--primary-color);
  color: white;
  border-radius: 4px;
  font-weight: bold;
  text-transform: uppercase;
  font-size: 0.9rem;
  transition: transform 0.2s ease, background-color 0.3s ease;
  text-decoration: none;
}

.view-menu-btn:hover {
  transform: scale(1.05);
  background-color: #0056b3; /* Darker shade of blue */
}

.view-menu-btn i {
  margin-right: 0.5rem;
}

.restaurant-card {
  background-color: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s ease;
}

.restaurant-card:hover {
  transform: translateY(-5px);
}

.restaurant-image {
  position: relative;
  height: 150px;
  overflow: hidden;
}


.restaurant-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.rating {
  position: absolute;
  bottom: 10px;
  right: 10px;
  background-color: rgba(255,215,0,0.9);
  color: white;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.9rem;
}

.restaurant-info {
  padding: 1rem;
}

.restaurant-info h3 {
  font-size: 1.1rem;
  margin-bottom: 0.5rem;
}

.cuisine {
  font-size: 0.9rem;
  color: #666;
  margin-bottom: 0.5rem;
}

.delivery-time {
  font-size: 0.9rem;
  color: #666;
}

.order-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.5rem;
}

.order-card {
  background-color: white;
  border-radius: 8px;
  padding: 1rem;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.order-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.order-header h3 {
  font-size: 1.1rem;
}

.order-date {
  font-size: 0.9rem;
  color: #666;
}

.order-items {
  padding: 0.5rem 0;
  border-top: 1px solid #eee;
  border-bottom: 1px solid #eee;
  margin-bottom: 0.5rem;
}

.order-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.order-price {
  font-weight: bold;
  color: var(--secondary-color);
}

.btn-sm {
  padding: 0.35rem 0.75rem;
  font-size: 0.9rem;
}

.voucher-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 1.5rem;
}

.voucher-card {
  background: linear-gradient(135deg, #f8f9fa, #e9ecef);
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  border-left: 4px solid var(--primary-color);
  position: relative;
}

.voucher-card::before {
  content: '';
  position: absolute;
  top: 0;
  right: 0;
  bottom: 0;
  width: 15px;
  background: 
    radial-gradient(circle at 0 10px, transparent 10px, rgba(255,255,255,0.5) 10px),
    radial-gradient(circle at 0 30px, transparent 10px, rgba(255,255,255,0.5) 10px),
    radial-gradient(circle at 0 50px, transparent 10px, rgba(255,255,255,0.5) 10px),
    radial-gradient(circle at 0 70px, transparent 10px, rgba(255,255,255,0.5) 10px),
    radial-gradient(circle at 0 90px, transparent 10px, rgba(255,255,255,0.5) 10px);
  background-size: 15px 20px;
  background-repeat: repeat-y;
}

.voucher-content h3 {
  font-size: 1.3rem;
  margin-bottom: 0.5rem;
  color: var(--primary-color);
}

.voucher-expiry {
  font-size: 0.85rem;
  color: #6c757d;
  margin-top: 0.5rem;
}

.notification-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.notification-card {
  display: flex;
  background-color: white;
  border-radius: 8px;
  padding: 1rem;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.notification-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 50px;
  height: 50px;
  border-radius: 50%;
  margin-right: 1rem;
}

.notification-icon.voucher {
  background-color: #FFF3E0;
  color: #FF9800;
}

.notification-icon.loyalty {
  background-color: #E8F5E9;
  color: #4CAF50;
}

.notification-icon.order, .notification-icon.payment {
  background-color: #E3F2FD;
  color: #2196F3;
}

.notification-icon.refund {
  background-color: #FCE4EC;
  color: #E91E63;
}

.notification-content {
  flex: 1;
}

.notification-content h3 {
  font-size: 1.1rem;
  margin-bottom: 0.25rem;
}

.notification-time {
  font-size: 0.8rem;
  color: #999;
}

@media (max-width: 768px) {
  .welcome-header {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .loyalty-card {
    width: 100%;
    margin-top: 1rem;
  }
  
  .restaurant-carousel, .order-list, .voucher-list {
    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  }
}
</style>