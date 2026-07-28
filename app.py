import json
import streamlit as st
from google import genai


# Lee la API Key desde los Secrets de Streamlit (nube) o usa un valor local
if "GEMINI_API_KEY" in st.secrets:
    API_KEY = st.secrets["GEMINI_API_KEY"]
else:
    API_KEY = ""

client = genai.Client(api_key=API_KEY)

# 2. Configuración de la página web (Modo ancho para pantalla completa)
st.set_page_config(
    page_title="Customer Pulse AI | Dashboard", page_icon="⚡", layout="wide"
)

# Encabezado con estilo
st.title("⚡ Customer Pulse AI")
st.caption(
    "Sistema Inteligente de Clasificación, Diagnóstico y Respuesta de Feedback de Clientes"
)
st.divider()

# 3. Entrada de usuario
texto_cliente = st.text_area(
    "📝 Reclamo, correo o reseña del cliente:",
    height=140,
    placeholder="Ejemplo: Llevo 3 días esperando mi paquete. La atención telefónica fue pésima y nadie me da respuesta. Exijo la devolución de mi dinero ya mismo...",
)

# Botón de acción ancho
if st.button("🚀 Analizar e Interpretar Feedback", type="primary", use_container_width=True):
    if not texto_cliente.strip():
        st.warning("⚠️ Por favor, ingresá un texto antes de presionar el botón.")
    else:
        with st.spinner("La IA está diagnosticando el mensaje y generando la respuesta... ⏳"):
            try:
                # Prompt estructurado pidiendo JSON estricto
                prompt = f"""
                Analiza el siguiente mensaje de cliente y responde ÚNICAMENTE en formato JSON válido con esta estructura:
                {{
                    "sentimiento": "opciones: Muy Negativo, Negativo, Neutro, o Positivo",
                    "urgencia": "opciones: Alta, Media, o Baja",
                    "puntos_clave": ["punto 1", "punto 2", "punto 3"],
                    "respuesta_sugerida": "borrador de respuesta profesional, empática y orientada a la solución"
                }}

                Texto del cliente:
                {texto_cliente}
                """

                # Forzamos a la API a responder en formato JSON
                respuesta = client.models.generate_content(
                    model="gemini-flash-latest",
                    contents=prompt,
                    config={"response_mime_type": "application/json"},
                )

                # Convertimos la respuesta de texto JSON a un Diccionario de Python
                datos = json.loads(respuesta.text)

                st.success("¡Análisis completado con éxito!")
                st.divider()

                # --- DASHBOARD DE RESULTADOS VISUALES ---
                
                # Fila 1: Tarjetas de Estado (Métricas)
                col_sentimiento, col_urgencia = st.columns(2)

                sentimiento = datos.get("sentimiento", "Neutro")
                urgencia = datos.get("urgencia", "Media")

                with col_sentimiento:
                    if "Negativo" in sentimiento:
                        st.error(f"🔻 **Sentimiento:** {sentimiento}")
                    elif "Positivo" in sentimiento:
                        st.success(f"🟢 **Sentimiento:** {sentimiento}")
                    else:
                        st.info(f"⚪ **Sentimiento:** {sentimiento}")

                with col_urgencia:
                    if urgencia == "Alta":
                        st.warning(f"🔥 **Nivel de Urgencia:** {urgencia}")
                    else:
                        st.info(f"🟢 **Nivel de Urgencia:** {urgencia}")

                st.write("")  # Espacio visual

                # Fila 2: Columnas de Contenido
                col_izq, col_der = st.columns([1, 1])

                with col_izq:
                    st.subheader("📌 Puntos Clave Detectados")
                    puntos = datos.get("puntos_clave", [])
                    for p in puntos:
                        st.markdown(f"- {p}")

                with col_der:
                    st.subheader("✉️ Respuesta Sugerida")
                    # st.code permite que el usuario copie la respuesta con un solo clic
                    st.code(datos.get("respuesta_sugerida", ""), language="markdown")
                    st.caption("💡 Podés hacer clic arriba a la derecha del recuadro para copiar el texto.")

            except Exception as error:
                st.error(f"Ocurrió un problema al procesar los datos: {error}")