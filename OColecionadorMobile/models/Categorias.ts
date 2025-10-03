import api from "../services/API";

export interface Categoria {
  id: number;
  descricao: string;
}

export const getCategorias = async (): Promise<Categoria[]> => {
  const { data } = await api.get("/Categorias");
  return data;
};
