<template>
  <footer class="footer">
    <div class="container footer-container">
      <div class="footer-column">
        <h3>TastyDelivery</h3>
        <p>Delicious food delivered to your doorstep. Discover the finest restaurants in your area.</p>
        <div class="social-icons">
          <a href="#"><i class="fab fa-facebook-f"></i></a>
          <a href="#"><i class="fab fa-twitter"></i></a>
          <a href="#"><i class="fab fa-instagram"></i></a>
        </div>
      </div>
      <div class="footer-column">
        <h4>Useful Links</h4>
        <ul>
          <li><router-link to="/">Home</router-link></li>
          <li><router-link to="/restaurants">Restaurants</router-link></li>
          <li><router-link to="/about">About Us</router-link></li>
          <li><router-link to="/contact">Contact Us</router-link></li>
        </ul>
      </div>
      <div class="footer-column">
        <h4>Help</h4>
        <ul>
          <li><router-link to="/faq">FAQ</router-link></li>
          <li><router-link to="/terms">Terms & Conditions</router-link></li>
          <li><router-link to="/privacy">Privacy Policy</router-link></li>
          <li><router-link to="/support">Support</router-link></li>
        </ul>
      </div>
      <div class="footer-column">
        <h4>Contact</h4>
        <p><i class="fas fa-map-marker-alt"></i> 123 Main Street, City</p>
        <p><i class="fas fa-phone"></i> +123 456 7890</p>
        <p><i class="fas fa-envelope"></i> info@tastydelivery.com</p>
      </div>
    </div>
    <div class="footer-bottom">
      <div class="container">
        <p>&copy; {{ currentYear }} TastyDelivery. All rights reserved.</p>
      </div>
    </div>
  </footer>
</template>

<script>
/* eslint-disable */
export default {
  name: 'Footer',
  computed: {
    currentYear() {
      return new Date().getFullYear()
    }
  }
}
</script>

<style scoped>
.footer {
  background-color: var(--dark-color);
  color: white;
  margin-top: auto;
}

.footer-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 2rem;
  padding: 3rem 0;
}

.footer-column h3 {
  font-size: 1.5rem;
  margin-bottom: 1rem;
}

.footer-column h4 {
  font-size: 1.2rem;
  margin-bottom: 1rem;
}

.footer-column p {
  margin-bottom: 1rem;
  color: #ccc;
}

.footer-column ul {
  list-style: none;
}

.footer-column ul li {
  margin-bottom: 0.5rem;
}

.footer-column ul li a {
  color: #ccc;
}

.footer-column ul li a:hover {
  color: var(--primary-color);
}

.social-icons {
  display: flex;
  gap: 1rem;
  margin-top: 1rem;
}

.social-icons a {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background-color: rgba(255, 255, 255, 0.1);
  color: white;
  transition: all 0.3s ease;
}

.social-icons a:hover {
  background-color: var(--primary-color);
}

.footer-bottom {
  background-color: rgba(0, 0, 0, 0.2);
  padding: 1rem 0;
  text-align: center;
}

.footer-bottom p {
  color: #ccc;
}

@media (max-width: 768px) {
  .footer-container {
    grid-template-columns: 1fr;
  }
}
</style>