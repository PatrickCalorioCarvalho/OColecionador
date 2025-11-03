// app/(tabs)/account.tsx
import { View, Text, Image, Button, ActivityIndicator,StyleSheet } from 'react-native';
import * as SecureStore from 'expo-secure-store';
import { useEffect, useState } from 'react';
import { router } from 'expo-router';

export default function Account() {
  const [user, setUser] = useState<any>(null);
  const [loading, setLoading] = useState(true);

    useEffect(() => {
    const fetchUser = async () => {
        const rawToken = await SecureStore.getItemAsync('token');
        if (!rawToken) return;

        const [provider, cleanToken] = rawToken.split('_OC_');

        try {
        let response;

        if (provider === 'google') {
            response = await fetch('https://www.googleapis.com/oauth2/v3/userinfo', {
            headers: {
                Authorization: `Bearer ${cleanToken}`,
            },
            });
        } else if (provider === 'github') {
            response = await fetch('https://api.github.com/user', {
            headers: {
                Authorization: `Bearer ${cleanToken}`,
            },
            });
        }

        const data = await response?.json();
        setUser(data);
        } catch (error) {
        console.error('Erro ao buscar perfil:', error);
        } finally {
        setLoading(false);
        }
    };

    fetchUser();
    }, []);


  const logout = async () => {
    await SecureStore.deleteItemAsync('token');
    router.replace('/login');
  };

  if (loading) return <ActivityIndicator size="large" />;

  return (
    <View style={styles.container}>
      {user?.picture || user?.avatar_url ? (
        <Image
          source={{ uri: user.picture || user.avatar_url }}
          style={styles.avatar}
        />
      ) : null}
      <Text style={styles.name}>{user?.name || user?.login}</Text>
      <Button title="Sair da conta" onPress={logout} color="#a00000" />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#1E2A38',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 20,
  },
  avatar: {
    width: 120,
    height: 120,
    borderRadius: 60,
    marginBottom: 20,
    borderWidth: 2,
    borderColor: '#fff',
  },
  name: {
    fontSize: 22,
    color: '#fff',
    marginBottom: 10,
  },
});