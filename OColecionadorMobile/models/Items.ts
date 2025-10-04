import api from "../services/API";

export interface Item {
  id: string;
  nome: string;
  categoriaId: number;
  fotos: string[];
}

export const getItems = async (): Promise<Item[]> => {
  const { data } = await api.get("/Items");
  return data;
};

export const createItem = async (item: FormData): Promise<Item> => {
  const { data } = await api.post("/Items", item, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return data;
};