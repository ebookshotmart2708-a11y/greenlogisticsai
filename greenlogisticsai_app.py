
import streamlit as st
import google.generativeai as genai
from PIL import Image
import json
import io

# Configurar la página
st.set_page_config(page_title="GreenLogisticsAI", page_icon="🚚", layout="wide")
st.title("🚚 GreenLogisticsAI")
st.markdown("### Optimización Inteligente de Rutas con IA")

# Sidebar para configuración
with st.sidebar:
    st.header("🔧 Configuración")
    api_key = st.text_input("Introduce tu API Key de Gemini:", type="password")
    if api_key:
        genai.configure(api_key=api_key)
        st.success("✅ API Key configurada")
    else:
        st.warning("⚠️ Necesitas una API Key para continuar")

# Cargar las funciones del backend (que deberías tener en otro archivo)
# Por ahora, las incluimos directamente
from tu_backend import analyze_logistics_document, recommend_shipment_route

# Interfaz principal
tab1, tab2 = st.tabs(["📤 Analizar Documento", "ℹ️ Cómo Funciona"])

with tab1:
    st.subheader("Sube tu Documento de Embarque")
    uploaded_file = st.file_uploader("Elige una imagen o PDF", type=["png", "jpg", "jpeg", "pdf"])

    if uploaded_file is not None:
        # Mostrar vista previa
        if uploaded_file.type.startswith('image'):
            st.image(uploaded_file, caption="Vista previa del documento", width=300)
        else:
            st.info(f"📄 PDF subido: {uploaded_file.name}")

        # Botón para analizar
        if st.button("🔍 Analizar con IA", type="primary"):
            if not api_key:
                st.error("Por favor, introduce tu API Key en la barra lateral.")
            else:
                with st.spinner("La IA está analizando tu documento..."):
                    # 1. Extraer datos del documento
                    datos_extraidos = analyze_logistics_document(uploaded_file)
                    try:
                        datos_json = json.loads(datos_extraidos)
                        st.success("✅ Datos extraídos correctamente")

                        # Mostrar datos extraídos
                        with st.expander("📋 Ver datos extraídos por la IA"):
                            st.json(datos_json)

                        # 2. Generar recomendación
                        with st.spinner("Calculando la mejor ruta..."):
                            recomendacion = recommend_shipment_route(datos_json)
                            rec_json = json.loads(recomendacion)

                        # Mostrar resultados de forma atractiva
                        st.subheader("📊 Análisis Comparativo de Rutas")

                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown("### 🚛 Opción Terrestre")
                            opcion = rec_json["analisis"]["opcion_terrestre"]
                            st.metric("Coste", f"€{opcion['coste_eur']}")
                            st.metric("Tiempo", f"{opcion['tiempo_horas']} h")
                            st.metric("CO₂", f"{opcion['co2_kg']} kg")
                            st.markdown("**Ventajas:**")
                            for v in opcion["ventajas"]:
                                st.markdown(f"- {v}")

                        with col2:
                            st.markdown("### 🚂 Opción Intermodal")
                            opcion = rec_json["analisis"]["opcion_intermodal"]
                            st.metric("Coste", f"€{opcion['coste_eur']}")
                            st.metric("Tiempo", f"{opcion['tiempo_horas']} h")
                            st.metric("CO₂", f"{opcion['co2_kg']} kg")
                            st.markdown("**Ventajas:**")
                            for v in opcion["ventajas"]:
                                st.markdown(f"- {v}")

                        # Recomendación final
                        st.info(f"**💡 Recomendación de la IA:** {rec_json['analisis']['recomendacion']}")

                        # Botón para descargar reporte
                        reporte = {
                            "datos_extraidos": datos_json,
                            "analisis_rutas": rec_json["analisis"]
                        }
                        st.download_button(
                            label="📥 Descargar Reporte Completo (JSON)",
                            data=json.dumps(reporte, indent=2, ensure_ascii=False),
                            file_name="analisis_greenlogisticsai.json",
                            mime="application/json"
                        )

                    except json.JSONDecodeError as e:
                        st.error(f"Error al procesar la respuesta de la IA: {e}")
                        st.text(datos_extraidos)

with tab2:
    st.markdown("""
    ## 🎯 Cómo funciona GreenLogisticsAI

    1. **Sube tu documento** de embarque (factura, packing list, etc.)
    2. **Nuestra IA analiza** el documento y extrae automáticamente:
       - Origen y destino
       - Peso y tipo de mercancía
       - Términos de envío
    3. **Compara automáticamente** dos opciones:
       - **Transporte terrestre** (más rápido)
       - **Opción intermodal** (más sostenible)
    4. **Recibe recomendaciones** basadas en:
       - Coste estimado
       - Tiempo de tránsito
       - Huella de carbono

    ## 🔑 Requisitos
    - Necesitas una **API Key gratuita** de [Google AI Studio](https://aistudio.google.com/apikey)
    - La IA funciona con **imágenes (PNG, JPG) y PDFs**
    - Las estimaciones son aproximadas para **rutas dentro de Europa**

    ## 🚀 Próximas Funcionalidades
    - Integración con APIs de transporte reales
    - Cálculos de carbono más precisos
    - Historial de análisis
    - Opciones multi-modales personalizadas
    """)

# Pie de página
st.markdown("---")
st.markdown("🌱 *GreenLogisticsAI - Logística Inteligente y Sostenible*")
