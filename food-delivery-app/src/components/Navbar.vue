<template>
  <nav class="navbar">
    <div class="container navbar-container">
      <div class="navbar-logo">
        <router-link to="/">
          <h1>Tasty<span>Delivery</span></h1>
        </router-link>
      </div>
      <div class="navbar-toggle" @click="toggleMobileMenu">
        <i class="fas fa-bars"></i>
      </div>
      <ul class="navbar-menu" :class="{ 'active': mobileMenuOpen }">
        <li><router-link to="/">Home</router-link></li>
        <li><router-link to="/restaurants">Restaurants</router-link></li>
        <li><router-link to="/about">About</router-link></li>
        <li><router-link to="/contact">Contact</router-link></li>
        <li class="navbar-button"><router-link to="/login" class="btn btn-secondary">Login</router-link></li>
        <li class="navbar-button"><router-link to="/signup" class="btn btn-primary">Sign Up</router-link></li>
      </ul>
    </div>
  </nav>
</template>

<script>
/* eslint-disable */
export default {
  name: 'Navbar',
  data() {
    return {
      mobileMenuOpen: false
    }
  },
  methods: {
    toggleMobileMenu() {
      this.mobileMenuOpen = !this.mobileMenuOpen
    }
  }
}
</script>

<style scoped>
.navbar {
  background-color: white;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
  position: sticky;
  top: 0;
  z-index: 100;
}

.navbar-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 0;
}

.navbar-logo h1 {
  font-size: 1.5rem;
  color: var(--secondary-color);
}

.navbar-logo span {
  color: var(--primary-color);
}

.navbar-menu {
  display: flex;
  list-style: none;
  align-items: center;
}

.navbar-menu li {
  margin-left: 1.5rem;
}

.navbar-menu a {
  font-weight: 500;
}

.navbar-menu a:hover {
  color: var(--primary-color);
}

.navbar-toggle {
  display: none;
  font-size: 1.5rem;
  cursor: pointer;
}

@media (max-width: 768px) {
  .navbar-toggle {
    display: block;
  }

  .navbar-menu {
    position: absolute;
    top: 100%;
    left: 0;
    right: 0;
    flex-direction: column;
    background-color: white;
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
    padding: 1rem 0;
    display: none;
  }

  .navbar-menu.active {
    display: flex;
  }

  .navbar-menu li {
    margin: 0.5rem 0;
  }

  .navbar-button {
    margin-top: 0.5rem;
  }
}
</style>