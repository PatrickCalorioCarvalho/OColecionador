import { useState } from "react";
import { TextInput, Button, Image, ScrollView } from "react-native";
import * as ImagePicker from "expo-image-picker";
import { createItem } from "../models/Items";

export default function NewItem() {
  const [title, setTitle] = useState("");
  const [photos, setPhotos] = useState<string[]>([]);

  const pickImage = async () => {
    let result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.Images,
      quality: 1,
    });

    if (!result.canceled) {
      setPhotos([...photos, result.assets[0].uri]);
    }
  };

  const saveItem = async () => {
    const formData = new FormData();
    formData.append("title", title);
    photos.forEach((p, i) => {
      formData.append("photos", {
        uri: p,
        name: `photo${i}.jpg`,
        type: "image/jpeg",
      } as any);
    });

    await createItem(formData);
    setTitle("");
    setPhotos([]);
  };

  return (
    <ScrollView style={{ padding: 20 }}>
      <TextInput
        placeholder="Título do item"
        value={title}
        onChangeText={setTitle}
        style={{ borderBottomWidth: 1, marginBottom: 10 }}
      />
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
