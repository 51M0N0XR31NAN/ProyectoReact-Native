import { PlatformPressable } from 'expo-router/react-navigation';
import * as Haptics from 'expo-haptics';

// El tipo público de `BottomTabBarButtonProps` que espera `Tabs` vive en una
// ruta interna de expo-router (no exportada); se tipa como `any` en vez de
// depender de esa ruta interna, ya que este wrapper solo reenvía las props.
export function HapticTab(props: any) {
  return (
    <PlatformPressable
      {...props}
      onPressIn={(ev) => {
        if (process.env.EXPO_OS === 'ios') {
          // Add a soft haptic feedback when pressing down on the tabs.
          Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
        }
        props.onPressIn?.(ev);
      }}
    />
  );
}
