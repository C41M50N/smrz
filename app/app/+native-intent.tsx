import { getShareExtensionKey, parseShareIntent } from "expo-share-intent";

export function redirectSystemPath({
  path,
  initial,
}: {
  path: string;
  initial: string;
}) {
  try {
    if (path.includes(`dataUrl=${getShareExtensionKey()}`)) {
      // redirect to the ShareIntent Screen to handle data with the hook
      console.debug(
        "[expo-router-native-intent] redirect to ShareIntent screen",
      );
      const intent = parseShareIntent(path, {});
      console.debug(
        "[expo-router-native-intent] ShareIntent data",
        JSON.stringify(intent),
        intent.webUrl,
      );
      return "/shareintent";
    }
    return path;
  } catch {
    return "/";
  }
}
