import React, { createContext, useContext, useEffect, useMemo, useState } from 'react';

import * as authService from '@/services/auth';
import { setAuthToken } from '@/services/api';
import { deleteToken, getToken, setToken } from '@/services/token-storage';
import type { Usuario } from '@/types/models';

const TOKEN_KEY = 'notvence_token';

interface AuthContextValue {
  user: Usuario | null;
  isLoading: boolean;
  login: (username: string, password: string) => Promise<void>;
  registro: (username: string, email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<Usuario | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    (async () => {
      try {
        const token = await getToken(TOKEN_KEY);
        if (token) {
          setAuthToken(token);
          const perfil = await authService.obtenerPerfil();
          setUser(perfil);
        }
      } catch {
        await deleteToken(TOKEN_KEY);
        setAuthToken(null);
      } finally {
        setIsLoading(false);
      }
    })();
  }, []);

  const guardarSesion = async (token: string) => {
    await setToken(TOKEN_KEY, token);
    setAuthToken(token);
    const perfil = await authService.obtenerPerfil();
    setUser(perfil);
  };

  const login = async (username: string, password: string) => {
    const { access_token } = await authService.login(username, password);
    await guardarSesion(access_token);
  };

  const registro = async (username: string, email: string, password: string) => {
    const { access_token } = await authService.registro(username, email, password);
    await guardarSesion(access_token);
  };

  const logout = async () => {
    await deleteToken(TOKEN_KEY);
    setAuthToken(null);
    setUser(null);
  };

  const value = useMemo(
    () => ({ user, isLoading, login, registro, logout }),
    [user, isLoading]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth debe usarse dentro de <AuthProvider>');
  }
  return context;
}
