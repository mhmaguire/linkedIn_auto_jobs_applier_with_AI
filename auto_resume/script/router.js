import { createRouter, createWebHistory } from 'vue-router'

export default createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', component: () => import('./views/Home.vue') },
    { path: '/jobs', component: () => import('./views/JobList.vue') },
    { path: '/jobs/:id', component: () => import('./views/Job.vue') },
    { path: '/resume', component: () => import('./views/Resume.vue') },
    { path: '/cover-letter', component: () => import('./views/CoverLetter.vue') },
  ]
})