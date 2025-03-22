<template>
  <div class="home">
    <!-- Hero section -->
    <section class="hero">
      <div class="hero-content">
        <h1>Order Delicious Food Online</h1>
        <p>Fast delivery to your doorstep</p>
        <button class="btn-primary">Order Now</button>
      </div>
      <div class="hero-image">
        <img :src="heroImage" alt="Food Delivery" />
      </div>
    </section>
    
    <!-- Featured restaurants section -->
    <section class="featured-restaurants">
      <h2>Popular Restaurants</h2>
      <div class="restaurant-grid">
        <div v-for="restaurant in featuredRestaurants" :key="restaurant.id" class="restaurant-card">
          <img :src="restaurant.image" :alt="restaurant.name" />
          <h3>{{ restaurant.name }}</h3>
          <p>{{ restaurant.cuisine }}</p>
          <div class="restaurant-details">
            <span>⭐ {{ restaurant.rating }}</span>
            <span>🕒 {{ restaurant.deliveryTime }}</span>
          </div>
        </div>
      </div>
    </section>
    
    <!-- App download section -->
    <section class="app-download">
      <div class="app-content">
        <h2>Download Our Mobile App</h2>
        <p>Get exclusive deals and faster ordering</p>
        <div class="app-buttons">
          <img :src="appStoreImage" alt="App Store" />
          <img :src="googlePlayImage" alt="Google Play" />
        </div>
      </div>
      <div class="app-image">
        <img :src="mobileAppImage" alt="Mobile App" />
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
      featuredRestaurants: [
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
      ]
    }
  }
}
</script>

<style scoped>
/* Add your CSS styling here */
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
}

.app-download {
  display: flex;
  padding: 2rem;
  background-color: #f8f9fa;
  margin-top: 2rem;
}
</style>