<template>
  <div id="app">
    <Navbar />
    <router-view />
    <Footer />
  </div>
</template>

<script>
import Navbar from '@/components/Navbar.vue'
import Footer from '@/components/Footer.vue'

export default {
  name: 'App',
  components: {
    Navbar,
    Footer
  }
}
</script>

<style>
:root {
  --primary-color: #ff5a5f;
  --secondary-color: #484848;
  --accent-color: #00a699;
  --light-color: #f7f7f7;
  --dark-color: #222222;
  --success-color: #28a745;
  --warning-color: #ffc107;
  --danger-color: #dc3545;
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Poppins', sans-serif;
  font-size: 16px;
  line-height: 1.6;
  color: var(--secondary-color);
  background-color: var(--light-color);
}

#app {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

a {
  text-decoration: none;
  color: var(--secondary-color);
}

.btn {
  display: inline-block;
  padding: 0.5rem 1.5rem;
  border-radius: 50px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  border: none;
}

.btn-primary {
  background-color: var(--primary-color);
  color: white;
}

.btn-primary:hover {
  background-color: #e84853;
}

.btn-secondary {
  background-color: white;
  color: var(--primary-color);
  border: 1px solid var(--primary-color);
}

.btn-secondary:hover {
  background-color: var(--primary-color);
  color: white;
}
</style>