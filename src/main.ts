import { createApp } from 'vue'
import App from './App.vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'

// 创建Vue应用实例
const app = createApp(App)

// 使用Element Plus组件库
app.use(ElementPlus)

// 挂载应用
app.mount('#app')