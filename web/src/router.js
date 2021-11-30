import { createRouter, createWebHistory } from 'vue-router'
import Home from './components/HelloWorld.vue'
import PuntosYRecorridos from './views/PuntosYRecorridos.vue'
import Denuncias from './views/DenunciaCreate.vue'
import ZonasInundables from './components/ZonasInundables.vue'
import ZonaInundableShow from './components/ZonaShow.vue'

const routes = [
    {
        path: '/',
        name: 'home',
        component: Home
    },
    {
        path: '/puntos_y_recorridos',
        name: 'puntos_y_recorridos',
        component: PuntosYRecorridos
    },
    {
        path: '/denuncia',
        name: 'denuncia',
        component: Denuncias
    },
    {
        path: '/zonas_inundables',
        name: 'zonas_inundables',
        component: ZonasInundables
    },
    {
        path: '/zonas_inundables/:id',
        name: 'zona_inundable',
        component: ZonaInundableShow
    },

]

const router = createRouter({
    history: createWebHistory(),
    routes
})

export default router