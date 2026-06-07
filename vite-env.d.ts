/// <reference types="vite/client" />

// 声明Vue单文件组件类型
declare module '*.vue' {
  import type { DefineComponent } from 'vue'
  const component: DefineComponent<{}, {}, any>
  export default component
}

declare module 'vite'

declare module '@vitejs/plugin-vue'

declare module '@vitejs/plugin-vue-jsx'

declare interface ImportMetaEnv {
  readonly VITE_API_BASE_URL: string
  readonly VITE_APP_TITLE: string
  readonly VITE_ENV: 'development' | 'production' | 'test'
}

declare interface ImportMeta {
  readonly env: ImportMetaEnv
}