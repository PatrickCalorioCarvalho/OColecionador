import { View, Text, Button, Image, StyleSheet } from 'react-native';
import * as SecureStore from 'expo-secure-store';
import * as WebBrowser from 'expo-web-browser';
import * as Linking from 'expo-linking';
import { router } from 'expo-router';

export default function Login() {
  const redirectUri = Linking.createURL('auth');
  const startLogin = async () => {
    const result = await WebBrowser.openAuthSessionAsync(
      'https://louse-model-lioness.ngrok-free.app/login?mobile=true',
      redirectUri
    );

    if (result.type === 'success' && result.url) {
      const token = Linking.parse(result.url).queryParams?.token;
      if (token && typeof token === 'string') {
        await SecureStore.setItemAsync('token', token);
        router.replace("/");
      }
    }
  };

  return (
    <View style={styles.container}>
      <Image source={require('../../assets/images/icon.png')} style={styles.logo} />
      <Text style={styles.title}>O Colecionador</Text>
      <Text style={styles.subtitle}>Organize sua coleção com estilo</Text>
      <View style={styles.buttonContainer}>
        <Button title="Entrar" onPress={startLogin} />
      </View>
    </View>
  );
}
const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#1E2A38',
    alignItems: 'center',
    justifyContent: 'center',
    paddingHorizontal: 20,
  },
  logo: {
    width: 240,
    height: 240,
    marginBottom: 20,
    resizeMode: 'contain',
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#ffffff',
    marginBottom: 10,
  },
  subtitle: {
    fontSize: 16,
    color: '#aaaaaa',
    marginBottom: 30,
    textAlign: 'center',
  },
  buttonContainer: {
    width: '100%',
    marginTop: 10,
  },
});
