import { Platform, Pressable, Share, Text, View } from "react-native";
import Markdown from "react-native-marked";
import Fontisto from '@expo/vector-icons/Fontisto';

type SummaryViewProps = {
  title: string;
  markdown: string;
  sourceUrl: string;
};

export function SummaryView({ title, markdown, sourceUrl }: SummaryViewProps) {
  return (
    <View className="pb-36">
      <View className="mb-5 flex flex-row items-center justify-between gap-2.5 border-b border-gray-300">
        <Text className="text-3xl font-semibold text-center mt-1 mb-2">
          {title}
        </Text>
        <Pressable
          className="items-center"
          accessibilityLabel="Share"
          onPress={() => {
            if (Platform.OS === "ios") {
              Share.share({ url: sourceUrl });
            } else {
              Share.share({ message: sourceUrl });
            }
          }}
        >
          <Fontisto name="share" size={16} color="black" />
        </Pressable>
      </View>
      <View className="font-reader"> {/* this doesn't work... */}
        <Markdown
          value={markdown}
          styles={{ // https://github.com/gmsgowtham/react-native-marked/blob/main/src/theme/types.ts
            text: { color: "black", fontSize: 14, lineHeight: 20, fontFamily: "Exile" },
            paragraph: { paddingTop: 2, paddingBottom: 8 },
            h3: { fontSize: 20, paddingTop: 6, paddingBottom: 0 },
            list: { marginLeft: -6 },
            li: { fontSize: 20, lineHeight: 20, paddingTop: 2.5, paddingBottom: 2.5 }, // fontSize = size of bullet points
          }}
          theme={{ spacing: { xs: 0, s: 0, m: 0, l: 0 } }}
        />
      </View>
    </View>
  );
}
