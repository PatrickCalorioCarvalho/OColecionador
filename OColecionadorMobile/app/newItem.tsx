import React, { useEffect, useState } from "react";
import { TextInput, Button, Image, ScrollView, Alert } from "react-native";
import { Picker } from "@react-native-picker/picker";
import * as ImagePicker from "expo-image-picker";
import { createItem } from "../models/Items";
import { Categoria, getCategorias } from "@/models/Categorias";

export default function NewItem() {
  const [nome, setnome] = useState("");
  const [photos, setPhotos] = useState<string[]>([]);
  const [categoriaId, setCategoriaId] = useState<number | null>(null);
  const [categorias, setCategorias] = useState<Categoria[]>([]);

  useEffect(() => {
    getCategorias().then(setCategorias).catch(console.error);
  }, []);

  const pickImage = async () => {
    Alert.alert(
      'Selecionar imagem',
      'Escolha a origem da imagem',
      [
        {
          text: 'Câmera',
          onPress: async () => {
            let result = await ImagePicker.launchCameraAsync({
              mediaTypes: ImagePicker.MediaTypeOptions.Images,
              quality: 1,
            });

            if (!result.canceled) {
              console.log(result.assets[0].uri);
              setPhotos([...photos, result.assets[0].uri]);
            }
          },
        },
        {
          text: 'Galeria',
          onPress: async () => {
            let result = await ImagePicker.launchImageLibraryAsync({
              mediaTypes: ImagePicker.MediaTypeOptions.Images,
              quality: 1,
            });

            if (!result.canceled) {
              console.log(result.assets[0].uri);
              setPhotos([...photos, result.assets[0].uri]);
            }
          },
        },
        {
          text: 'Cancelar',
          style: 'cancel',
        },
      ],
      { cancelable: true }
    );
  };

  const saveItem = async () => {
    const formData = new FormData();
    formData.append("nome", nome);
    formData.append("categoriaId", categoriaId?.toString() || "");
    photos.forEach((p, i) => {
      formData.append("fotos", {
        uri: p,
        name: `photo${i}.jpg`,
        type: "image/jpeg",
      } as any);
    });

    await createItem(formData);
    setnome("");
    setPhotos([]);
  };

  return (
    <ScrollView style={{ padding: 20 }}>
      <TextInput
        placeholder="Título do item"
        value={nome}
        onChangeText={setnome}
        style={{ borderBottomWidth: 1, marginBottom: 10 }}
      />
      <Picker
          selectedValue={categoriaId}
          onValueChange={(itemValue) => setCategoriaId(itemValue)}
        >
          <Picker.Item label="Selecione uma categoria" value={null} />
          {categorias.map((c) => (
            <Picker.Item key={c.id} label={c.descricao} value={c.id} />
          ))}
      </Picker>
      <Button title="Selecionar Foto" onPress={pickImage} />
      <ScrollView horizontal>
        {photos.map((uri, idx) => (
          <Image
            key={idx}
            source={{ uri }}
            style={{ width: 100, height: 100, margin: 5 }}
          />
        ))}
      </ScrollView>
      <Button title="Salvar Item" onPress={saveItem} />
    </ScrollView>
  );
}
