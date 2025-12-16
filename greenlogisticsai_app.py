
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
# ============================================================================
# 🔧 FUNCIONES DE BACKEND (Reemplazan 'tu_backend.py')
# ============================================================================
import json
from PIL import Image
import io
from pdf2image import convert_from_bytes

# Configura el modelo de Gemini (asegúrate de que 'genai' y 'model' estén configurados antes)
# Esta configuración debe estar en tu código principal, cerca del inicio.

def analyze_logistics_document(uploaded_file):
    """
    Esta función toma un archivo subido (imagen o PDF) y le pide a la IA que
    extraiga los datos clave para el análisis logístico.
    """
    try:
        # Leer el archivo
        if uploaded_file.type == "application/pdf":
            # Para PDFs, extraer la primera página como imagen
            images = convert_from_bytes(uploaded_file.read())
            img = images[0]
        else:
            # Para imágenes
            img = Image.open(io.BytesIO(uploaded_file.read()))

        # Preparar el prompt para la IA
        prompt = """
        Eres un experto en logística internacional y procesamiento de documentos de comercio exterior.
        Analiza el documento proporcionado y extrae SOLO los siguientes datos en formato JSON:

        {
          "origen": "ciudad y país de origen",
          "destino": "ciudad y país de destino",
          "peso_total_kg": peso en kilogramos,
          "descripcion_mercancia": breve descripción del producto",
          "incoterm": "término incoterm si es visible (ej: FOB, CIF, EXW)",
          "valor_mercancia_usd": valor declarado en dólares si está disponible
        }

        Si algún dato no está presente en el documento, usa "no_encontrado".
        Solo responde con el JSON, sin explicaciones adicionales.
        """

        # Generar la respuesta de la IA
        response = model.generate_content([prompt, img])
        return response.text

    except Exception as e:
        return f"Error al procesar el documento: {str(e)}"

def recommend_shipment_route(logistics_data):
    """
    Esta función toma los datos extraídos y genera una recomendación
    comparando opciones de transporte.
    """
    try:
        prompt = f"""
        Basándote en estos datos de envío:
        {logistics_data}

        Actúa como un experto en optimización de rutas europeas sostenibles.
        Compara DOS opciones para este envío dentro de Europa:

        1. **Opción Terrestre (Camión)**: La opción más rápida y directa.
        2. **Opción Intermodal (Tren + Camión)**: La opción más sostenible y potencialmente más económica para distancias largas.

        Para cada opción, proporciona estimaciones realistas para:
        - Coste aproximado (en EUR)
        - Tiempo de tránsito (en horas)
        - Huella de carbono aproximada (en kg de CO₂eq)

        Considera que:
        - El transporte por ferrocarril emite aproximadamente 1/4 del CO₂ del transporte por carretera.
        - La combinación intermodal puede añadir 12-24 horas por transbordo.

        Presenta tu respuesta en formato JSON claro:
        {{
          "analisis": {{
            "opcion_terrestre": {{
              "coste_eur": "valor",
              "tiempo_horas": "valor",
              "co2_kg": "valor",
              "ventajas": ["lista de ventajas"],
              "desventajas": ["lista de desventajas"]
            }},
            "opcion_intermodal": {{
              "coste_eur": "valor",
              "tiempo_horas": "valor",
              "co2_kg": "valor",
              "ventajas": ["lista de ventajas"],
              "desventajas": ["lista de desventajas"]
            }},
            "recomendacion": "explicación de cuál opción recomiendas y por qué"
          }}
        }}

        Solo responde con el JSON, sin explicaciones adicionales.
        """
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error al generar recomendación: {str(e)}"

# ============================================================================

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
