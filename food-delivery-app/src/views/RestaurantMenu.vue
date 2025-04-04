<template>
  <div class="restaurant-menu">
    <div class="container">
      <!-- Restaurant Header -->
      <div v-if="isLoading" class="loading-container">
        <p><i class="fas fa-spinner fa-spin"></i> Loading restaurant details...</p>
      </div>
      <div v-else-if="error" class="error-container">
        <p><i class="fas fa-exclamation-circle"></i> {{ error }}</p>
        <button @click="fetchData" class="btn btn-primary mt-3">Try Again</button>
      </div>
      <div v-else>
        <!-- Restaurant Info -->
        <div class="restaurant-header">
          <div class="restaurant-image">
            <img :src="restaurant.image_url" :alt="restaurant.name">
          </div>
          <div class="restaurant-info">
            <h1>{{ restaurant.name }}</h1>
            <div class="restaurant-details">
              <span class="cuisine"><i class="fas fa-utensils"></i> {{ restaurant.cuisine_type }}</span>
              <span class="rating"><i class="fas fa-star"></i> {{ restaurant.rating }}</span>
              <span class="delivery-time"><i class="fas fa-clock"></i> 30-45 min</span>
              <span class="contact"><i class="fas fa-phone"></i> {{ restaurant.contact_number }}</span>
            </div>
          </div>
        </div>

        <!-- Menu Categories and Search -->
        <div class="menu-controls">
          <div class="search-bar">
            <i class="fas fa-search"></i>
            <input 
              type="text" 
              v-model="searchQuery" 
              placeholder="Search menu items..." 
              @input="filterMenuItems"
            >
            <button v-if="searchQuery" @click="clearSearch" class="clear-search">
              <i class="fas fa-times"></i>
            </button>
          </div>
          <div class="categories-filter">
            <button 
              class="category-btn" 
              :class="{ active: activeCategory === 'all' }"
              @click="setCategory('all')"
            >
              All
            </button>
            <button 
              v-for="category in categories" 
              :key="category"
              class="category-btn" 
              :class="{ active: activeCategory === category }"
              @click="setCategory(category)"
            >
              {{ category }}
            </button>
          </div>
        </div>

        <!-- Menu Items -->
        <div v-if="isLoadingMenuItems" class="loading-container">
          <p><i class="fas fa-spinner fa-spin"></i> Loading menu items...</p>
        </div>
        <div v-else-if="menuItemsError" class="error-container">
          <p><i class="fas fa-exclamation-circle"></i> {{ menuItemsError }}</p>
        </div>
        <div v-else-if="filteredMenuItems.length === 0" class="no-items-container">
          <p>No menu items found with your search criteria.</p>
          <button @click="clearSearch" class="btn btn-primary mt-3">Clear Search</button>
        </div>
        <div v-else class="menu-items-grid">
          <div v-for="item in filteredMenuItems" :key="item.item_id" class="menu-item-card">
            <div class="item-image">
              <img :src="item.image_url || 'https://dummyimage.com/150x150/cccccc/000000&text=Food'" :alt="item.item_name">
            </div>
            <div class="item-info">
              <h3>{{ item.item_name }}</h3>
              <p class="item-description">{{ item.description || 'Delicious menu item' }}</p>
              <div class="item-footer">
                <span class="item-price">${{ item.price.toFixed(2) }}</span>
                <div v-if="item.stock_quantity > 0">
                  <button 
                    class="btn btn-primary add-to-cart" 
                    v-if="isLoggedIn" 
                    @click="addToCart(item)"
                  >
                    <i class="fas fa-plus"></i> Add
                  </button>
                  <button 
                    class="btn btn-success in-stock" 
                    v-else
                  >
                    In Stock
                  </button>
                </div>
                <div v-else>
                  <span class="out-of-stock-label">Out of Stock</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Cart Summary (Fixed at bottom) -->
      <div v-if="cart.items.length > 0" class="cart-summary">
        <div class="cart-info">
          <span class="cart-count">{{ cart.totalItems }} items</span>
          <span class="cart-total">${{ cart.totalPrice.toFixed(2) }}</span>
        </div>
        <button class="btn btn-primary checkout-btn" @click="goToCartPage">
          Proceed to Checkout
        </button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'RestaurantMenu',
  data() {
    return {
      restaurant: {},
      menuItems: [],
      filteredMenuItems: [],
      categories: [],
      activeCategory: 'all',
      searchQuery: '',
      isLoading: true,
      isLoadingMenuItems: true,
      error: null,
      isLoggedIn: false,
      menuItemsError: null,
      cart: {
        items: [],
        totalItems: 0,
        totalPrice: 0
      }
    }
  },
  computed: {
    restaurantId() {
      return this.$route.params.id;
    }
  },
  methods: {
    checkLoginStatus() {
      // Check if user is logged in based on localStorage
      this.isLoggedIn = localStorage.getItem('isAuthenticated') === 'true';
    },
    
    async fetchData() {
      this.isLoading = true;
      this.error = null;
      
      try {
        // Fetch restaurant details
        const restaurantResponse = await fetch(`http://localhost:5007/restaurant/${this.restaurantId}`);
        
        if (!restaurantResponse.ok) {
          throw new Error(`Error fetching restaurant: ${restaurantResponse.statusText}`);
        }
        
        const restaurantResult = await restaurantResponse.json();
        
        if (restaurantResult.code === 200 && restaurantResult.data) {
          this.restaurant = restaurantResult.data;
          // Now fetch menu items
          this.fetchMenuItems();
        } else {
          this.error = 'Restaurant not found';
        }
      } catch (error) {
        console.error('Error fetching restaurant details:', error);
        this.error = 'Failed to load restaurant details. Please try again later.';
      } finally {
        this.isLoading = false;
      }
    },
    
    async fetchMenuItems() {
      this.isLoadingMenuItems = true;
      this.menuItemsError = null;
      
      try {
        // In a real app, we would filter by restaurant_id directly from the API
        // For now, fetch all inventory items and filter client-side
        const menuResponse = await fetch(`http://localhost:5008/restaurant_inventory/restaurant/${this.restaurantId}`);
        if (!menuResponse.ok) {
          throw new Error(`Error fetching menu items: ${menuResponse.statusText}`);
        }
        
        const menuResult = await menuResponse.json();
        
        if (menuResult.code === 200) {
          this.menuItems = menuResult.data.inventory_items || [];
          this.filteredMenuItems = [...this.menuItems];
          
          // Extract unique categories
          const categorySet = new Set();
          this.menuItems.forEach(item => {
            if (item.category) {
              categorySet.add(item.category);
            }
          });
          this.categories = Array.from(categorySet);
          
        } else {
          this.menuItemsError = 'No menu items found for this restaurant';
        }
      } catch (error) {
        console.error('Error fetching menu items:', error);
        this.menuItemsError = 'Failed to load menu items. Please try again later.';
      } finally {
        this.isLoadingMenuItems = false;
      }
    },
    
    filterMenuItems() {
      // Apply both category and search filters
      this.filteredMenuItems = this.menuItems.filter(item => {
        const matchesCategory = this.activeCategory === 'all' || item.category === this.activeCategory;
        const matchesSearch = !this.searchQuery || 
          item.item_name.toLowerCase().includes(this.searchQuery.toLowerCase()) ||
          (item.description && item.description.toLowerCase().includes(this.searchQuery.toLowerCase()));
        
        return matchesCategory && matchesSearch;
      });
    },
    
    setCategory(category) {
      this.activeCategory = category;
      this.filterMenuItems();
    },
    
    clearSearch() {
      this.searchQuery = '';
      this.filterMenuItems();
    },
    
    addToCart(item) {
      try {
        // First, retrieve the current cart from localStorage
        const cartData = localStorage.getItem('cart');
        let cartItems = [];
        
        if (cartData) {
          cartItems = JSON.parse(cartData);
        }
        
        // Check if item is already in cart
        const existingItemIndex = cartItems.findIndex(cartItem => cartItem.item_id === item.item_id);
        
        if (existingItemIndex >= 0) {
          // Increment quantity if already in cart
          cartItems[existingItemIndex].quantity += 1;
          cartItems[existingItemIndex].totalPrice = cartItems[existingItemIndex].quantity * cartItems[existingItemIndex].price;
        } else {
          // Add new item to cart with restaurant info
          cartItems.push({
            ...item,
            restaurant_name: this.restaurant.name,
            quantity: 1,
            totalPrice: item.price
          });
        }
        
        // Update cart in localStorage
        localStorage.setItem('cart', JSON.stringify(cartItems));
        
        // Update the cart display
        this.loadCartFromStorage();
        
      } catch (error) {
        console.error('Error adding item to cart:', error);
      }
    },
    
    loadCartFromStorage() {
      // Load cart from localStorage
      const cartData = localStorage.getItem('cart');
      if (cartData) {
        try {
          const cartItems = JSON.parse(cartData);
          this.cart.items = cartItems;
          this.cart.totalItems = cartItems.reduce((total, item) => total + item.quantity, 0);
          this.cart.totalPrice = cartItems.reduce((total, item) => total + item.totalPrice, 0);
        } catch (error) {
          console.error('Error parsing cart data:', error);
          this.cart.items = [];
          this.cart.totalItems = 0;
          this.cart.totalPrice = 0;
        }
      } else {
        this.cart.items = [];
        this.cart.totalItems = 0;
        this.cart.totalPrice = 0;
      }
    },
    
    goToCartPage() {
      // Navigate to the cart page
      this.$router.push('/cart');
    }
  },
  mounted() {
    this.checkLoginStatus();
    this.fetchData();
    this.loadCartFromStorage();
    
    // Listen for login/logout events
    window.addEventListener('user-logged-in', this.checkLoginStatus);
    window.addEventListener('user-logged-out', this.checkLoginStatus);
  },
  beforeDestroy() {
    // Clean up event listeners
    window.removeEventListener('user-logged-in', this.checkLoginStatus);
    window.removeEventListener('user-logged-out', this.checkLoginStatus);
  },
  watch: {
    // Re-fetch data if restaurant ID changes
    restaurantId() {
      this.fetchData();
    }
  }
}
</script>

