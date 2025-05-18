import React from "react";
import { useRouter } from "expo-router";
import { useShareIntentContext } from "expo-share-intent";
import { Text, TextInput, View } from "react-native";
import { SummaryView } from "components/SummaryView";
import LoadingSpinner from "components/LoadingSpinner";
import { Button } from "components/Button";
import { fetchSummary } from "api";

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
                content url
              </Text>
              <View className="w-full px-3 py-3 bg-gray-100 rounded border border-gray-300">
                <TextInput
                  className="w-full text-black"
                  autoCapitalize="none"
                  autoCorrect={false}
                  value={text}
                  onChangeText={setText}
                  editable={!loading}
                />
              </View>
            </View>
            <Button
              onPress={() => resetShareIntent()}
              loading={loading}
              className="w-full bg-black py-3 px-5 rounded mb-2 items-center"
            >
              <Text className="text-white font-bold text-base">summarize</Text>
            </Button>
            {error && (
              <Text className="text-red-500 text-center mb-2">
                Error: {error}
              </Text>
            )}
          </View>
        </>
      )}
      {loading && <LoadingSpinner />}
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
