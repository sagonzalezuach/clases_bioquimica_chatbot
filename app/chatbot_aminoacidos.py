import streamlit as st
import os
import openai
from pptx import Presentation
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Configurar clave de API desde secretos de Streamlit
openai.api_key = st.secrets["OPENAI_API_KEY"]

st.title("🤖 ChatBot de Bioquímica – GPT-4 Edition")
st.success("Este chatbot usa GPT-4 para responder preguntas sobre aminoácidos con base en tus materiales de clase.")

# Archivos fuente
pptx_path = "clase_001_aminoacidos.pptx"
txt_path = "capitulo_aminoacidos_mckee_LIMPIO.txt"

# Video relacionado
video_url = "https://youtu.be/6-rvZqSTANo?si=WfT34ODacliTwOhz"

# Extraer texto de pptx
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

# Extraer bloques del archivo txt
def extract_text_from_txt(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    return [p.strip() for p in content.split("\n\n") if len(p.strip()) > 60]

# Cargar contenido
slides = extract_text_from_pptx(pptx_path)
chapter = extract_text_from_txt(txt_path)
all_docs = slides + chapter

# Entrada del usuario
query = st.text_input("Escribe tu pregunta sobre aminoácidos:")

if query:
    # Vectorizar pregunta y documentos
    vectorizer = TfidfVectorizer().fit_transform([query] + all_docs)
    similarity = cosine_similarity(vectorizer[0:1], vectorizer[1:])
    top_indices = similarity[0].argsort()[-3:][::-1]  # Los 3 más relevantes

    # Combinar fragmentos relevantes como contexto
    context = "\n\n".join([all_docs[i] for i in top_indices])

    # Construir mensaje para GPT-4
    prompt = f"""
Eres un asistente de bioquímica que responde con claridad, precisión y lenguaje profesional, usando solo el contenido proporcionado.
Responde a la siguiente pregunta usando los fragmentos de clase como contexto. Si no está en el contexto, responde que no se encuentra en los materiales.

PREGUNTA: {query}

MATERIALES DE CLASE:
{context}

RESPUESTA:
"""

    with st.spinner("Consultando a GPT-4..."):
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=600
        )

        st.subheader("📖 Respuesta elaborada por GPT-4:")
        st.write(response.choices[0].message.content)

        st.markdown("🎥 **También puedes ver la explicación en video:**")
        st.video(video_url)
