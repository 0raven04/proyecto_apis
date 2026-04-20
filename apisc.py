import pandas as pd
from google import genai
import time

# --- CONFIGURACIÓN ---
API_KEY = "TU_API_KEY_AQUI"
client = genai.Client(api_key="AIzaSyAaQRfSMsPr16i06uOUtcX-x_aqCI2Zs5Y")

# Usamos exactamente el ID que salió en tu lista
MODEL_ID = "gemini-2.5-flash" 

df = pd.read_csv('historial_frutas_vegetales.csv')

def buscar_contexto_en_csv(pregunta_usuario):
    # Una búsqueda un poco más flexible por si escribes en plural
    productos_encontrados = []
    palabras_usuario = pregunta_usuario.lower().split()
    
    for producto in df['producto'].tolist():
        # Si el nombre del producto está en la pregunta
        if producto.lower() in pregunta_usuario.lower():
            info = df[df['producto'] == producto].iloc[0]
            contexto_item = (
                f"- {info['producto']}: Vida útil {info['vida_util_dias']} días. "
                f"Signos de daño: {info['signos_deterioro']}. "
                f"Uso de emergencia (Receta): {info['uso_emergencia']}."
            )
            productos_encontrados.append(contexto_item)
    
    return "\n".join(productos_encontrados) if productos_encontrados else "No tengo historial de estos productos."

def consultar_gemini_con_rag(pregunta_usuario):
    contexto_historico = buscar_contexto_en_csv(pregunta_usuario)
    
    # Prompt optimizado para tu problema de desperdicio
    prompt = f"""
    Actúa como un experto en gestión de alimentos. 
    Ayuda al usuario a evitar el desperdicio basándote en este historial de su cocina:
    
    HISTORIAL RECUPERADO:
    {contexto_historico}
    
    PREGUNTA DEL USUARIO:
    "{pregunta_usuario}"
    
    Respuesta breve, empática y directa:
    """

    try:
        response = client.models.generate_content(
            model=MODEL_ID,
            contents=prompt
        )
        return response.text
    except Exception as e:
        if "429" in str(e):
            return "❌ Te acabaste la cuota por este minuto, Dani. Espera 30 segunditos."
        return f"❌ Error: {e}"

# --- EJECUCIÓN ---
print(f"--- Usando el modelo: {MODEL_ID} ---")
pregunta = input("¿Qué quieres saber sobre tus frutas y verduras? ")
print(consultar_gemini_con_rag(pregunta))