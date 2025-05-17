import { useRouter } from "expo-router";
import { useShareIntentContext } from "expo-share-intent";
import { useEffect } from "react";
import { Text, View } from "react-native";

export default function Home() {
  const { hasShareIntent, shareIntent, error, resetShareIntent } = useShareIntentContext();

  return (
    <View className="flex-1 bg-white items-center justify-center p-5">
      {!hasShareIntent && (
        <Text className="text-3xl font-bold text-center mb-2">
          HOME
        </Text>
      )}
      {hasShareIntent && (
        <Text className="text-3xl font-bold text-center mb-2">
          CONTENT: {shareIntent.webUrl ?? "<NO URL>"}
        </Text>
      )}
    </View>
  );
}
