import React, { useCallback, useState } from 'react';
import {
  ActivityIndicator,
  FlatList,
  RefreshControl,
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
} from 'react-native';
import { useFocusEffect, useRouter } from 'expo-router';

import { useAuth } from '@/context/auth-context';
import { ApiError } from '@/services/api';
import { listarProductos } from '@/services/productos';
import type { Producto } from '@/types/models';

const COLOR_ESTADO: Record<Producto['estado_clase'], string> = {
  success: '#27ae60',
  warning: '#e67e22',
  danger: '#e74c3c',
};

export default function InventarioScreen() {
  const { logout } = useAuth();
  const router = useRouter();
  const [productos, setProductos] = useState<Producto[]>([]);
  const [cargando, setCargando] = useState(true);
  const [refrescando, setRefrescando] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const cargarProductos = useCallback(async () => {
    try {
      const data = await listarProductos();
      setProductos(data);
      setError(null);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Error al cargar el inventario');
    } finally {
      setCargando(false);
      setRefrescando(false);
    }
  }, []);

  useFocusEffect(
    useCallback(() => {
      cargarProductos();
    }, [cargarProductos])
  );

  const handleRefresh = () => {
    setRefrescando(true);
    cargarProductos();
  };

  if (cargando) {
    return (
      <View style={styles.center}>
        <ActivityIndicator size="large" color="#007bff" />
        <Text style={styles.loadingText}>Cargando inventario...</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Inventario</Text>
        <TouchableOpacity onPress={logout}>
          <Text style={styles.logout}>Cerrar sesión</Text>
        </TouchableOpacity>
      </View>

      {error && <Text style={styles.error}>{error}</Text>}

      <TouchableOpacity style={styles.botonNuevo} onPress={() => router.push('/producto/nuevo')}>
        <Text style={styles.botonNuevoTexto}>+ Nuevo producto</Text>
      </TouchableOpacity>

      <FlatList
        data={productos}
        keyExtractor={(item) => item.codigo}
        refreshControl={<RefreshControl refreshing={refrescando} onRefresh={handleRefresh} />}
        ListEmptyComponent={
          !error ? <Text style={styles.emptyText}>No hay productos en el inventario todavía.</Text> : null
        }
        renderItem={({ item }) => (
          <TouchableOpacity
            style={[styles.card, { borderLeftColor: COLOR_ESTADO[item.estado_clase] }]}
            onPress={() => router.push({ pathname: '/producto/[codigo]', params: { codigo: item.codigo } })}
          >
            <View style={styles.cardHeader}>
              <Text style={styles.nombre}>{item.nombre}</Text>
              <Text style={[styles.estado, { color: COLOR_ESTADO[item.estado_clase] }]}>{item.estado}</Text>
            </View>
            <Text style={styles.subtext}>Código: {item.codigo}</Text>
            <Text style={styles.subtext}>
              Cantidad: {item.cantidad} {item.presentacion}
            </Text>
            <Text style={styles.subtext}>Ubicación: {item.ubicacion}</Text>
            <Text style={styles.subtext}>Vence: {item.vence}</Text>
          </TouchableOpacity>
        )}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: 16, backgroundColor: '#f8f9fa' },
  center: { flex: 1, justifyContent: 'center', alignItems: 'center' },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  headerTitle: { fontSize: 22, fontWeight: 'bold', color: '#2c3e50' },
  logout: { color: '#e74c3c', fontSize: 14, fontWeight: '600' },
  loadingText: { marginTop: 12, color: '#666' },
  error: { color: '#e74c3c', marginBottom: 12 },
  botonNuevo: {
    backgroundColor: '#007bff',
    padding: 12,
    borderRadius: 8,
    alignItems: 'center',
    marginBottom: 12,
  },
  botonNuevoTexto: { color: '#fff', fontWeight: 'bold' },
  emptyText: { textAlign: 'center', color: '#666', marginTop: 40 },
  card: {
    backgroundColor: '#fff',
    padding: 16,
    borderRadius: 8,
    marginBottom: 12,
    borderLeftWidth: 5,
    elevation: 2,
  },
  cardHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 4,
  },
  nombre: { fontSize: 18, fontWeight: 'bold', color: '#333' },
  estado: { fontSize: 12, fontWeight: 'bold' },
  subtext: { color: '#666', marginTop: 2 },
});
