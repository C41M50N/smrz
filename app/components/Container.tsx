import { SafeAreaView } from 'react-native';
import { cn } from 'utils';

export const Container = ({ children, className = "" }: { children: React.ReactNode, className?: string }) => {
  return <SafeAreaView className={cn('flex flex-1 m-6', className)}>{children}</SafeAreaView>;
};
