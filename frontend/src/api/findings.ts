import {request} from './client';import type {Finding} from '../types/domain';export const getFindings=(run?:number)=>request<Finding[]>('/findings'+(run?'?run_id='+run:''));
