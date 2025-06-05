import { useQuery } from "@tanstack/react-query";
import { fetchSummary } from "api";
import LoadingSpinner from "components/LoadingSpinner";
import { MarkdownViewer } from "components/MarkdownViewer";
import { router } from "expo-router";
import { useShareIntentContext } from "expo-share-intent";
import React from "react";
import { Platform, Pressable, SafeAreaView, Share, Text, View } from "react-native";
import { Button } from "components/Button";
import Ionicons from '@expo/vector-icons/Ionicons';
import { Container } from "components/Container";
import { Tabs } from "components/tabs";

const TabIds = {
  CONTENT: 'content',
  SUMMARY: 'summary',
  NOTES: 'notes',
} as const;

export default function SummaryReaderIntentPage() {
  const { isReady: isIntentLoading, hasShareIntent, shareIntent, error: intentError, resetShareIntent } = useShareIntentContext();
  React.useEffect(() => {
    console.debug("[expo-router-native-intent] inside useEffect");
    if (!isIntentLoading) {
      console.debug("[expo-router-native-intent] no share intent detected");
      resetShareIntent();
      router.replace("/");
    }
  }, [hasShareIntent, shareIntent.webUrl, resetShareIntent, isIntentLoading]);

  const { data, error, isLoading } = useQuery({
    queryKey: ["summary", shareIntent.webUrl],
    queryFn: () => fetchSummary(shareIntent.webUrl!),
    staleTime: Infinity,
    enabled: !!shareIntent.webUrl,
  });

  const url = shareIntent.webUrl;
  // const title = data ? (data.summary.match(/^# (.+)$/m)?.[1] ?? null) : null;
  const content = data ? data.content.replace(/^# (.+)$/m, "") : null;
  const summary = data ? data.summary.replace(/^# (.+)$/m, "") : null;

  return (
    <View className="h-full p-0">
      <SafeAreaView>
        {(isLoading || isIntentLoading) && <LoadingSpinner />}
        {error && (
          <View className="flex-1 items-center justify-center">
            <Text className="text-red-500">{error.message}</Text>
            <Button
              className="mt-4"
              onPress={() => router.replace("/")}
            >
              Go Back
            </Button>
          </View>
        )}
        {intentError && (
          <View className="flex-1 items-center justify-center">
            <Text className="text-red-500">{intentError}</Text>
            <Button
              className="mt-4"
              onPress={() => router.replace("/")}
            >
              Go Back
            </Button>
          </View>
        )}
        {url && data && (
          <View className="pb-3 flex items-center border-b border-gray-300">
            <View className="mx-[46px] flex flex-row items-center justify-between gap-3">
              <Pressable
                className="items-center"
                accessibilityLabel="Back"
                onPress={() => router.back()}
              >
                <Ionicons name="arrow-back" size={22} color="black" />
              </Pressable>
              <Text className="px-2 text-xl font-semibold text-center line-clamp-1">
                {data.title}
              </Text>
              <Pressable
                className="items-center"
                accessibilityLabel="Share"
                onPress={() => {
                  if (Platform.OS === "ios") {
                    Share.share({ url: url });
                  } else {
                    Share.share({ message: url });
                  }
                }}
              >
                <Ionicons name="share-social" size={22} color="black" />
              </Pressable>
            </View>
          </View>
        )}
      </SafeAreaView>

      {url && data && content && summary && (
        <Tabs
          defaultTab={TabIds.CONTENT}
          tabs={[
            {
              id: TabIds.CONTENT,
              icon: "document-text",
              label: "Content",
              content: (
                <Container>
                  <MarkdownViewer markdown={content} />
                </Container>
              ),
            },
            {
              id: TabIds.SUMMARY,
              icon: "chatbubble-ellipses",
              label: "Summary",
              content: (
                <Container>
                  <MarkdownViewer markdown={summary} />
                </Container>
              ),
            },
            {
              id: TabIds.NOTES,
              icon: "pencil",
              label: "Notes",
              content: (
                <Text className="p-4 text-gray-500">
                  Notes feature is coming soon!
                </Text>
              ),
            },
          ]}
        />
      )}
    </View>
  )
}
