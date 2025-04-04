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
  }
]

const router = new VueRouter({
  mode: 'history',
  base: process.env.BASE_URL,
  routes
})

export default router