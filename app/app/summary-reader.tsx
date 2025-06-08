import { useQuery } from "@tanstack/react-query";
import { fetchSummary } from "api";
import { Container } from "components/Container";
import LoadingSpinner from "components/LoadingSpinner";
import { MarkdownViewer } from "components/MarkdownViewer";
import { Tabs } from "components/tabs";
import { router, useLocalSearchParams } from "expo-router";
import React from "react";
import { Platform, Pressable, SafeAreaView, Share, Text, View } from "react-native";
import Ionicons from '@expo/vector-icons/Ionicons';

const TabIds = {
  CONTENT: 'content',
  SUMMARY: 'summary',
  NOTES: 'notes',
} as const;

export default function SummaryReaderPage() {
  const { url } = useLocalSearchParams<{ url?: string }>();
  React.useEffect(() => {
    if (!url) router.replace("/");
  }, [url]);

  const { data, error, isLoading, refetch } = useQuery({
    queryKey: ["summary", url],
    queryFn: () => fetchSummary(url!),
    staleTime: Infinity,
    enabled: !!url,
  });

  // const title = data ? (data.summary.match(/^# (.+)$/m)?.[1] ?? null) : null;
  const content = data ? data.content.replace(/^# (.+)$/m, "").concat("\n## \n") : null;
  const summary = data ? data.summary.replace(/^# (.+)$/m, "").concat("\n## \n") : null;

  return (
    <View className="h-full p-0 m-0">
      <SafeAreaView>
        {isLoading && (
          <View className="h-full items-center justify-center">
            <LoadingSpinner />
          </View>
        )}
        {error && (
          <View className="h-full items-center justify-center gap-4">
            <Text className="text-base text-red-600">{error.message}</Text>
            <View className="flex flex-row gap-2">
              <Pressable
                className="bg-gray-200 px-4 py-2 rounded"
                accessibilityLabel="Go Back"
                accessibilityHint="Return to the home page"
                accessibilityRole="button"
                onPress={() => router.replace("/")}
              >
                <Text className="text-gray-800 font-semibold">
                  Go Back
                </Text>
              </Pressable>
              <Pressable
                className="bg-gray-200 px-4 py-2 rounded"
                accessibilityLabel="Try Again"
                accessibilityHint="Try to summarize the content again"
                accessibilityRole="button"
                onPress={() => refetch()}
              >
                <Text className="text-gray-800 font-semibold">
                  Try Again
                </Text>
              </Pressable>
            </View>
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
              <Text className="w-full px-2 text-xl font-semibold text-center line-clamp-1">
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
