import { Pressable } from "react-native";
import { cn } from "utils";
import LoadingSpinner from "./LoadingSpinner";

type ButtonProps = {
  onPress: () => void;
  disabled?: boolean;
  loading?: boolean;
  className?: string;
  children: React.ReactNode;
}

export function Button({ onPress, disabled, loading, className, children }: ButtonProps) {
  return (
    <Pressable
      onPress={onPress}
      disabled={disabled || loading}
      className={cn(
        "bg-blue-500 rounded-lg px-4 py-2 flex items-center justify-center",
        disabled && "bg-gray-300",
        loading && "bg-gray-400",
        className
      )}
    >
      {children}{loading && <LoadingSpinner className="absolute right-2" />}
    </Pressable>
  );
}
