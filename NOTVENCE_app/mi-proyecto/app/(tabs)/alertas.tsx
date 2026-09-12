import React, { useCallback, useState } from 'react';
import { ActivityIndicator, FlatList, RefreshControl, StyleSheet, Text, View } from 'react-native';
import { useFocusEffect } from 'expo-router';

import { ApiError } from '@/services/api';
import { listarAlertas } from '@/services/productos';
import type { Producto } from '@/types/models';

const COLOR_ESTADO: Record<Producto['estado_clase'], string> = {
  success: '#27ae60',
  warning: '#e67e22',
  danger: '#e74c3c',
};

export default function AlertasScreen() {
  const [alertas, setAlertas] = useState<Producto[]>([]);
  const [cargando, setCargando] = useState(true);
  const [refrescando, setRefrescando] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const cargarAlertas = useCallback(async () => {
    try {
      const data = await listarAlertas();
      setAlertas(data);
      setError(null);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Error al cargar las alertas');
    } finally {
      setCargando(false);
      setRefrescando(false);
    }
  }, []);

  useFocusEffect(
    useCallback(() => {
      cargarAlertas();
    }, [cargarAlertas])
  );

  const handleRefresh = () => {
    setRefrescando(true);
    cargarAlertas();
  };

  if (cargando) {
    return (
      <View style={styles.center}>
        <ActivityIndicator size="large" color="#e74c3c" />
        <Text style={styles.loadingText}>Cargando alertas de vencimiento...</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      {error && <Text style={styles.error}>{error}</Text>}

      {!error && alertas.length === 0 ? (
        <View style={styles.center}>
          <Text style={styles.emptyText}>¡No hay productos con alertas activas!</Text>
        </View>
      ) : (
        <FlatList
          data={alertas}
          keyExtractor={(item) => item.codigo}
          refreshControl={<RefreshControl refreshing={refrescando} onRefresh={handleRefresh} />}
          renderItem={({ item }) => (
            <View style={[styles.card, { borderLeftColor: COLOR_ESTADO[item.estado_clase] }]}>
              <View style={styles.cardHeader}>
                <Text style={styles.nombre}>{item.nombre}</Text>
                <View style={[styles.badge, { backgroundColor: COLOR_ESTADO[item.estado_clase] }]}>
                  <Text style={styles.badgeText}>{item.estado}</Text>
                </View>
              </View>
              <Text style={styles.subtext}>
                Cantidad disponible: {item.cantidad} {item.presentacion}
              </Text>
              <Text style={styles.vencimiento}>Fecha de vencimiento: {item.vence}</Text>
            </View>
          )}
        />
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: 16, backgroundColor: '#f8f9fa' },
  center: { flex: 1, justifyContent: 'center', alignItems: 'center' },
  loadingText: { marginTop: 12, color: '#666' },
  error: { color: '#e74c3c', marginBottom: 12 },
  emptyText: { fontSize: 16, color: '#27ae60', fontWeight: 'bold' },
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
    marginBottom: 6,
  },
  nombre: { fontSize: 18, fontWeight: 'bold', color: '#2c3e50' },
  badge: { paddingHorizontal: 8, paddingVertical: 4, borderRadius: 4 },
  badgeText: { color: '#fff', fontSize: 12, fontWeight: 'bold' },
  subtext: { color: '#555', marginTop: 2 },
  vencimiento: { color: '#c0392b', fontWeight: '600', marginTop: 4 },
});
