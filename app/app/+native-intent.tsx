import { getShareExtensionKey } from "expo-share-intent";

export function redirectSystemPath({
  path,
  initial,
}: {
  path: string;
  initial: string;
}) {
  try {
    if (path.includes(`dataUrl=${getShareExtensionKey()}`)) {
      console.debug(
        "[expo-router-native-intent] redirect to shareintent screen",
      );
      return "/summary-reader-intent";
    }
    return path;
  } catch {
    return "/";
  }
}
