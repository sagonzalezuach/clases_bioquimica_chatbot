import streamlit as st
import os
from openai import OpenAI
from pptx import Presentation
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Inicializar cliente OpenAI
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# --- Personalización visual ---
st.set_page_config(page_title="ChatBot Bioquímica UACH", page_icon="🔖", layout="centered")

# Estilo CSS en tonos rosas
st.markdown("""
    <style>
    body {
        background-color: #fff0f5;
    }
    .main {
        background-color: #ffe6f0;
        padding: 2rem;
        border-radius: 12px;
    }
    h1, h2, h3, h4 {
        color: #c2185b;
    }
    .stButton button {
        background-color: #ec407a;
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

# --- Encabezado ---
st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/3/31/Escudo_UACH.png/320px-Escudo_UACH.png", width=100)
st.title("ChatBot de Bioquímica – GPT-4 Edition")
st.markdown("""
**Facultad de Medicina y Ciencias Biomédicas**  
**Universidad Autónoma de Chihuahua**  
Este asistente responde preguntas sobre aminoácidos usando tus propias clases: presentaciones, lectura y video.
""")

# Archivos fuente
pptx_path = "clase_001_aminoacidos.pptx"
txt_path = "capitulo_aminoacidos_mckee_LIMPIO.txt"
video_url = "https://youtu.be/6-rvZqSTANo?si=WfT34ODacliTwOhz"

# Funciones para cargar contenido
def extract_text_from_pptx(file_path):
    prs = Presentation(file_path)
    return [" ".join(shape.text for shape in slide.shapes if hasattr(shape, "text")).strip() for slide in prs.slides]

def extract_text_from_txt(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return [p.strip() for p in f.read().split("\n\n") if len(p.strip()) > 60]

slides = extract_text_from_pptx(pptx_path)
chapter = extract_text_from_txt(txt_path)
all_docs = slides + chapter

# Entrada del usuario
query = st.text_input("🎓 Escribe tu pregunta sobre aminoácidos:")

if query:
    vectorizer = TfidfVectorizer().fit_transform([query] + all_docs)
    similarity = cosine_similarity(vectorizer[0:1], vectorizer[1:])
    top_indices = similarity[0].argsort()[-3:][::-1]
    context = "\n\n".join([all_docs[i] for i in top_indices])

    prompt = f"""
Eres un asistente de bioquímica de la Facultad de Medicina de la UACH.
Responde solo usando los siguientes materiales proporcionados por la Dra. Susana González Chávez.
No inventes nada fuera del contenido.

PREGUNTA: {query}

MATERIALES:
{context}

RESPUESTA:
"""

    with st.spinner("🤖 Consultando a GPT-4..."):
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=600
        )

        st.subheader(":open_book: Respuesta elaborada con base en tus clases:")
        st.write(response.choices[0].message.content)
        st.caption("📚 Esta respuesta se generó con base en tus presentaciones, lectura y video. No se utilizó información externa.")

        st.markdown("**🎥 Explicación en video:**")
        st.video(video_url)

# Pie de página
st.markdown("""
---
**Desarrollado por la Dra. Susana González Chávez**  
Facultad de Medicina y Ciencias Biomédicas, UACH  
:heart: Proyecto educativo con fines docentes
""")
