import Vue from 'vue'
import VueRouter from 'vue-router'
import HomePage from '@/views/HomePage.vue'
import AboutPage from '@/views/AboutPage.vue'
import ContactPage from '@/views/ContactPage.vue'
import RestaurantsPage from '@/views/RestaurantsPage.vue'
import RestaurantDetailPage from '@/views/RestaurantDetailPage.vue'
import SignupPage from '@/views/SignupPage.vue'
import LoginPage from '@/views/LoginPage.vue'
import AppHomePage from '@/views/AppHomePage.vue'
import CartPage from '@/views/CartPage.vue'
import OrderSuccess from '@/views/OrderSuccess.vue'
import OrderPage from '@/views/Orderpage.vue'
import RefundPage from '@/views/RefundPage.vue'
import Restaurant from '@/views/Restaurant.vue'

Vue.use(VueRouter)

// Navigation guard for protected routes
const requireAuth = (to, from, next) => {
  const isAuthenticated = localStorage.getItem('isAuthenticated') === 'true'
  if (isAuthenticated) {
    next()
  } else {
    next('/login')
  }
}

// Navigation guard for restaurant staff
// eslint-disable-next-line no-unused-vars
const requireRestaurantAuth = (to, from, next) => {
  // In a real app, you would check for restaurant staff credentials
  // For this example, we'll use a simple flag in localStorage
  const isRestaurantStaff = localStorage.getItem('isRestaurantStaff') === 'true'
  if (isRestaurantStaff) {
    next()
  } else {
    // Redirect to restaurant login page (you would need to create this)
    // For now, we'll redirect to the main login page
    next('/restaurant/login')
  }
}

const routes = [
  {
    path: '/',
    name: 'Home',
    component: HomePage
  },
  {
    path: '/about',
    name: 'About',
    component: AboutPage
  },
  {
    path: '/contact',
    name: 'Contact',
    component: ContactPage
  },
  {
    path: '/restaurants',
    name: 'Restaurants',
    component: RestaurantsPage
  },
  {
    path: '/restaurants/:id',
    name: 'RestaurantDetail',
    component: RestaurantDetailPage
  },
  {
    path: '/signup',
    name: 'Signup',
    component: SignupPage
  },
  {
    path: '/login',
    name: 'Login',
    component: LoginPage
  },
  {
    path: '/app/home',
    name: 'AppHome',
    component: AppHomePage,
    beforeEnter: requireAuth
  },
  {
    path: '/restaurant/:id/menu',
    name: 'RestaurantMenu',
    component: () => import('../views/RestaurantMenu.vue')
  },
  {
    path: '/cart',
    name: 'Cart',
    component: CartPage,
    beforeEnter: requireAuth
  },
  {
    path: '/checkout',
    name: 'Checkout',
    component: () => import('../views/Checkout.vue'),
    beforeEnter: requireAuth
  },
  {
    path: '/app/order-success',
    name: 'OrderSuccess',
    component: OrderSuccess,
    beforeEnter: requireAuth
  },
  {
    path: '/app/order/:id',
    name: 'OrderDetail',
    component: OrderPage,
    beforeEnter: requireAuth
  },
  {
    path: '/app/refund/:id?',
    name: 'Refund',
    component: RefundPage,
    beforeEnter: requireAuth,
    props: true
  },
  
  // Restaurant Dashboard route - outside of customer app
  {
    path: '/restaurant-dashboard',
    name: 'RestaurantDashboard',
    component: Restaurant,
    meta: { 
      layout: 'restaurant', // Optional: Use this if you want to create a specific layout
      hideNavbar: true // Use this flag to hide the navbar
    }
    // Uncomment the next line to enable authentication once you have a restaurant login
    // beforeEnter: requireRestaurantAuth
  },
  
  {
    path: '/restaurant/login',
    name: 'RestaurantLogin',
    component: () => import('../views/RestaurantLogin.vue'),
    meta: { hideNavbar: true }
  }
]

const router = new VueRouter({
  mode: 'history',
  base: process.env.BASE_URL,
  routes
})

export default router