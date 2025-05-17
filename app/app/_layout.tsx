import '../global.css';
import { Slot, useRouter } from "expo-router";
import { ShareIntentProvider } from "expo-share-intent";
import { StatusBar } from 'expo-status-bar';

export default function Layout() {
  const router = useRouter();

  return (
    <ShareIntentProvider
      options={{
        debug: true,
        resetOnBackground: true,
        onResetShareIntent: () =>
          // used when app going in background and when the reset button is pressed
          router.replace({
            pathname: "/",
          }),
      }}
    >
      <Slot />
      <StatusBar style="auto" />
    </ShareIntentProvider>
  );
}