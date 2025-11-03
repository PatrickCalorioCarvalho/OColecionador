import React, { useEffect, useState } from "react";
import { TextInput, Button, Image, ScrollView, Alert, View, FlatList, Text,StyleSheet  } from "react-native";
import { Picker } from "@react-native-picker/picker";
import * as ImagePicker from "expo-image-picker";
import { createItem } from "../../models/Items";
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
    <View style={styles.container}>
      <ScrollView contentContainerStyle={styles.scrollContent}>
        <Text style={styles.label}>Nome do item</Text>
        <TextInput
          placeholder="Digite o nome"
          placeholderTextColor="#aaa"
          value={nome}
          onChangeText={setnome}
          style={styles.input}
        />

        <Text style={styles.label}>Categoria</Text>
        <View style={styles.pickerWrapper}>
          <Picker
            selectedValue={categoriaId}
            onValueChange={(itemValue) => setCategoriaId(itemValue)}
            dropdownIconColor="#fff"
            style={styles.picker}
          >
            <Picker.Item label="Selecione uma categoria" value={null} />
            {categorias.map((c) => (
              <Picker.Item key={c.id} label={c.descricao} value={c.id} />
            ))}
          </Picker>
        </View>

        <View style={styles.buttonWrapper}>
          <Button title="Selecionar Foto" onPress={pickImage} />
        </View>

        {photos.length > 0 && (
          <View style={styles.photosSection}>
            <Text style={styles.label}>Fotos selecionadas</Text>
            <FlatList
              data={photos}
              horizontal
              keyExtractor={(item, index) => index.toString()}
              renderItem={({ item }) => (
                <Image source={{ uri: item }} style={styles.photo} />
              )}
            />
          </View>
        )}
      </ScrollView>

      <View style={styles.saveButton}>
        <Button title="Salvar Item" onPress={saveItem} color="#2ecc71" />
      </View>
    </View>
  );
}
const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#1E2A38',
  },
  scrollContent: {
    padding: 20,
    paddingBottom: 100, // espaço extra para o botão fixo
  },
  label: {
    fontSize: 16,
    color: '#fff',
    marginBottom: 5,
  },
  input: {
    borderWidth: 1,
    borderColor: '#444',
    borderRadius: 8,
    padding: 10,
    marginBottom: 20,
    color: '#fff',
    backgroundColor: '#2c3e50',
  },
  pickerWrapper: {
    borderWidth: 1,
    borderColor: '#444',
    borderRadius: 8,
    marginBottom: 20,
    backgroundColor: '#2c3e50',
  },
  picker: {
    color: '#fff',
  },
  buttonWrapper: {
    marginBottom: 20,
  },
  photosSection: {
    marginBottom: 20,
  },
  photo: {
    width: 100,
    height: 100,
    marginRight: 10,
    borderRadius: 8,
  },
  saveButton: {
    position: 'absolute',
    bottom: 20,
    left: 20,
    right: 20,
  },
});