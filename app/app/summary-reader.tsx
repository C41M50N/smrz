import { useQuery } from "@tanstack/react-query";
import { fetchSummary } from "api";
import LoadingSpinner from "components/LoadingSpinner";
import { SummaryView } from "components/SummaryView";
import { router, useLocalSearchParams } from "expo-router";
import React from "react";
import { Text, View } from "react-native";

export default function SummaryReaderPage() {
  const { url } = useLocalSearchParams<{ url?: string }>();
  React.useEffect(() => {
    if (!url) router.replace("/");
  }, [url]);

  const { data, error, isLoading } = useQuery({
    queryKey: ["summary", url],
    queryFn: () => fetchSummary(url!),
    staleTime: Infinity,
    enabled: !!url,
  });

  const title = data ? (data.summary.match(/^# (.+)$/m)?.[1] ?? null) : null;
  const content = data ? data.summary.replace(/^# (.+)$/m, "") : null;

  return (
    <View className="h-full p-0">
      {isLoading && <LoadingSpinner />}
      {error && (
        <View className="flex-1 items-center justify-center">
          <Text className="text-red-500">{error.message}</Text>
        </View>
      )}
      {url && title && content && (
        <SummaryView
          title={title}
          markdown={content}
          sourceUrl={url}
        />
      )}
    </View>
  )
}
