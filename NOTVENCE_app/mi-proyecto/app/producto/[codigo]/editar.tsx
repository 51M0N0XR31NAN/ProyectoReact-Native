import { useFocusEffect, useLocalSearchParams, useRouter } from 'expo-router';
import React, { useCallback, useState } from 'react';
import { ActivityIndicator, StyleSheet, Text, View } from 'react-native';

import { ProductoForm } from '@/components/producto-form';
import { ApiError } from '@/services/api';
import { actualizarProducto, obtenerProducto } from '@/services/productos';
import type { ProductoInput } from '@/services/productos';
import type { Producto } from '@/types/models';

export default function EditarProductoScreen() {
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

  const handleSubmit = async (datos: ProductoInput) => {
    await actualizarProducto(codigo, datos);
    router.replace({ pathname: '/producto/[codigo]', params: { codigo } });
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
      <Text style={styles.title}>Editar producto</Text>
      <ProductoForm inicial={producto} onSubmit={handleSubmit} textoBoton="Guardar cambios" />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#f8f9fa' },
  center: { flex: 1, justifyContent: 'center', alignItems: 'center', backgroundColor: '#f8f9fa' },
  error: { color: '#e74c3c', fontSize: 16 },
  title: { fontSize: 20, fontWeight: 'bold', padding: 16, paddingBottom: 0, color: '#2c3e50' },
});
