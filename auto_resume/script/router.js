import { createRouter, createWebHistory } from 'vue-router'

export default createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', component: () => import('./views/Home.vue') },
    { path: '/jobs',
      children: [
        { path: '', component: () => import('./views/JobList.vue') },
        { path: ':id', component: () => import('./views/Job.vue') },
      ]

    },
    { 
      path: '/search/parameters',
      component: () => import('./views/Search.vue')
    },
    { path: '/resumes/:id', component: () => import('./views/Resume.vue') },
    { path: '/cover-letter', component: () => import('./views/CoverLetter.vue') },
  ]
})