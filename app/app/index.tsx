import { useRouter } from "expo-router";
import { useShareIntentContext } from "expo-share-intent";
import { useEffect } from "react";
import { Text, View } from "react-native";

export default function Home() {
  const router = useRouter();
  const { hasShareIntent } = useShareIntentContext();

  useEffect(() => {
    if (hasShareIntent) {
      // we want to handle share intent event in a specific page
      console.debug("[expo-router-index] redirect to ShareIntent screen");
      router.replace({
        pathname: "shareintent",
      });
    }
  }, [hasShareIntent]);

  return (
    <View className="flex-1 bg-white items-center justify-center p-5">
      <Text className="text-xl font-bold text-center mb-2">Welcome to Expo Share Intent Demo !</Text>
      <Text>Try to share a content to access specific page</Text>
    </View>
  );
}
