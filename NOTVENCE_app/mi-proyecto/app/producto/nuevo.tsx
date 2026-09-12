import { useRouter } from 'expo-router';
import React from 'react';
import { StyleSheet, Text, View } from 'react-native';

import { ProductoForm } from '@/components/producto-form';
import { crearProducto } from '@/services/productos';
import type { ProductoInput } from '@/services/productos';

export default function NuevoProductoScreen() {
  const router = useRouter();

  const handleSubmit = async (datos: ProductoInput) => {
    const producto = await crearProducto(datos);
    router.replace({ pathname: '/producto/[codigo]', params: { codigo: producto.codigo } });
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Nuevo producto</Text>
      <ProductoForm onSubmit={handleSubmit} textoBoton="Guardar producto" />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#f8f9fa' },
  title: { fontSize: 20, fontWeight: 'bold', padding: 16, paddingBottom: 0, color: '#2c3e50' },
});
