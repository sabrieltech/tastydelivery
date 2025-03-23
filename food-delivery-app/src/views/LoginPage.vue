<template>
  <div class="login-container container">
    <div class="login-card">
      <h1 class="login-title">Login</h1>
      
      <form @submit.prevent="handleLogin" class="login-form">
        <div class="form-group">
          <label for="username">Username</label>
          <div class="input-wrapper">
            <i class="fas fa-user"></i>
            <input 
              type="text" 
              id="username" 
              v-model="username" 
              placeholder="Enter your username"
              required
            />
          </div>
          <p v-if="errors.username" class="error-message">{{ errors.username }}</p>
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
          <p v-if="errors.password" class="error-message">{{ errors.password }}</p>
        </div>
        
        <div class="form-options">
          <div class="remember-me">
            <input type="checkbox" id="remember" v-model="rememberMe" />
            <label for="remember">Remember me</label>
          </div>
          <router-link to="/forgot-password" class="forgot-password">Forgot password?</router-link>
        </div>
        
        <button type="submit" class="btn btn-primary login-btn" :disabled="isLoading">
          <span v-if="isLoading"><i class="fas fa-spinner fa-spin"></i> Logging in...</span>
          <span v-else>Login</span>
        </button>
        
        <p v-if="successMessage" class="login-success">{{ successMessage }}</p>
        <p v-if="errorMessage" class="login-error">{{ errorMessage }}</p>
      </form>
      
      <div class="divider">
        <span>or</span>
      </div>
      
      <div class="social-login">
        <button class="social-btn google">
          <i class="fab fa-google"></i> Continue with Google
        </button>
        <button class="social-btn facebook">
          <i class="fab fa-facebook-f"></i> Continue with Facebook
        </button>
      </div>
      
      <div class="signup-link">
        Don't have an account? <router-link to="/signup">Sign up</router-link>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'LoginPage',
  data() {
    return {
      username: '',
      password: '',
      rememberMe: false,
      showPassword: false,
      isLoading: false,
      errorMessage: '',
      successMessage: '',
      errors: {
        username: '',
        password: ''
      }
    }
  },
  methods: {
    validateForm() {
      let isValid = true;
      this.errors = {
        username: '',
        password: ''
      };
      
      if (!this.username.trim()) {
        this.errors.username = 'Username is required';
        isValid = false;
      }
      
      if (!this.password) {
        this.errors.password = 'Password is required';
        isValid = false;
      } else if (this.password.length < 6) {
        this.errors.password = 'Password must be at least 6 characters';
        isValid = false;
      }
      
      return isValid;
    },
    async handleLogin() {
  if (!this.validateForm()) {
    return;
  }

  this.isLoading = true;
  this.errorMessage = '';
  this.successMessage = '';

  try {
    // Direct API call to the customer service to fetch CUST001
    const response = await fetch('http://localhost:5006/customer/CUST001');

    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
    }

    const result = await response.json();

    // Check if we got a valid response
    if (result.code === 200 && result.data) {
      // Store user information in localStorage
      localStorage.setItem('currentUser', JSON.stringify(result.data));
      localStorage.setItem('isAuthenticated', 'true');

      // Display success message
      this.successMessage = `Login successful! Welcome ${result.data.name}`;

      console.log('Login successful with CUST001 from database');

      // Dispatch a custom event to notify other components (like Navbar)
      window.dispatchEvent(new Event('user-logged-in'));

      // Redirect to /app/home after successful login
      setTimeout(() => {
        this.$router.push('/app/home');
      }, 1000);
    } else {
      this.errorMessage = 'Could not retrieve customer data';
    }
  } catch (error) {
    console.error('Login error:', error);
    this.errorMessage = 'Connection error. Please try again later.';
  } finally {
    this.isLoading = false;
  }
}
  }
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: calc(100vh - 200px);
  padding: 2rem 1rem;
}

.login-card {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
  padding: 2.5rem 2rem;
  width: 100%;
  max-width: 450px;
}

.login-title {
  color: var(--secondary-color);
  font-size: 1.8rem;
  font-weight: 600;
  margin-bottom: 1.5rem;
  text-align: center;
}

.login-form {
  margin-bottom: 1.5rem;
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

.error-message {
  color: var(--danger-color);
  font-size: 0.85rem;
  margin-top: 0.25rem;
}

.login-success {
  color: var(--success-color);
  text-align: center;
  margin-top: 0.5rem;
}

.form-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  font-size: 0.9rem;
}

.remember-me {
  display: flex;
  align-items: center;
}

.remember-me input {
  margin-right: 0.5rem;
}

.forgot-password {
  color: var(--accent-color);
  text-decoration: none;
}

.forgot-password:hover {
  text-decoration: underline;
}

.login-btn {
  width: 100%;
  padding: 0.75rem;
  font-size: 1rem;
  font-weight: 500;
  margin-bottom: 1rem;
}

.login-error {
  color: var(--danger-color);
  text-align: center;
  margin-top: 0.5rem;
}

.divider {
  display: flex;
  align-items: center;
  margin: 1.5rem 0;
}

.divider::before,
.divider::after {
  content: '';
  flex: 1;
  border-bottom: 1px solid #ddd;
}

.divider span {
  padding: 0 1rem;
  color: #777;
  font-size: 0.9rem;
}

.social-login {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.social-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0.75rem;
  border-radius: 50px;
  border: 1px solid #ddd;
  background-color: white;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.social-btn i {
  margin-right: 0.75rem;
}

.social-btn.google i {
  color: #DB4437;
}

.social-btn.facebook i {
  color: #4267B2;
}

.social-btn:hover {
  background-color: #f8f8f8;
}

.signup-link {
  text-align: center;
  font-size: 0.95rem;
}

.signup-link a {
  color: var(--primary-color);
  font-weight: 500;
  text-decoration: none;
}

.signup-link a:hover {
  text-decoration: underline;
}

@media (max-width: 480px) {
  .login-card {
    padding: 2rem 1.5rem;
  }
  
  .form-options {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.75rem;
  }
  
  .social-login {
    gap: 0.75rem;
  }
}
</style>