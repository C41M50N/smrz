import { useRouter } from "expo-router";
import { useShareIntentContext } from "expo-share-intent";
import React, { useEffect } from "react";
import { Button, Pressable, Share, Text, TextInput, View } from "react-native";
import { SummaryView } from "components/SummaryView";
import { fetchSummary } from "api";
import AntDesign from '@expo/vector-icons/AntDesign';

export default function Home() {
  const { hasShareIntent, shareIntent, error: intentError, resetShareIntent } = useShareIntentContext();

  const [rawContent, setRawContent] = React.useState<string>();
  const [loading, setLoading] = React.useState(false);
  const [error, setError] = React.useState<string | null>(intentError);

  const title = rawContent ? (rawContent.match(/^# (.+)$/m)?.[1] ?? null) : null;
  const content = rawContent ? rawContent.replace(/^# (.+)$/m, "") : null;

  const [text, setText] = React.useState<string>("");

  React.useEffect(() => {
    async function loadSummary(url: string) {
      setLoading(true);
      const response = await fetchSummary(url);
      if ("error" in response) {
        console.error("Error fetching summary:", response.error);
        setError(response.error);
        setLoading(false);
        return;
      }
      console.debug("Summary response:", response);
      setRawContent(response.summary);
      setLoading(false);
      setError(null);
    }
    if (hasShareIntent && shareIntent.webUrl && !rawContent) {
      console.debug("Share Intent Web URL:", shareIntent.webUrl);
      loadSummary(shareIntent.webUrl);
    }
  }, [hasShareIntent, shareIntent]);

  return (
    <View className="h-full p-0">
      {!hasShareIntent && (
        <>
          <View className="h-3/6 flex items-center justify-center">
            <Text className="text-3xl text-black font-bold text-center">
              smrz
            </Text>
          </View>
          <View className="bg-white flex items-center justify-center gap-y-4">
            <View className="w-full flex-col items-start justify-end gap-y-0">
              <Text className="text-gray-900 text-sm font-medium px-1 py-0.5">
                URL
              </Text>
              <View className="w-full bg-gray-100 rounded border border-gray-300">
                <TextInput
                  className="w-full px-3 py-4 text-base text-black"
                  autoCapitalize="none"
                  autoCorrect={false}
                  value={text}
                  onChangeText={setText}
                  editable={!loading}
                />
              </View>
            </View>
            <Pressable
              onPress={() => resetShareIntent()}
              className="w-full bg-black py-3 px-5 rounded mb-2 items-center"
            >
              <Text className="text-white font-bold text-base">summarize</Text>
            </Pressable>
            {error && (
              <Text className="text-red-500 text-center mb-2">
                Error: {error}
              </Text>
            )}
          </View>
        </>
      )}
      {loading && (
        <View className="flex-1 items-center justify-center">
          <AntDesign name="loading1" size={20} color="black" className="animate-spin" />
        </View>
      )}
      {hasShareIntent && content && title && shareIntent.webUrl && (
        <SummaryView
          title={title}
          markdown={content}
          sourceUrl={shareIntent.webUrl}
        />
      )}
    </View>
  );
}
