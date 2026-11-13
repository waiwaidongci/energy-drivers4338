export async function request<T>(path:string,options:RequestInit={}):Promise<T>{
 const token=localStorage.getItem('energy-token');
 const response=await fetch('/api'+path,{...options,headers:{'Content-Type':'application/json',...(token?{Authorization:'Bearer '+token}:{}),...options.headers}});
 if(!response.ok){const e=await response.json().catch(()=>({detail:'网络请求失败'}));if(response.status===401&&path!='/auth/login'){localStorage.removeItem('energy-token');location.hash='/login';}throw new Error(typeof e.detail==='string'?e.detail:JSON.stringify(e.detail));}
 return response.json();
}
export const post=<T>(path:string,data:unknown)=>request<T>(path,{method:'POST',body:JSON.stringify(data)});
