import {onUnmounted} from 'vue';
export function usePolling(action:()=>Promise<unknown>,interval=2500){const timer=setInterval(()=>action().catch(()=>{}),interval);onUnmounted(()=>clearInterval(timer));}
