import api from "../services/API";


export interface Container {
  id: string;
  names: string[];
  image: string;
  command: string;
  state: string;
  status: string;
}

export const getContainers = () => api.get('/Docker');
export const startContainer = (id: string) => api.post(`/Docker/start/${id}`);
export const stopContainer = (id: string) => api.post(`/Docker/stop/${id}`);
export const restartContainer = (id: string) => api.post(`/Docker/restart/${id}`)