import { useFocusEffect, useLocalSearchParams, useRouter } from 'expo-router';
import React, { useCallback, useState } from 'react';
import { ActivityIndicator, Alert, StyleSheet, Text, TouchableOpacity, View } from 'react-native';

import { ApiError } from '@/services/api';
import { eliminarProducto, obtenerProducto } from '@/services/productos';
import type { Producto } from '@/types/models';

const COLOR_ESTADO: Record<Producto['estado_clase'], string> = {
  success: '#27ae60',
  warning: '#e67e22',
  danger: '#e74c3c',
};

export default function DetalleProductoScreen() {
  const { codigo } = useLocalSearchParams<{ codigo: string }>();
  const router = useRouter();
  const [producto, setProducto] = useState<Producto | null>(null);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useFocusEffect(
    useCallback(() => {
      let activo = true;
      setCargando(true);
      obtenerProducto(codigo)
        .then((data) => {
          if (activo) setProducto(data);
        })
        .catch((err) => {
          if (activo) setError(err instanceof ApiError ? err.message : 'No se pudo cargar el producto');
        })
        .finally(() => {
          if (activo) setCargando(false);
        });
      return () => {
        activo = false;
      };
    }, [codigo])
  );

  const handleEliminar = () => {
    Alert.alert('Eliminar producto', '¿Seguro que quieres eliminar este producto?', [
      { text: 'Cancelar', style: 'cancel' },
      {
        text: 'Eliminar',
        style: 'destructive',
        onPress: async () => {
          try {
            await eliminarProducto(codigo);
            router.replace('/(tabs)');
          } catch (err) {
            Alert.alert('Error', err instanceof ApiError ? err.message : 'No se pudo eliminar el producto');
          }
        },
      },
    ]);
  };

  if (cargando) {
    return (
      <View style={styles.center}>
        <ActivityIndicator size="large" color="#007bff" />
      </View>
    );
  }

  if (error || !producto) {
    return (
      <View style={styles.center}>
        <Text style={styles.error}>{error ?? 'Producto no encontrado'}</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <View style={[styles.card, { borderLeftColor: COLOR_ESTADO[producto.estado_clase] }]}>
        <View style={styles.cardHeader}>
          <Text style={styles.nombre}>{producto.nombre}</Text>
          <Text style={[styles.estado, { color: COLOR_ESTADO[producto.estado_clase] }]}>{producto.estado}</Text>
        </View>
        <Text style={styles.dato}>Código: {producto.codigo}</Text>
        <Text style={styles.dato}>Categoría: {producto.categoria}</Text>
        <Text style={styles.dato}>
          Cantidad: {producto.cantidad} {producto.presentacion}
        </Text>
        <Text style={styles.dato}>Ubicación: {producto.ubicacion}</Text>
        <Text style={styles.dato}>Vence: {producto.vence}</Text>
      </View>

      <TouchableOpacity
        style={styles.botonEditar}
        onPress={() => router.push({ pathname: '/producto/[codigo]/editar', params: { codigo: producto.codigo } })}
      >
        <Text style={styles.botonTexto}>Editar</Text>
      </TouchableOpacity>

      <TouchableOpacity style={styles.botonEliminar} onPress={handleEliminar}>
        <Text style={styles.botonTexto}>Eliminar</Text>
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: 16, backgroundColor: '#f8f9fa' },
  center: { flex: 1, justifyContent: 'center', alignItems: 'center', backgroundColor: '#f8f9fa' },
  error: { color: '#e74c3c', fontSize: 16 },
  card: { backgroundColor: '#fff', padding: 20, borderRadius: 8, borderLeftWidth: 6, elevation: 2 },
  cardHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 },
  nombre: { fontSize: 22, fontWeight: 'bold', color: '#2c3e50' },
  estado: { fontSize: 13, fontWeight: 'bold' },
  dato: { fontSize: 15, color: '#555', marginTop: 6 },
  botonEditar: {
    backgroundColor: '#007bff',
    padding: 16,
    borderRadius: 8,
    alignItems: 'center',
    marginTop: 20,
  },
  botonEliminar: {
    backgroundColor: '#e74c3c',
    padding: 16,
    borderRadius: 8,
    alignItems: 'center',
    marginTop: 12,
  },
  botonTexto: { color: '#fff', fontSize: 16, fontWeight: 'bold' },
});
