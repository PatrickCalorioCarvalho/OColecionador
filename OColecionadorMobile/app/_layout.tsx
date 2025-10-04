import { Tabs } from "expo-router";

export default function Layout() {
  return (
    <Tabs>
      <Tabs.Screen name="index" options={{ title: "Home" }} />
      <Tabs.Screen name="newItem" options={{ title: "Novo Item" }} />
    </Tabs>
  );
}
