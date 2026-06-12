import { defineConfig, loadEnv } from 'vite';
import vue from '@vitejs/plugin-vue';
export default defineConfig(({ mode }) => {
    const env = loadEnv(mode, process.cwd(), '');
    const contractTarget = env.VITE_CONTRACT_PROXY_TARGET || 'http://127.0.0.1:8000';
    const loginTarget = env.VITE_LOGIN_PROXY_TARGET || 'http://127.0.0.1:8000';
    return {
        plugins: [vue()],
        base: '/mobile/contract/',
        server: {
            proxy: {
                '/api/contract': {
                    target: contractTarget,
                    changeOrigin: true,
                    rewrite: (path) => path.replace(/^\/api\/contract/, '/api/v1/contract'),
                },
                '/api/auth': {
                    target: loginTarget,
                    changeOrigin: true,
                    rewrite: (path) => path.replace(/^\/api\/auth/, ''),
                },
            },
        },
    };
});
