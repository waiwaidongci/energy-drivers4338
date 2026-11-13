import {ref} from 'vue';
export function useTask(){const busy=ref(false),error=ref('');async function perform(action:()=>Promise<unknown>){busy.value=true;error.value='';try{return await action();}catch(e){error.value=e instanceof Error?e.message:String(e);}finally{busy.value=false;}}return {busy,error,perform};}
