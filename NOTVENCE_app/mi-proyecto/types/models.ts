export type EstadoClase = 'success' | 'warning' | 'danger';

export interface Producto {
  codigo: string;
  nombre: string;
  categoria: string;
  presentacion: string;
  cantidad: number;
  ubicacion: string;
  vence: string;
  estado: string;
  estado_clase: EstadoClase;
}

export interface Usuario {
  username: string;
  id_casa: number;
}
