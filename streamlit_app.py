
import streamlit as st
import pandas as pd
import random
import io

st.set_page_config(page_title="Generador de Grupos al Azar", layout="wide")

st.title("🎲 Generador de Grupos al Azar")

st.markdown("""
Este generador permite subir una lista de nombres (uno por línea) o parejas (`nombre y nombre`) 
y repartirlos aleatoriamente en grupos equilibrados.  
La diferencia máxima entre grupos será de 1 persona.
""")

# Cargar archivo de texto
uploaded_file = st.file_uploader("📤 Sube tu archivo de texto (.txt) con la lista de nombres", type=["txt"])

def contar_personas(lista):
    return sum(2 if " y " in nombre.lower() else 1 for nombre in lista)

def generar_grupos_ajustados(lista_nombres, num_grupos, max_intentos=10):
    for _ in range(max_intentos):
        random.shuffle(lista_nombres)
        grupos = [[] for _ in range(num_grupos)]
        for i, nombre in enumerate(lista_nombres):
            grupos[i % num_grupos].append(nombre)
        personas_por_grupo = [contar_personas(grupo) for grupo in grupos]
        if max(personas_por_grupo) - min(personas_por_grupo) <= 1:
            return grupos
    return grupos

if uploaded_file:
    nombres_raw = uploaded_file.read().decode("utf-8").splitlines()
    nombres = [line.strip() for line in nombres_raw if line.strip()]
    total_personas = contar_personas(nombres)

    st.success(f"📋 Lista cargada correctamente. Total de personas detectadas: {total_personas}")

    num_grupos = st.number_input("Selecciona el número de grupos", min_value=1, max_value=10, value=8)

    if st.button("🔀 Generar Grupos"):
        grupos = generar_grupos_ajustados(nombres, num_grupos)
        personas_por_grupo = [contar_personas(grupo) for grupo in grupos]
        min_pers = min(personas_por_grupo)
        max_pers = max(personas_por_grupo)

        st.subheader(f"📊 Reparto generado (personas por grupo: {min_pers}-{max_pers})")
        cols = st.columns(num_grupos)

        for i, (grupo, col) in enumerate(zip(grupos, cols)):
            with col:
                st.markdown(f"**Grupo {i+1}**")
                for j, nombre in enumerate(grupo):
                    if j == 0:
                        st.markdown(f"👉 **{nombre}**")
                    else:
                        st.markdown(f"- {nombre}")

        # Descargar Excel
        df = pd.DataFrame({f"Grupo {i+1}": pd.Series(grupo) for i, grupo in enumerate(grupos)})
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False)
        st.download_button(
            label="📥 Descargar Excel",
            data=output.getvalue(),
            file_name="grupos_generados.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
else:
    st.warning("🔁 Sube un archivo de texto para empezar.")
