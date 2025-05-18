import { useRouter } from "expo-router";
import { useShareIntentContext } from "expo-share-intent";
import React, { useEffect } from "react";
import { Button, Pressable, Share, Text, TextInput, View } from "react-native";
import Markdown from "react-native-marked";
import Fontisto from '@expo/vector-icons/Fontisto';

type SummaryResponse = { summary: string } | { error: string };

export default function Home() {
  const { hasShareIntent, shareIntent, error: intentError, resetShareIntent } = useShareIntentContext();

  const [rawContent, setRawContent] = React.useState<string>();
  const [loading, setLoading] = React.useState(false);
  const [error, setError] = React.useState<string | null>(intentError);

  const title = rawContent ? (rawContent.match(/^# (.+)$/m)?.[1] ?? null) : null;
  const content = rawContent ? rawContent.replace(/^# (.+)$/m, "").replace("### SUMMARY:", "") : null;

  const [text, setText] = React.useState<string>("");

  React.useEffect(() => {
    async function fetchSummary(url: string) {
      setLoading(true);
      const response = await (await fetch(`http://127.0.0.1:8000/summarize?url=${encodeURIComponent(url)}`, { method: "GET" })).json() as SummaryResponse;
      if ("error" in response) {
        console.error("Error fetching summary:", response.error);
        setError(response.error);
        setLoading(false);
        return;
      }
      console.debug("Summary response:", response);
      setRawContent(response.summary);
      setLoading(false);
    }
    if (hasShareIntent && shareIntent.webUrl && !rawContent) {
      console.debug("Share Intent Web URL:", shareIntent.webUrl);
      fetchSummary(shareIntent.webUrl);
    }
    console.debug("hasShareIntent:", hasShareIntent);
  }, [hasShareIntent, shareIntent]);

  return (
    <View className="h-full p-0">
      {!hasShareIntent && (
        <>
          <View className="h-2/5 flex items-center justify-center">
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
      {hasShareIntent && content && title && (
        <View className="pb-36">
          <View className="flex flex-row items-center justify-between border-b border-gray-300 gap-2.5 mb-5">
            <Text className="text-3xl font-semibold text-center mt-1 mb-2">
              {title}
            </Text>
            {/* Share Button with Icon */}
            <Pressable
              onPress={async () => {
                if (shareIntent.webUrl) {
                  try {
                    await Share.share({ title, message: `${title}\n${shareIntent.webUrl}` });
                  } catch (err) {
                    console.error("Share failed:", err);
                  }
                }
              }}
              accessibilityLabel="Share"
              className="p-0 justify-center items-center rounded-full"
            >
              <Fontisto name="share" size={16} color="black" />
            </Pressable>
          </View>
          <Markdown
            value={content}
            styles={{ // https://github.com/gmsgowtham/react-native-marked/blob/main/src/theme/types.ts
              text: { color: "black", fontSize: 14, lineHeight: 20 },
              paragraph: { paddingTop: 2, paddingBottom: 8 },
              h3: { fontSize: 20, paddingTop: 6, paddingBottom: 0 },
              list: { marginLeft: -6 },
              li: { fontSize: 20, lineHeight: 20, paddingTop: 2.5, paddingBottom: 2.5 }, // fontSize = size of bullet points
            }}
            theme={{ spacing: { xs: 0, s: 0, m: 0, l: 0 } }}
          />
        </View>
      )}
    </View>
  );
}
