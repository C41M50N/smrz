import React from "react";
import { useRouter } from "expo-router";
import { Pressable, Text, TextInput, View } from "react-native";

export default function Home() {
  const router = useRouter();
  const [text, setText] = React.useState<string>("");

  return (
    <View className="h-full p-0">
      <View className="h-3/6 flex items-center justify-center">
        <Text className="text-3xl text-black font-bold text-center">
          smrz
        </Text>
      </View>
      <View className="bg-white flex items-center justify-center gap-y-4">
        <View className="w-full flex-col items-start justify-end gap-y-0">
          <Text className="text-gray-900 text-sm font-medium px-1 py-0.5">
            content url
          </Text>
          <View className="w-full px-3 py-3 bg-gray-100 rounded border border-gray-300">
            <TextInput
              className="w-full text-black"
              autoCapitalize="none"
              autoCorrect={false}
              value={text}
              onChangeText={setText}
            />
          </View>
        </View>
        <Pressable
          onPress={() => {
            try {
              new URL(text);
              // If no error is thrown, it's a valid URL
              router.push(`/summary-reader?url=${encodeURIComponent(text)}`);
            } catch {
              // TODO: show error
            }
          }}
          className="w-full bg-black py-3 px-5 rounded mb-2 items-center"
        >
          <Text className="text-white font-bold text-base">summarize</Text>
        </Pressable>
      </View>
    </View>
  );
}
