import { View } from "react-native";
import Markdown from "react-native-marked";

type MarkdownViewerProps = {
  markdown: string;
};

// comments in the return statement breaks RN.... wtf
// https://github.com/gmsgowtham/react-native-marked/blob/main/src/theme/types.ts
// li fontSize = size of bullet points
// font-reader does not work yet

export function MarkdownViewer({ markdown }: MarkdownViewerProps) {
  return (
    <View className="font-reader">
      <Markdown
        value={markdown}
        styles={{
          text: { color: "black", fontSize: 14, lineHeight: 20, fontFamily: "Exile" },
          paragraph: { paddingTop: 2, paddingBottom: 8 },
          h1: { borderBottomWidth: 0 },
          h2: { fontSize: 20, paddingTop: 6, paddingBottom: 2, borderBottomWidth: 0, lineHeight: 28 },
          h3: { fontSize: 16, paddingTop: 6, paddingBottom: 2, lineHeight: 24 },
          list: { marginLeft: -6 },
          li: { fontSize: 20, lineHeight: 20, paddingTop: 2.5, paddingBottom: 2.5 },
        }}
        theme={{ spacing: { xs: 0, s: 0, m: 0, l: 0 } }}
      />
    </View>
  );
}
