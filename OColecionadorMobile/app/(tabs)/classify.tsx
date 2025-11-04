import React, { useState } from 'react';
import {
  View,
  Text,
  Image,
  StyleSheet,
  Alert,
  ScrollView,
  Button,
  TouchableOpacity,
  ActivityIndicator,
} from 'react-native';
import * as ImagePicker from 'expo-image-picker';
import { uploadClasificar } from '../../models/Clasificar';

export default function Classify() {
  const [photo, setPhoto] = useState<string | null>(null);
  const [resultado, setResultado] = useState<any | null>(null);
  const [loading, setLoading] = useState(false);

  const pickImage = async () => {
    Alert.alert('Selecionar imagem', 'Escolha a origem da imagem', [
      {
        text: 'Câmera',
        onPress: async () => {
          let result = await ImagePicker.launchCameraAsync({
            mediaTypes: ImagePicker.MediaTypeOptions.Images,
            quality: 1,
          });
          if (!result.canceled) {
            setPhoto(result.assets[0].uri);
            setResultado(null);
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
            setPhoto(result.assets[0].uri);
            setResultado(null);
          }
        },
      },
      { text: 'Cancelar', style: 'cancel' },
    ]);
  };

  const handleClasificar = async () => {
    if (!photo) {
      Alert.alert('Erro', 'Selecione uma imagem primeiro.');
      return;
    }

    const formData = new FormData();
    formData.append('Foto', {
      uri: photo,
      name: 'photo.jpg',
      type: 'image/jpeg',
    } as any);

    setLoading(true);
    try {
      const response = await uploadClasificar(formData);
      setResultado(response);
    } catch (error) {
      Alert.alert('Erro', 'Falha ao classificar a imagem.');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <ScrollView
      style={styles.scroll}
      contentContainerStyle={styles.content}
      showsVerticalScrollIndicator={false}
    >
    <TouchableOpacity
      style={[styles.buttonWrapper, { backgroundColor: photo ? '#e74c3c' : '#3498db' }]}
      onPress={photo ? () => { setPhoto(null); setResultado(null); } : pickImage}
    >
      <Text style={styles.buttonText}>
        {photo ? 'Limpar Imagem' : 'Selecionar Imagem'}
      </Text>
    </TouchableOpacity>

      {photo && (
        <Image source={{ uri: photo }} style={styles.selectedImage} resizeMode="contain" />
      )}

      {photo && (
        <View style={styles.analyzeButton}>
          <Button title="Analisar Foto" onPress={handleClasificar} color="#2ecc71" />
        </View>
      )}

      {loading && <ActivityIndicator size="large" color="#fff" style={{ marginTop: 20 }} />}

      {resultado && (
        <View style={styles.resultado}>
          <Text style={styles.resultTitle}>Classe: {resultado.classe}</Text>
          <Text style={styles.resultSubtitle}>
            Confiança: {(resultado.confianca * 100).toFixed(2)}%
          </Text>

          <Text style={styles.resultSubtitle}>Itens semelhantes:</Text>

          {Array.isArray(resultado?.items) && resultado.items.length > 0 ? (
            resultado.items.map((item: any, index: number) => (
            <View key={index} style={styles.card}>
              <Image source={{ uri: item.fotos[0] }} style={styles.cardImage} />
              <Text style={styles.cardText}>{item.nome}</Text>
              <Text style={styles.cardSubtext}>{item.categoria}</Text>
              <Text style={styles.cardSubtext}>Distância: {item.distancia.toFixed(4)}</Text>
            </View>
            ))
          ) : (
            <Text style={{ color: '#ccc' }}>Nenhum item semelhante encontrado.</Text>
          )}
        </View>
      )}
    </ScrollView>
  );
}
const styles = StyleSheet.create({
  scroll: {
    flex: 1,
    backgroundColor: '#1E2A38',
  },
  content: {
    flexGrow: 1,
    backgroundColor: '#1E2A38',
    padding: 20,
    
  },
  buttonWrapper: {
    backgroundColor: '#3498db',
    padding: 12,
    borderRadius: 8,
    marginBottom: 20,
  },
  buttonText: {
    color: '#fff',
    fontSize: 16,
  },
  selectedImage: {
    width: '100%',
    height: 300,
    borderRadius: 10,
    marginBottom: 20,
  },
  analyzeButton: {
    marginBottom: 20,
    width: '100%',
  },
  resultado: {
    width: '100%',
    marginTop: 20,
  },
  resultTitle: {
    fontSize: 20,
    color: '#fff',
    marginBottom: 5,
  },
  resultSubtitle: {
    fontSize: 16,
    color: '#ccc',
    marginBottom: 10,
  },
  card: {
    backgroundColor: '#2c3e50',
    borderRadius: 10,
    padding: 10,
    marginBottom: 16,
    alignItems: 'center',
  },
  cardImage: {
    width: '100%',
    height: 150,
    borderRadius: 8,
    marginBottom: 10,
  },
  cardText: {
    color: '#fff',
    fontSize: 16,
    textAlign: 'center',
  },
  cardSubtext: {
    color: '#ccc',
    fontSize: 12,
    textAlign: 'center',
  },
});
