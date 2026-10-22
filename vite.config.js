import { defineConfig } from 'vite';
export default defineConfig({server:{proxy:{'/api':`http://127.0.0.1:${process.env.OPENING_DAY_API_PORT||8000}`}}});
