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
        <!-- Show these items only when user is NOT logged in -->
        <template v-if="!isLoggedIn">
          <li class="navbar-button"><router-link to="/login" class="btn btn-secondary">Login</router-link></li>
          <li class="navbar-button"><router-link to="/signup" class="btn btn-primary">Sign Up</router-link></li>
        </template>
        <!-- Show user info and logout when user IS logged in -->
        <template v-else>
          <!-- Order Now button that appears after login -->
          <li class="navbar-button order-now-button">
            <router-link to="/app/home" class="btn btn-primary order-now-btn">
              <i class="fas fa-utensils"></i> Order Now
            </router-link>
          </li>
          <li class="user-info">
            <div class="user-dropdown">
              <span class="user-name" @click="toggleUserMenu">
                <i class="fas fa-user-circle"></i> {{ userName }}
                <i class="fas fa-chevron-down"></i>
              </span>
              <div class="dropdown-menu" v-show="userMenuOpen">
                <router-link to="/profile">My Profile</router-link>
                <router-link to="/orders">My Orders</router-link>
                <a href="#" @click.prevent="logout">Logout</a>
              </div>
            </div>
          </li>
        </template>
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
      mobileMenuOpen: false,
      userMenuOpen: false,
      currentUser: null
    }
  },
  computed: {
    isLoggedIn() {
      return this.currentUser !== null;
    },
    userName() {
      return this.currentUser ? this.currentUser.name : '';
    }
  },
  methods: {
    toggleMobileMenu() {
      this.mobileMenuOpen = !this.mobileMenuOpen;
    },
    toggleUserMenu() {
      this.userMenuOpen = !this.userMenuOpen;
    },
    logout() {
      // Clear user data from localStorage
      localStorage.removeItem('currentUser');
      localStorage.removeItem('isAuthenticated');

      // Reset the current user
      this.currentUser = null;

      // Close any open menus
      this.userMenuOpen = false;
      
      // Dispatch a custom event for other components to respond to logout
      window.dispatchEvent(new Event('user-logged-out'));

      // Redirect to home page
      if (this.$route.path !== '/') {
        this.$router.push('/');
      }
    },
    checkUserSession() {
      // Get user data from localStorage
      const userData = localStorage.getItem('currentUser');
      if (userData) {
        try {
          this.currentUser = JSON.parse(userData);
        } catch (e) {
          console.error('Error parsing user data', e);
          this.currentUser = null;
        }
      } else {
        this.currentUser = null;
      }
    }
  },
  created() {
    // Check if user is logged in when component is created
    this.checkUserSession();
    
    // Listen for storage events (in case login/logout happens in another tab)
    window.addEventListener('storage', this.checkUserSession);
  },
  mounted() {
    // Setup a custom event listener for login events
    window.addEventListener('user-logged-in', this.checkUserSession);
  },
  beforeDestroy() {
    // Clean up event listeners
    window.removeEventListener('storage', this.checkUserSession);
    window.removeEventListener('user-logged-in', this.checkUserSession);
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

.navbar-toggle {
  display: none;
  font-size: 1.5rem;
  cursor: pointer;
}

/* Order Now button styles */
.order-now-btn {
  display: flex;
  align-items: center;
  padding: 0.5rem 1rem;
  font-weight: bold;
  background-color: var(--primary-color);
  color: white;
  border-radius: 50px;
  transition: all 0.3s ease;
  text-transform: uppercase;
  font-size: 0.9rem;
  letter-spacing: 0.5px;
  border: 2px solid transparent;
}

.order-now-btn i {
  margin-right: 0.5rem;
}

.order-now-btn:hover {
  background-color: white;
  color: var(--primary-color);
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  border: 2px solid #0056b3;
}


/* User dropdown styles */
.user-info {
  position: relative;
}

.user-name {
  display: flex;
  align-items: center;
  cursor: pointer;
  font-weight: 500;
  color: var(--primary-color);
}

.user-name i {
  margin-right: 5px;
}

.user-name .fa-chevron-down {
  font-size: 0.75rem;
  margin-left: 5px;
}

.dropdown-menu {
  position: absolute;
  top: 100%;
  right: 0;
  background: white;
  min-width: 160px;
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
  border-radius: 4px;
  padding: 0.5rem 0;
  z-index: 10;
}

.dropdown-menu a {
  display: block;
  padding: 0.5rem 1rem;
  color: var(--secondary-color);
  text-decoration: none;
}

.dropdown-menu a:hover {
  background-color: #f5f5f5;
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
  
  .user-info {
    width: 100%;
    text-align: center;
  }
  
  .dropdown-menu {
    position: relative;
    width: 100%;
    box-shadow: none;
    margin-top: 0.5rem;
  }
  
  /* Mobile-specific styles for Order Now button */
  .order-now-button {
    width: 80%;
    margin: 0.5rem auto;
  }
  
  .order-now-btn {
    width: 100%;
    justify-content: center;
  }
}
</style>