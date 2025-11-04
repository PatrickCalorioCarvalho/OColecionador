import api from "../services/API";

export interface Clasificar {
  foto: string;
}

export const uploadClasificar = async (clasificar: FormData): Promise<Clasificar> => {
  const { data } = await api.post("/clasificar", clasificar, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return data;
};