import streamlit as st
from pptx import Presentation
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import os

st.title("🤖 ChatBot de Bioquímica – Aminoácidos")
st.write("Haz preguntas sobre aminoácidos y el chatbot responderá usando tus diapositivas y video de clase.")

# Ruta al archivo .pptx
pptx_path = "clase_001_aminoacidos.pptx"

# Enlace del video de YouTube
videos = {
    "clase_001_aminoacidos.pptx": "https://youtu.be/6-rvZqSTANo?si=WfT34ODacliTwOhz"
}

# Función para extraer texto de cada diapositiva
def extract_text_from_pptx(file_path):
    prs = Presentation(file_path)
    slides_text = []
    for slide in prs.slides:
        text = ""
        for shape in slide.shapes:
            if hasattr(shape, "text"):
                text += shape.text + " "
        slides_text.append(text.strip())
    return slides_text

# Cargar contenido
try:
    slides = extract_text_from_pptx(pptx_path)
except Exception as e:
    st.error(f"Error al leer el archivo: {e}")
    st.stop()

# Input del usuario
query = st.text_input("Pregunta sobre aminoácidos:")

if query:
    vectorizer = TfidfVectorizer().fit_transform([query] + slides)
    similarity = cosine_similarity(vectorizer[0:1], vectorizer[1:])
    best_idx = similarity.argmax()
    
    st.subheader("📖 Respuesta basada en tu clase:")
    st.write(slides[best_idx])

    # Mostrar el video si está disponible
   video_url = videos.get(pptx_path)
    if video_url:
        st.markdown("🎥 **Mira la explicación en video:**")
        st.video(video_url)