<style scoped>
.restaurant-menu {
  padding-bottom: 80px; /* Space for fixed cart at bottom */
}

.restaurant-header {
  display: flex;
  margin-bottom: 2rem;
  background-color: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.restaurant-image {
  flex: 0 0 300px;
  height: 200px;
}

.restaurant-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.restaurant-info {
  flex: 1;
  padding: 1.5rem;
}

.restaurant-info h1 {
  margin-bottom: 1rem;
  color: var(--secondary-color);
}

.restaurant-details {
  display: flex;
  flex-wrap: wrap;
  gap: 1.5rem;
  color: #666;
}

.restaurant-details span {
  display: flex;
  align-items: center;
}

.restaurant-details i {
  margin-right: 0.5rem;
  color: var(--primary-color);
}

.menu-controls {
  margin-bottom: 2rem;
}

.search-bar {
  position: relative;
  margin-bottom: 1rem;
}

.search-bar i {
  position: absolute;
  left: 15px;
  top: 50%;
  transform: translateY(-50%);
  color: #999;
}

.search-bar input {
  width: 100%;
  padding: 0.75rem 2.5rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
}

.clear-search {
  position: absolute;
  right: 15px;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  color: #999;
  cursor: pointer;
}

.categories-filter {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.category-btn {
  padding: 0.5rem 1rem;
  background-color: #f0f0f0;
  border: none;
  border-radius: 50px;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.2s;
}

.category-btn.active {
  background-color: var(--primary-color);
  color: white;
}

.menu-items-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.5rem;
}

.menu-item-card {
  display: flex;
  background-color: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
  transition: transform 0.2s;
}

.menu-item-card:hover {
  transform: translateY(-5px);
}

.item-image {
  flex: 0 0 100px;
  position: relative;
}

.item-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.availability {
  position: absolute;
  top: 0;
  left: 0;
  padding: 0.25rem 0.5rem;
  font-size: 0.8rem;
  color: white;
}

.available {
  background-color: var(--success-color, #28a745);
}

.out-of-stock-label {
  display: inline-block;
  background-color: rgba(220, 53, 69, 0.9); /* Prominent red */
  color: white;
  font-weight: bold;
  font-size: 0.9rem;
  text-transform: uppercase;
  padding: 0.4rem 0.75rem;
  border-radius: 4px;
  text-align: center;
  cursor: not-allowed;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1); /* Subtle shadow */
}

.in-stock {
  padding: 0.4rem 0.75rem;
  font-size: 0.9rem;
  background-color: var(--success-color, #28a745);
  color: white;
  border: none;
  border-radius: 4px;
  cursor: default;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
}


.item-info {
  flex: 1;
  padding: 1rem;
  display: flex;
  flex-direction: column;
}

.item-info h3 {
  margin-bottom: 0.5rem;
  font-size: 1.1rem;
}

.item-description {
  color: #666;
  font-size: 0.9rem;
  margin-bottom: 0.5rem;
  flex: 1;
}

.item-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: auto;
}

.item-price {
  font-weight: bold;
  font-size: 1.1rem;
  color: var(--secondary-color);
}

.add-to-cart {
  padding: 0.4rem 0.75rem;
  font-size: 0.9rem;
}

.add-to-cart:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.loading-container, .error-container, .no-items-container {
  text-align: center;
  padding: 2rem;
  background-color: #f8f9fa;
  border-radius: 8px;
  margin: 1rem 0;
}

.error-container {
  color: var(--danger-color, #dc3545);
}

.cart-summary {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background-color: white;
  padding: 1rem 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.1);
  z-index: 100;
}

.cart-info {
  display: flex;
  flex-direction: column;
}

.cart-count {
  font-size: 0.9rem;
  color: #666;
}

.cart-total {
  font-weight: bold;
  font-size: 1.2rem;
  color: var(--secondary-color);
}

.checkout-btn {
  padding: 0.75rem 1.5rem;
}

@media (max-width: 768px) {
  .restaurant-header {
    flex-direction: column;
  }
  
  .restaurant-image {
    flex: 0 0 150px;
    width: 100%;
  }
  
  .menu-item-card {
    flex-direction: column;
  }
  
  .item-image {
    height: 150px;
    width: 100%;
  }
}
</style>