import { View } from "react-native";
import AntDesign from '@expo/vector-icons/AntDesign';
import { cn } from "utils";

type LoadingSpinnerProps = {
  className?: string;
};

export default function LoadingSpinner({ className }: LoadingSpinnerProps) {
  return (
    <View className={cn("flex-1 items-center justify-center", className)}>
      <AntDesign name="loading1" size={20} color="black" className="animate-spin" />
    </View>
  )
}
