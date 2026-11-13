export const number=(n:number|undefined,d=0)=>n===undefined?'—':new Intl.NumberFormat('zh-CN',{maximumFractionDigits:d}).format(n);
export const date=(s:string)=>new Date(s+'Z').toLocaleString('zh-CN',{month:'2-digit',day:'2-digit',hour:'2-digit',minute:'2-digit',hour12:false});
