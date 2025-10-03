import React, { useEffect, useState } from "react";
import { TextInput, Button, Image, ScrollView, Alert, View, FlatList, Text } from "react-native";
import { Picker } from "@react-native-picker/picker";
import * as ImagePicker from "expo-image-picker";
import { createItem } from "../models/Items";
import { Categoria, getCategorias } from "@/models/Categorias";

export default function NewItem() {
  const [nome, setnome] = useState("");
  const [photos, setPhotos] = useState<string[]>([]);
  const [categoriaId, setCategoriaId] = useState<number | null>(null);
  const [categorias, setCategorias] = useState<Categoria[]>([]);
  const [isSaving, setIsSaving] = useState(false);

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
    if (isSaving) return;
    setIsSaving(true);
    if (!nome.trim()) {
      Alert.alert("Erro", "O nome do item é obrigatório.");
      setIsSaving(false);
      return;
    }
    if (!categoriaId) {
      Alert.alert("Erro", "A categoria do item é obrigatória.");
      setIsSaving(false);
      return;
    }
    if (photos.length === 0) {
      Alert.alert("Erro", "Ao menos uma foto é obrigatória.");
      setIsSaving(false);
      return;
    }

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
    setCategoriaId(null);
    setIsSaving(false);
    Alert.alert("Sucesso", "Item criado com sucesso!");
  };

  return (
    <ScrollView contentContainerStyle={{ padding: 20 }}>
      <Text style={{ fontSize: 16, marginBottom: 5 }}>Nome do item</Text>
      <TextInput
        placeholder="Digite o nome"
        value={nome}
        onChangeText={setnome}
        style={{
          borderWidth: 1,
          borderColor: '#ccc',
          borderRadius: 8,
          padding: 10,
          marginBottom: 20,
        }}
      />
      <Text style={{ fontSize: 16, marginBottom: 5 }}>Categoria</Text>
      <View
        style={{
          borderWidth: 1,
          borderColor: '#ccc',
          borderRadius: 8,
          marginBottom: 20,
        }}
      >
        <Picker
          selectedValue={categoriaId}
          onValueChange={(itemValue) => setCategoriaId(itemValue)}
        >
          <Picker.Item label="Selecione uma categoria" value={null} />
          {categorias.map((c) => (
            <Picker.Item key={c.id} label={c.descricao} value={c.id} />
          ))}
        </Picker>
      </View>
      <View style={{ marginBottom: 20 }}>
        <Button title="Selecionar Foto" onPress={pickImage} />
      </View>
      {photos.length > 0 && (
        <View style={{ marginBottom: 20 }}>
          <Text style={{ fontSize: 16, marginBottom: 10 }}>Fotos selecionadas</Text>
          <FlatList
            data={photos}
            horizontal
            keyExtractor={(item, index) => index.toString()}
            renderItem={({ item }) => (
              <Image
                source={{ uri: item }}
                style={{ width: 100, height: 100, marginRight: 10, borderRadius: 8 }}
              />
            )}
          />
        </View>
      )}
      <View style={{ marginBottom: 40 }}>
        <Button title="Salvar Item" onPress={saveItem} />
      </View>
    </ScrollView>
  );
}
