<template>
  <div class="restaurant-login">
    <div class="login-container">
      <div class="login-card">
        <div class="logo">
          <img src="/logo.png" alt="Restaurant Logo" v-if="false">
          <i class="fas fa-utensils" v-else></i>
          <h1>Restaurant Portal</h1>
        </div>
        
        <form @submit.prevent="handleLogin" class="login-form">
          <div class="form-group">
            <label for="restaurant-id">Restaurant ID</label>
            <div class="input-wrapper">
              <i class="fas fa-store"></i>
              <input 
                type="text" 
                id="restaurant-id" 
                v-model="restaurantId" 
                placeholder="Enter your restaurant ID"
                required
              />
            </div>
          </div>
          
          <div class="form-group">
            <label for="password">Password</label>
            <div class="input-wrapper">
              <i class="fas fa-lock"></i>
              <input 
                :type="showPassword ? 'text' : 'password'" 
                id="password" 
                v-model="password" 
                placeholder="Enter your password"
                required
              />
              <i 
                :class="['password-toggle', showPassword ? 'fa-eye-slash' : 'fa-eye', 'fas']" 
                @click="showPassword = !showPassword"
              ></i>
            </div>
          </div>
          
          <button type="submit" class="btn btn-primary login-btn" :disabled="isLoading">
            <span v-if="isLoading"><i class="fas fa-spinner fa-spin"></i> Logging in...</span>
            <span v-else>Login</span>
          </button>
          
          <p v-if="errorMessage" class="error-message">{{ errorMessage }}</p>
        </form>
        
        <div class="info-section">
          <p>This page is for restaurant staff only. If you're a customer, please <router-link to="/login">click here</router-link> to login to the customer portal.</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'RestaurantLogin',
  data() {
    return {
      restaurantId: '',
      password: '',
      showPassword: false,
      isLoading: false,
      errorMessage: ''
    }
  },
  methods: {
    async handleLogin() {
      this.isLoading = true;
      this.errorMessage = '';
      
      try {
        // For demonstration purposes, we're using hardcoded credentials
        // In a real app, you would validate against your backend
        if (this.restaurantId === 'REST001' && this.password === 'password') {
          // Store authentication state in localStorage
          localStorage.setItem('isRestaurantStaff', 'true');
          localStorage.setItem('restaurantId', this.restaurantId);
          
          // Redirect to restaurant dashboard
          this.$router.push('/restaurant-dashboard');
        } else {
          this.errorMessage = 'Invalid credentials. Please try again.';
        }
      } catch (error) {
        console.error('Login error:', error);
        this.errorMessage = 'Something went wrong. Please try again.';
      } finally {
        this.isLoading = false;
      }
    }
  }
}
</script>

<style scoped>
.restaurant-login {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #f8f9fa;
}

.login-container {
  width: 100%;
  max-width: 450px;
  padding: 2rem 1rem;
}

.login-card {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
  padding: 2.5rem 2rem;
}

.logo {
  text-align: center;
  margin-bottom: 2rem;
}

.logo i {
  font-size: 3rem;
  color: var(--primary-color);
  margin-bottom: 1rem;
}

.logo h1 {
  font-size: 1.8rem;
  color: var(--secondary-color);
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: var(--secondary-color);
}

.input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
  border: 1px solid #ddd;
  border-radius: 4px;
  overflow: hidden;
}

.input-wrapper i {
  padding: 0 1rem;
  color: #999;
}

.input-wrapper input {
  flex: 1;
  padding: 0.75rem;
  border: none;
  outline: none;
  font-size: 1rem;
}

.password-toggle {
  cursor: pointer;
  padding-right: 1rem;
}

.login-btn {
  width: 100%;
  padding: 0.75rem;
  font-size: 1rem;
  margin-bottom: 1rem;
}

.error-message {
  color: var(--danger-color);
  text-align: center;
  margin-top: 1rem;
}

.info-section {
  margin-top: 2rem;
  text-align: center;
  padding-top: 1rem;
  border-top: 1px solid #eee;
  font-size: 0.9rem;
  color: #6c757d;
}

.info-section a {
  color: var(--primary-color);
}
</style>