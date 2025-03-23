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

      <!-- Quick actions section -->
      <section class="quick-actions">
        <h2>Quick Actions</h2>
        <div class="action-cards">
          <div class="action-card">
            <i class="fas fa-utensils"></i>
            <h3>Order Food</h3>
            <p>Order from your favorite restaurants</p>
            <button class="btn btn-primary">Start Order</button>
          </div>
          <div class="action-card">
            <i class="fas fa-history"></i>
            <h3>Recent Orders</h3>
            <p>Track or reorder from previous orders</p>
            <button class="btn btn-secondary">View History</button>
          </div>
          <div class="action-card">
            <i class="fas fa-tags"></i>
            <h3>Vouchers</h3>
            <p>{{ activeVouchers }} active vouchers available</p>
            <button class="btn btn-secondary">View Vouchers</button>
          </div>
        </div>
      </section>

      <!-- Recommended restaurants -->
      <section class="recommendations">
        <h2>Recommended For You</h2>
        <div class="restaurant-carousel">
          <div v-for="restaurant in recommendedRestaurants" :key="restaurant.id" class="restaurant-card">
            <div class="restaurant-image">
              <img :src="restaurant.image" :alt="restaurant.name">
              <span class="rating"><i class="fas fa-star"></i> {{ restaurant.rating }}</span>
            </div>
            <div class="restaurant-info">
              <h3>{{ restaurant.name }}</h3>
              <p class="cuisine">{{ restaurant.cuisine }}</p>
              <p class="delivery-time"><i class="fas fa-clock"></i> {{ restaurant.deliveryTime }}</p>
            </div>
          </div>
        </div>
      </section>

      <!-- Recent orders -->
      <section class="recent-orders" v-if="recentOrders.length > 0">
        <h2>Your Recent Orders</h2>
        <div class="order-list">
          <div v-for="order in recentOrders" :key="order.id" class="order-card">
            <div class="order-header">
              <h3>{{ order.restaurantName }}</h3>
              <span class="order-date">{{ order.date }}</span>
            </div>
            <div class="order-items">
              <p>{{ order.items }}</p>
            </div>
            <div class="order-footer">
              <span class="order-price">${{ order.totalPrice.toFixed(2) }}</span>
              <button class="btn btn-primary btn-sm">Reorder</button>
            </div>
          </div>
        </div>
      </section>

      <!-- Notifications -->
      <section class="notifications" v-if="notifications.length > 0">
        <h2>Notifications</h2>
        <div class="notification-list">
          <div v-for="notification in notifications" :key="notification.id" class="notification-card">
            <div class="notification-icon" :class="notification.type">
              <i :class="getNotificationIcon(notification.type)"></i>
            </div>
            <div class="notification-content">
              <h3>{{ notification.title }}</h3>
              <p>{{ notification.message }}</p>
              <span class="notification-time">{{ notification.time }}</span>
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
      activeVouchers: 2,
      recommendedRestaurants: [
        {
          id: 1,
          name: 'Gourmet Delight',
          cuisine: 'Italian',
          rating: 4.5,
          deliveryTime: '30-45 min',
          image: 'https://via.placeholder.com/300x200?text=Gourmet+Delight'
        },
        {
          id: 2,
          name: 'Spicy Fusion',
          cuisine: 'Indian',
          rating: 4.2,
          deliveryTime: '25-40 min',
          image: 'https://via.placeholder.com/300x200?text=Spicy+Fusion'
        },
        {
          id: 3,
          name: 'Green Eats',
          cuisine: 'Vegan',
          rating: 4.8,
          deliveryTime: '20-35 min',
          image: 'https://via.placeholder.com/300x200?text=Green+Eats'
        },
        {
          id: 4,
          name: 'BBQ Haven',
          cuisine: 'BBQ',
          rating: 4.6,
          deliveryTime: '35-50 min',
          image: 'https://via.placeholder.com/300x200?text=BBQ+Haven'
        }
      ],
      recentOrders: [
        {
          id: 1,
          restaurantName: 'Gourmet Delight',
          date: '2025-03-20',
          items: 'Margherita Pizza, Garlic Bread, Coca Cola',
          totalPrice: 28.95
        },
        {
          id: 2,
          restaurantName: 'Spicy Fusion',
          date: '2025-03-15',
          items: 'Butter Chicken, Naan, Mango Lassi',
          totalPrice: 32.50
        }
      ],
      notifications: [
        {
          id: 1,
          type: 'voucher',
          title: 'New Voucher',
          message: 'You received a 15% off voucher for your next order!',
          time: '2 hours ago'
        },
        {
          id: 2,
          type: 'loyalty',
          title: 'Loyalty Points',
          message: 'You earned 25 loyalty points from your last order',
          time: '1 day ago'
        }
      ]
    }
  },
  computed: {
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
    getNotificationIcon(type) {
      switch(type) {
        case 'voucher':
          return 'fas fa-tag';
        case 'loyalty':
          return 'fas fa-crown';
        case 'order':
          return 'fas fa-shopping-bag';
        default:
          return 'fas fa-bell';
      }
    },
    loadUserData() {
      const userData = localStorage.getItem('currentUser');
      if (userData) {
        try {
          const user = JSON.parse(userData);
          this.userName = user.name || 'Guest';
          this.loyaltyStatus = user.loyalty_status || 'Bronze';
          this.loyaltyPoints = user.loyalty_points || 0;
          
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
    }
  },
  mounted() {
    this.loadUserData();
    
    // In a real application, you would fetch these from the respective APIs
    // For example:
    // this.fetchRecentOrders();
    // this.fetchNotifications();
    // this.fetchRecommendations();
    // this.fetchVouchers();
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

.quick-actions, .recommendations, .recent-orders, .notifications {
  margin-bottom: 3rem;
}

.quick-actions h2, .recommendations h2, .recent-orders h2, .notifications h2 {
  font-size: 1.5rem;
  margin-bottom: 1.5rem;
  color: var(--secondary-color);
}

.action-cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 1.5rem;
}

.action-card {
  background-color: white;
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  text-align: center;
  transition: transform 0.3s ease;
}

.action-card:hover {
  transform: translateY(-5px);
}

.action-card i {
  font-size: 2rem;
  color: var(--primary-color);
  margin-bottom: 1rem;
}

.action-card h3 {
  font-size: 1.2rem;
  margin-bottom: 0.5rem;
}

.action-card p {
  color: #666;
  margin-bottom: 1rem;
}

.restaurant-carousel {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 1.5rem;
  overflow-x: auto;
  padding-bottom: 1rem;
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
  background-color: rgba(0, 0, 0, 0.7);
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

.notification-icon.order {
  background-color: #E3F2FD;
  color: #2196F3;
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
  
  .restaurant-carousel, .order-list {
    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  }
}
</style>