import { apiFetch } from '@/services/api';
import type { Producto } from '@/types/models';

export interface ProductoInput {
  nombre: string;
  categoria: string;
  presentacion: string;
  cantidad: number;
  ubicacion: string;
  vence: string | null;
}

export function listarProductos() {
  return apiFetch<Producto[]>('/api/productos');
}

export function listarAlertas() {
  return apiFetch<Producto[]>('/api/alertas');
}

export function obtenerProducto(codigo: string) {
  return apiFetch<Producto>(`/api/productos/${codigo}`);
}

export function crearProducto(datos: ProductoInput) {
  return apiFetch<Producto>('/api/productos', {
    method: 'POST',
    body: JSON.stringify(datos),
  });
}

export function actualizarProducto(codigo: string, datos: ProductoInput) {
  return apiFetch<Producto>(`/api/productos/${codigo}`, {
    method: 'PUT',
    body: JSON.stringify(datos),
  });
}

export function eliminarProducto(codigo: string) {
  return apiFetch<void>(`/api/productos/${codigo}`, { method: 'DELETE' });
}

export function listarCategorias() {
  return apiFetch<{ categorias: string[] }>('/api/categorias');
}

export function listarPresentaciones(categoria: string) {
  return apiFetch<{ categoria: string; presentaciones: string[] }>(
    `/api/categorias/${encodeURIComponent(categoria)}/presentaciones`
  );
}
