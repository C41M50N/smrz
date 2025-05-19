import { useQuery } from "@tanstack/react-query";
import { fetchSummary } from "api";
import LoadingSpinner from "components/LoadingSpinner";
import { SummaryView } from "components/SummaryView";
import { router } from "expo-router";
import { useShareIntentContext } from "expo-share-intent";
import React from "react";
import { Text, View } from "react-native";

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

  const title = data ? (data.summary.match(/^# (.+)$/m)?.[1] ?? null) : null;
  const content = data ? data.summary.replace(/^# (.+)$/m, "") : null;

  return (
    <View className="h-full p-0">
      {(isLoading || isIntentLoading) && <LoadingSpinner />}
      {error && (
        <View className="flex-1 items-center justify-center">
          <Text className="text-red-500">{error.message}</Text>
        </View>
      )}
      {intentError && (
        <View className="flex-1 items-center justify-center">
          <Text className="text-red-500">{intentError}</Text>
        </View>
      )}
      {shareIntent.webUrl && title && content && (
        <SummaryView
          title={title}
          markdown={content}
          sourceUrl={shareIntent.webUrl}
        />
      )}
    </View>
  )
}
