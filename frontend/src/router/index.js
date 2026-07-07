import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'home',
    component: () => import('@/views/HomeView.vue'),
  },
  {
    path: '/search',
    name: 'search',
    component: () => import('@/views/SearchView.vue'),
  },
  {
    path: '/talent/:id',
    name: 'talent-profile',
    component: () => import('@/views/TalentProfileView.vue'),
  },
  {
    path: '/talent/:id/book',
    name: 'booking-request',
    component: () => import('@/views/BookingRequestView.vue'),
  },
  {
    path: '/open-gig/new',
    name: 'open-gig-new',
    component: () => import('@/views/NewOpenGigView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/dashboard/open-gigs',
    name: 'my-open-gigs',
    component: () => import('@/views/MyOpenGigsView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/dashboard/open-gigs/:id',
    name: 'open-gig-detail',
    component: () => import('@/views/OpenGigDetailView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/venues',
    name: 'venues',
    component: () => import('@/views/VenuesView.vue'),
  },
  {
    path: '/login',
    name: 'login',
    component: () => import('@/views/AuthView.vue'),
  },
  {
    path: '/register',
    name: 'register',
    component: () => import('@/views/AuthView.vue'),
  },
  {
    path: '/dashboard',
    name: 'dashboard',
    component: () => import('@/views/DashboardView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/dashboard/bookings/:id',
    name: 'booking-detail',
    component: () => import('@/views/BookingDetailView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/dashboard/bookings/:bookingId/pay',
    name: 'booking-pay',
    component: () => import('@/views/PaymentCheckoutView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/payment/return',
    name: 'payment-return',
    component: () => import('@/views/PaymentReturnView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/partner',
    name: 'partner-dashboard',
    component: () => import('@/views/PartnerDashboardView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/partner/onboarding',
    name: 'partner-onboarding',
    component: () => import('@/views/PartnerOnboardingView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/packs',
    name: 'packs-catalog',
    component: () => import('@/views/PacksCatalogView.vue'),
  },
  {
    path: '/aliado/:userId',
    name: 'aliado-profile',
    component: () => import('@/views/AliadoProfileView.vue'),
  },
  {
    path: '/talent-onboarding',
    name: 'talent-onboarding',
    component: () => import('@/views/TalentOnboardingView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/talent-dashboard',
    name: 'talent-dashboard',
    component: () => import('@/views/TalentDashboardView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/admin',
    name: 'admin-dashboard',
    component: () => import('@/views/AdminDashboardView.vue'),
    meta: { requiresAuth: true, requiresAdmin: true },
  },
  {
    path: '/account',
    name: 'account',
    component: () => import('@/views/AccountView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/tiers',
    name: 'tiers',
    component: () => import('@/views/TiersView.vue'),
  },
  {
    path: '/como-funciona',
    name: 'how-it-works',
    component: () => import('@/views/HowItWorksView.vue'),
  },
  {
    path: '/forgot-password',
    name: 'forgot-password',
    component: () => import('@/views/ForgotPasswordView.vue'),
  },
  {
    path: '/reset-password',
    name: 'reset-password',
    component: () => import('@/views/ResetPasswordView.vue'),
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior() {
    return { top: 0 }
  },
})

router.beforeEach((to) => {
  if (to.meta.requiresAuth) {
    const token = localStorage.getItem('access_token')
    if (!token) {
      return { name: 'login', query: { redirect: to.fullPath } }
    }
  }
})

export default router
