import React, { useState } from 'react';
import { View, Text, TouchableOpacity, SafeAreaView } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { cn } from 'utils';

export interface Tab {
  id: string;
  label: string;
  icon: keyof typeof Ionicons.glyphMap;
  content: React.ReactNode;
}

export interface TabsProps {
  tabs: Tab[];
  defaultTab?: string;
  onTabChange?: (tabId: string) => void;
}

export function Tabs({ tabs, defaultTab, onTabChange }: TabsProps) {
  const [activeTab, setActiveTab] = useState(defaultTab || tabs[0]?.id);
  const insets = useSafeAreaInsets();

  const handleTabPress = (tabId: string) => {
    setActiveTab(tabId);
    onTabChange?.(tabId);
  };

  const activeTabContent = tabs.find(tab => tab.id === activeTab)?.content;

  return (
    <View className="flex-1 bg-white">
      {/* Content Area */}
      <SafeAreaView className="-mt-2 -mb-4 flex-1">
        {activeTabContent}
      </SafeAreaView>

      {/* Bottom Tab Bar - extends to device bottom */}
      <View className="bg-gray-100 border-t border-gray-200" style={{ paddingBottom: insets.bottom }}>
        <View className="flex-row">
          {tabs.map((tab) => {
            const isActive = activeTab === tab.id;

            return (
              <TouchableOpacity
                key={tab.id}
                onPress={() => handleTabPress(tab.id)}
                className="flex-1 items-center justify-center pt-4 pb-2 px-1"
                activeOpacity={0.7}
              >
                <Ionicons
                  name={tab.icon}
                  size={22}
                  color={isActive ? 'black' : 'gray'}
                />
                <Text
                  className={`text-xs mt-1 text-center ${isActive ? 'text-gray-800 font-medium' : 'text-gray-500'
                    }`}
                >
                  {tab.label}
                </Text>
              </TouchableOpacity>
            );
          })}
        </View>
      </View>
    </View>
  );
}