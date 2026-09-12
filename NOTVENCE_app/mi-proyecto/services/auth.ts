import { apiFetch } from '@/services/api';
import type { Usuario } from '@/types/models';

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

export function login(username: string, password: string) {
  return apiFetch<TokenResponse>('/api/auth/login', {
    method: 'POST',
    body: JSON.stringify({ username, password }),
  });
}

export function registro(username: string, email: string, password: string) {
  return apiFetch<TokenResponse>('/api/auth/registro', {
    method: 'POST',
    body: JSON.stringify({ username, email, password }),
  });
}

export function obtenerPerfil() {
  return apiFetch<Usuario>('/api/auth/me');
}
