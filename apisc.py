import pandas as pd
import google.generativeai as genai

# 1. Configura tu API Key de Google AI Studio
# Consíguela en: https://aistudio.google.com/app/apikey
GENAI_API_KEY = "AIzaSyDFabjhHXIK5ftyk7SRQBjdykWJLPGzN5c"
genai.configure(api_key=GENAI_API_KEY)

# 2. Cargamos tu "Base de Datos" de frutas
df = pd.read_csv('historial_frutas_vegetales.csv')

def buscar_contexto_en_csv(pregunta_usuario):
    """
    Busca productos mencionados en la pregunta dentro del CSV
    para darle contexto real al LLM.
    """
    # Buscamos coincidencias de palabras clave en la columna 'producto'
    productos_encontrados = []
    for producto in df['producto'].tolist():
        if producto.lower() in pregunta_usuario.lower():
            # Extraemos la info de esa fila
            info = df[df['producto'] == producto].iloc[0]
            contexto_item = (
                f"- {info['producto']}: Dura {info['vida_util_dias']} días. "
                f"Cuidado con: {info['signos_deterioro']}. "
                f"Tip: {info['tips_conservacion']}. "
                f"Uso de emergencia: {info['uso_emergencia']}."
            )
            productos_encontrados.append(contexto_item)
    
    return "\n".join(productos_encontrados) if productos_encontrados else "No hay historial específico para estos productos."

def consultar_gemini_con_rag(pregunta_usuario):
    # Recuperamos la info de nuestro CSV
    contexto_historico = buscar_contexto_en_csv(pregunta_usuario)
    
    # Armamos el prompt Pro con el estilo que definimos
    prompt_final = f"""
    Eres un experto en gestión de desperdicio de alimentos y economía del hogar.
    
    CONTEXTO DEL HISTORIAL (Base de datos):
    {contexto_historico}
    
    PREGUNTA DEL USUARIO:
    "{pregunta_usuario}"
    
    INSTRUCCIONES:
    1. Usa el contexto del historial para dar consejos específicos.
    2. Si el producto está por echarse a perder, prioriza la 'Receta de rescate'.
    3. Sé breve, práctico y empático.
    """
    
    # Inicializamos el modelo (Gemini 1.5 o 2.0 Flash)
    model = genai.GenerativeModel('gemini-1.5-flash') # O 'gemini-2.0-flash-exp'
    
    response = model.generate_content(prompt_final)
    return response.text

# --- PRUEBA DE FUEGO ---
# Dani, aquí es donde sucede la magia:
tu_duda = "Oye, compré muchas espinacas y se me están olvidando, ¿qué hago para que no se mueran?"

print("--- Consultando a Gemini con tu RAG local ---")
respuesta = consultar_gemini_con_rag(tu_duda)
print(respuesta)