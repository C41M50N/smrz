import { Button, Image, Text, View } from "react-native";
import { useRouter } from "expo-router";
import {
  ShareIntent as ShareIntentType,
  useShareIntentContext,
} from "expo-share-intent";

const WebUrlComponent = ({ shareIntent }: { shareIntent: ShareIntentType }) => {
  return (
    <View className="flex-row items-center border border-gray-300 rounded-lg h-[102px] mb-5 gap-2.5 px-2.5">
      <Image
        source={
          shareIntent.meta?.["og:image"]
            ? { uri: shareIntent.meta?.["og:image"] }
            : undefined
        }
        className="w-24 h-24 rounded-lg bg-gray-200 mr-2.5"
      />
      <View className="flex-shrink px-1.5">
        <Text className="mb-5">{shareIntent.meta?.title || "<NO TITLE>"}</Text>
        <Text className="mb-5">{shareIntent.webUrl}</Text>
      </View>
    </View>
  );
};

export default function ShareIntent() {
  const router = useRouter();
  const { hasShareIntent, shareIntent, error, resetShareIntent } =
    useShareIntentContext();

  return (
    <View className="flex-1 bg-white items-center justify-center px-2.5">
      <Image
        source={require("../assets/icon.png")}
        className="w-[75px] h-[75px] mb-5"
        style={{ resizeMode: "contain" }}
      />
      {!hasShareIntent && <Text>No Share intent detected</Text>}
      {hasShareIntent && (
        <Text className="mb-5 text-xl">
          Congratz, a share intent value is available
        </Text>
      )}
      {!!shareIntent.text && <Text className="mb-5">{shareIntent.text}</Text>}
      {shareIntent?.type === "weburl" && (
        <WebUrlComponent shareIntent={shareIntent} />
      )}
      {shareIntent?.files?.map((file) => (
        <Image
          key={file.path}
          source={{ uri: file.path }}
          className="w-[200px] h-[200px] mb-5"
          style={{ resizeMode: "contain" }}
        />
      ))}
      {hasShareIntent && (
        <Button onPress={() => resetShareIntent()} title="Reset" />
      )}
      <Text className="text-red-500">{error}</Text>
      <Button onPress={() => router.replace("/")} title="Go home" />
    </View>
  );
}
