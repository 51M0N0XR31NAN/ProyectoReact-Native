import { Picker } from '@react-native-picker/picker';
import React, { useEffect, useState } from 'react';
import {
  ActivityIndicator,
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  TouchableOpacity,
  View,
} from 'react-native';

import { ApiError } from '@/services/api';
import { listarCategorias, listarPresentaciones } from '@/services/productos';
import type { ProductoInput } from '@/services/productos';
import type { Producto } from '@/types/models';

interface ProductoFormProps {
  inicial?: Producto;
  onSubmit: (datos: ProductoInput) => Promise<void>;
  textoBoton: string;
}

export function ProductoForm({ inicial, onSubmit, textoBoton }: ProductoFormProps) {
  const [categorias, setCategorias] = useState<string[]>([]);
  const [presentaciones, setPresentaciones] = useState<string[]>([]);
  const [cargandoCategorias, setCargandoCategorias] = useState(true);

  const [nombre, setNombre] = useState(inicial?.nombre ?? '');
  const [categoria, setCategoria] = useState(inicial?.categoria ?? '');
  const [presentacion, setPresentacion] = useState(inicial?.presentacion ?? '');
  const [cantidad, setCantidad] = useState(inicial ? String(inicial.cantidad) : '');
  const [ubicacion, setUbicacion] = useState(inicial?.ubicacion ?? '');
  const [vence, setVence] = useState(inicial && inicial.vence !== 'Sin fecha' ? inicial.vence : '');
  const [enviando, setEnviando] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    (async () => {
      try {
        const { categorias: lista } = await listarCategorias();
        setCategorias(lista);
        setCategoria((actual) => actual || lista[0] || '');
      } catch {
        setError('No se pudieron cargar las categorías.');
      } finally {
        setCargandoCategorias(false);
      }
    })();
  }, []);

  useEffect(() => {
    if (!categoria) {
      return;
    }
    let activo = true;
    listarPresentaciones(categoria)
      .then(({ presentaciones: lista }) => {
        if (!activo) return;
        setPresentaciones(lista);
        setPresentacion((actual) => (lista.includes(actual) ? actual : lista[0] ?? ''));
      })
      .catch(() => {
        if (activo) setPresentaciones([]);
      });
    return () => {
      activo = false;
    };
  }, [categoria]);

  const handleSubmit = async () => {
    if (!nombre.trim() || !categoria || !presentacion || !ubicacion.trim()) {
      setError('Completa nombre, categoría, presentación y ubicación.');
      return;
    }
    const cantidadNum = Number(cantidad);
    if (!Number.isFinite(cantidadNum) || cantidadNum < 0) {
      setError('La cantidad debe ser un número válido mayor o igual a 0.');
      return;
    }
    if (vence.trim() && !/^\d{4}-\d{2}-\d{2}$/.test(vence.trim())) {
      setError('La fecha de vencimiento debe tener el formato AAAA-MM-DD.');
      return;
    }

    setError(null);
    setEnviando(true);
    try {
      await onSubmit({
        nombre: nombre.trim(),
        categoria,
        presentacion,
        cantidad: cantidadNum,
        ubicacion: ubicacion.trim(),
        vence: vence.trim() || null,
      });
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'No se pudo guardar el producto.');
    } finally {
      setEnviando(false);
    }
  };

  if (cargandoCategorias) {
    return (
      <View style={styles.center}>
        <ActivityIndicator size="large" color="#007bff" />
      </View>
    );
  }

  return (
    <ScrollView contentContainerStyle={styles.container} keyboardShouldPersistTaps="handled">
      {error && <Text style={styles.error}>{error}</Text>}

      <Text style={styles.label}>Nombre</Text>
      <TextInput style={styles.input} value={nombre} onChangeText={setNombre} editable={!enviando} />

      <Text style={styles.label}>Categoría</Text>
      <View style={styles.pickerWrapper}>
        <Picker selectedValue={categoria} onValueChange={setCategoria} enabled={!enviando}>
          {categorias.map((c) => (
            <Picker.Item key={c} label={c} value={c} />
          ))}
        </Picker>
      </View>

      <Text style={styles.label}>Presentación</Text>
      <View style={styles.pickerWrapper}>
        <Picker selectedValue={presentacion} onValueChange={setPresentacion} enabled={!enviando}>
          {(categoria ? presentaciones : []).map((p) => (
            <Picker.Item key={p} label={p} value={p} />
          ))}
        </Picker>
      </View>

      <Text style={styles.label}>Cantidad</Text>
      <TextInput
        style={styles.input}
        value={cantidad}
        onChangeText={setCantidad}
        keyboardType="numeric"
        editable={!enviando}
      />

      <Text style={styles.label}>Ubicación</Text>
      <TextInput style={styles.input} value={ubicacion} onChangeText={setUbicacion} editable={!enviando} />

      <Text style={styles.label}>Vence (AAAA-MM-DD, opcional)</Text>
      <TextInput
        style={styles.input}
        value={vence}
        onChangeText={setVence}
        placeholder="2026-12-31"
        editable={!enviando}
      />

      <TouchableOpacity style={styles.button} onPress={handleSubmit} disabled={enviando}>
        {enviando ? <ActivityIndicator color="#fff" /> : <Text style={styles.buttonText}>{textoBoton}</Text>}
      </TouchableOpacity>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { padding: 16 },
  center: { flex: 1, justifyContent: 'center', alignItems: 'center' },
  error: { color: '#e74c3c', marginBottom: 12 },
  label: { fontSize: 14, fontWeight: '600', color: '#333', marginBottom: 6, marginTop: 12 },
  input: { backgroundColor: '#fff', padding: 12, borderRadius: 8, borderWidth: 1, borderColor: '#ddd' },
  pickerWrapper: { backgroundColor: '#fff', borderRadius: 8, borderWidth: 1, borderColor: '#ddd' },
  button: {
    backgroundColor: '#007bff',
    padding: 16,
    borderRadius: 8,
    alignItems: 'center',
    marginTop: 24,
    marginBottom: 40,
  },
  buttonText: { color: '#fff', fontSize: 16, fontWeight: 'bold' },
});
