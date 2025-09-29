import { useEffect, useState } from "react";
import { View, Text, FlatList, Image, StyleSheet } from "react-native";
import { getItems, Item } from "../models/Items";

export default function Index() {
  const [items, setItems] = useState<Item[]>([]);

  useEffect(() => {
    getItems().then(setItems).catch(console.error);
  }, []);

  return (
    <FlatList
      data={items}
      keyExtractor={(item) => item.id}
      numColumns={2}
      renderItem={({ item }) => (
        <View style={styles.card}>
          <Image source={{ uri: item.fotos[0] }} style={styles.image} />
          <Text style={styles.title}>{item.nome}</Text>
        </View>
      )}
    />
  );
}

const styles = StyleSheet.create({
  card: {
    flex: 1,
    margin: 4,
    backgroundColor: "#fff",
    borderRadius: 8,
    overflow: "hidden",
  },
  image: {
    width: "100%",
    height: 150,
    resizeMode: "cover",
  },
  title: {
    padding: 8,
    fontWeight: "bold",
  },
});
