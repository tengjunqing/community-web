import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/stores/user'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/auth/Login.vue'),
    meta: { requiresAuth: false },
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/views/auth/Register.vue'),
    meta: { requiresAuth: false },
  },
  {
    path: '/',
    component: () => import('@/components/layout/AppLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        name: 'Home',
        component: () => import('@/views/home/HomeView.vue'),
      },
      {
        path: 'profile/:id',
        name: 'Profile',
        component: () => import('@/views/profile/ProfileView.vue'),
        props: true,
      },
      {
        path: 'profile/edit',
        name: 'ProfileEdit',
        component: () => import('@/views/profile/ProfileEdit.vue'),
      },
      {
        path: 'post/create',
        name: 'PostCreate',
        component: () => import('@/views/post/PostCreate.vue'),
      },
      {
        path: 'post/:id',
        name: 'PostDetail',
        component: () => import('@/views/post/PostDetail.vue'),
        props: true,
      },
      {
        path: 'messages',
        name: 'Messages',
        component: () => import('@/views/message/MessageView.vue'),
      },
      {
        path: 'groups',
        name: 'Groups',
        component: () => import('@/views/group/GroupList.vue'),
      },
      {
        path: 'group/create',
        name: 'GroupCreate',
        component: () => import('@/views/group/GroupCreate.vue'),
      },
      {
        path: 'group/:id',
        name: 'GroupDetail',
        component: () => import('@/views/group/GroupDetail.vue'),
        props: true,
      },
    ],
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/',
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const userStore = useUserStore()
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth !== false)

  if (requiresAuth && !userStore.isAuthenticated) {
    next('/login')
  } else if (!requiresAuth && userStore.isAuthenticated) {
    next('/')
  } else {
    next()
  }
})

export default router
