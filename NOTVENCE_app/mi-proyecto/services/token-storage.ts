import { Platform } from 'react-native';
import * as SecureStore from 'expo-secure-store';

// expo-secure-store no tiene implementación en web (su módulo web es un objeto
// vacío). En web usamos localStorage; en iOS/Android, el almacenamiento seguro.
const isWeb = Platform.OS === 'web';

export async function getToken(key: string): Promise<string | null> {
  if (isWeb) {
    try {
      return localStorage.getItem(key);
    } catch {
      return null;
    }
  }
  return SecureStore.getItemAsync(key);
}

export async function setToken(key: string, value: string): Promise<void> {
  if (isWeb) {
    try {
      localStorage.setItem(key, value);
    } catch {
      // Almacenamiento no disponible (modo privado, etc.); la sesión no persiste.
    }
    return;
  }
  await SecureStore.setItemAsync(key, value);
}

export async function deleteToken(key: string): Promise<void> {
  if (isWeb) {
    try {
      localStorage.removeItem(key);
    } catch {
      // Ignorar: nada que borrar si no está disponible.
    }
    return;
  }
  await SecureStore.deleteItemAsync(key);
}
