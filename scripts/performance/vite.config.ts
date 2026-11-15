import {defineConfig} from 'vite';
import react from '@vitejs/plugin-react';
import {resolve} from 'node:path';
export default defineConfig({
 root:resolve(import.meta.dirname),plugins:[react()],
 // React's production profiling build measures real commits without dev/HMR.
 resolve:{alias:{'react-dom/client':'react-dom/profiling'}},
 build:{outDir:resolve(import.meta.dirname,'../../.tools/performance-web'),emptyOutDir:true},
});
