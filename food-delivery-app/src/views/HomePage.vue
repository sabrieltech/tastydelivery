<template>
  <div class="home">

    <!-- Featured restaurants section -->
    <section class="featured-restaurants">
      <h2>Popular Restaurants</h2>
      <div v-if="isLoading" class="loading-container">
        <p>Loading restaurants...</p>
      </div>
      <div v-else-if="error" class="error-container">
        <p>{{ error }}</p>
      </div>
      <div v-else class="restaurant-grid">
        <div v-for="restaurant in featuredRestaurants" :key="restaurant.restaurant_id" class="restaurant-card">
          <img :src="restaurant.image_url" :alt="restaurant.name" />
          <h3>{{ restaurant.name }}</h3>
          <p>{{ restaurant.cuisine_type }}</p>
          <div class="restaurant-details">
            <span><i class="fas fa-star"></i> {{ restaurant.rating }}</span>
            <span><i class="fas fa-clock"></i> 30-45 min</span>
          </div>
          <!-- Add View Menu Button -->
          <router-link
            :to="{ name: 'RestaurantMenu', params: { id: restaurant.restaurant_id } }"
            class="btn-primary view-menu-btn"
          >
            View Menu
          </router-link>
        </div>
      </div>
    </section>
    
  </div>
</template>

<script>
export default {
  name: 'HomePage',
  data() {
    return {
      heroImage: 'https://via.placeholder.com/500x300?text=Food+Delivery',
      appStoreImage: 'https://via.placeholder.com/150x50?text=App+Store',
      googlePlayImage: 'https://via.placeholder.com/150x50?text=Google+Play',
      mobileAppImage: 'https://via.placeholder.com/300x600?text=Mobile+App',
      featuredRestaurants: [],
      isLoading: true,
      error: null
    }
  },
  mounted() {
    this.fetchRestaurants();
  },
    methods: {
    async fetchRestaurants() {
      this.isLoading = true;
      this.error = null;
  
      try {
        const response = await fetch('http://localhost:5007/restaurant');
        if (!response.ok) {
          throw new Error(`Error fetching restaurants: ${response.statusText}`);
        }
  
        const result = await response.json();
  
        if (result.code === 200 && result.data && result.data.restaurants) {
          // Use all restaurants without limiting to the top 4
          this.featuredRestaurants = result.data.restaurants.sort((a, b) => b.rating - a.rating);
        } else {
          this.error = 'No restaurants found';
        }
      } catch (error) {
        console.error('Error fetching restaurants:', error);
        this.error = 'Failed to load restaurants. Please try again later.';
      } finally {
        this.isLoading = false;
      }
    },
    redirectToLogin() {
      this.$router.push('/login'); // Redirect to the LoginPage
    }
  }
}
</script>

<style scoped>
/* Add your CSS styling here */

.view-menu-btn {
  display: block;
  width: fit-content;
  margin: 1rem auto;
  padding: 0.3rem 0.8rem;
  font-size: 0.9rem;
  font-weight: bold;
  text-transform: uppercase;
  background-color: var(--primary-color);
  color: #fff;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s ease, transform 0.2s ease;
}

.view-menu-btn:hover {
  background-color: #0056b3;
  transform: scale(1.05);
}

.hero {
  display: flex;
  padding: 2rem;
  background-color: #f8f9fa;
}

.featured-restaurants {
  padding: 2rem;
}

.restaurant-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 2rem;
  margin-top: 1.5rem;
}

.restaurant-card {
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s ease;
}

.restaurant-card:hover {
  transform: translateY(-5px);
}

.restaurant-card img {
  width: 100%;
  height: 200px;
  object-fit: cover;
}

.restaurant-card h3, .restaurant-card p {
  padding: 0 1rem;
  margin: 0.5rem 0;
}

.restaurant-details {
  display: flex;
  justify-content: space-between;
  padding: 0.5rem 1rem 1rem;
  color: #666;
}

.loading-container, .error-container {
  text-align: center;
  padding: 2rem;
  background-color: #f8f9fa;
  border-radius: 8px;
  margin-top: 1.5rem;
}

.error-container {
  color: var(--danger-color, #dc3545);
}

.app-download {
  display: flex;
  padding: 2rem;
  background-color: #f8f9fa;
  margin-top: 2rem;
}
</style>