import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import '../global.css';
import { Slot, useRouter } from "expo-router";
import { ShareIntentProvider } from "expo-share-intent";
import { StatusBar } from 'expo-status-bar';

const queryClient = new QueryClient()

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
      <QueryClientProvider client={queryClient}>
        <Slot />
      </QueryClientProvider>
      <StatusBar style="auto" />
    </ShareIntentProvider>
  );
}