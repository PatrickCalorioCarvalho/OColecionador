import { Slot, Redirect, usePathname } from 'expo-router';
import * as SecureStore from 'expo-secure-store';
import { useEffect, useState } from 'react';
import { View, ActivityIndicator } from 'react-native';

export default function RootLayout() {
  const [token, setToken] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const pathname = usePathname();

  useEffect(() => {
    SecureStore.getItemAsync('token').then((storedToken) => {
      setToken(storedToken);
      setLoading(false);
    });
  }, []);

  if (loading) {
    return (
      <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center' }}>
        <ActivityIndicator size="large" />
      </View>
    );
  }

  const isAuthRoute = pathname === '/login';
  const isTabsRoute = pathname === '/home' || pathname === '/account' || pathname === '/classify' || pathname === '/newItem';

  if (!token && !isAuthRoute) {
    return <Redirect href="/login" />;
  }

  if (token && isAuthRoute) {
    return <Redirect href="/home" />;
  }

  if (token && !isAuthRoute && !isTabsRoute) {
    return <Redirect href="/home" />;
  }

  return <Slot />;
}