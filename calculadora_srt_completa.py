import streamlit as st
from datetime import date
import requests

st.set_page_config(page_title="Calculadora SRT Completa", page_icon=":balance_scale:", layout="centered")
st.title("Calculadora de Indemnización (SRT) - Ley 26.773 y 27.348")

st.markdown("""
Calculadora simplificada para estimar indemnizaciones por contingencias laborales: ILP, gran invalidez y fallecimiento.
""")

# --- Entradas comunes ---
tipo = st.selectbox("Tipo de contingencia:", [
    "ILP parcial (≤ 50%)",
    "ILP parcial (51–65%)",
    "ILP total (≥ 66%)",
    "Gran invalidez",
    "Fallecimiento",
    "Incapacidad Laboral Temporaria (ILT)"])

vib = st.number_input("Valor Ingreso Base (VIB con RIPTE en pesos $):", min_value=0.0, step=1000.0, format="%.2f")
edad = st.number_input("Edad al momento de la primera manifestación invalidante:", min_value=16, max_value=100, step=1)
fecha_hecho = st.date_input("Fecha del hecho:", value=date.today())
is_in_itinere = st.checkbox("¿Accidente in itinere?")

ilp = 0
if tipo != "Fallecimiento" and tipo != "Gran invalidez" and tipo != "ILT":
    ilp = st.number_input("Porcentaje de incapacidad (%):", min_value=1.0, max_value=100.0, step=0.1, format="%.2f")

# --- Obtener RIPTE automático (último valor disponible de la serie oficial) ---
def obtener_ripte_actual():
    try:
        url = "https://api.estadisticasbcra.com/ripte"
        headers = {"Authorization": "BEARER eyJhbGciOiJIUzUxMiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3ODI4NDMyNjMsInR5cGUiOiJleHRlcm5hbCIsInVzZXIiOiJiYWxhZG9hYm9nYWRvc0BnbWFpbC5jb20ifQ.k41Nvmqs3RLiuQz7mF-KvFfnwipS-JJi7UOadVmf7lqwuVtc5tpb83wOd176W4_D-VRJBpuCP1IE9rR4y7EF-A"}  # Requiere token gratuito desde estadisticasbcra.com
        r = requests.get(url, headers=headers)
        if r.status_code == 200:
            datos = r.json()
            return float(datos[-1]['valor'])  # último RIPTE
    except:
        pass
    return 1.0  # fallback

ripte_index = obtener_ripte_actual()

# --- Constantes ---
piso_minimo_base = 55699217 * ripte_index / 100000  # Ajustado por RIPTE si corresponde
capu_dict = {
    "ILP total (≥ 66%)": 30944014,
    "ILP parcial (51–65%)": 24755211,
    "Fallecimiento": 37132805
}
gran_invalidez_valores = {
    "Mayo 2025": 631286.10,
    "Junio 2025": 648835.85,
    "Julio 2025": 658568.39
}

# --- Cálculo base ---
capital = 0
piso = 0
capu = 0
iapu = 0

if tipo.startswith("ILP"):
    capital = 53 * vib * (ilp / 100) * (65 / edad)
    piso = piso_minimo_base * (ilp / 100)
    capu = capu_dict.get(tipo, 0) * (ilp / 100)
    if not is_in_itinere:
        iapu = 0.20 * max(capital, piso)
    total = max(capital, piso) + capu + iapu
    st.subheader("Resultado ILP")
    st.write(f"Capital SRT: ${capital:,.2f}")
    st.write(f"Piso mínimo: ${piso:,.2f}")
    st.write(f"CAPU: ${capu:,.2f}")
    st.write(f"IAPU: ${iapu:,.2f}")
    st.success(f"**Total estimado: ${total:,.2f}**")

elif tipo == "Fallecimiento":
    base = vib
    capital = 53 * base * (65 / edad)
    piso = piso_minimo_base
    capu = capu_dict["Fallecimiento"]
    if not is_in_itinere:
        iapu = 0.20 * max(capital, piso)
    total = max(capital, piso) + capu + iapu
    st.subheader("Resultado Fallecimiento")
    st.write(f"Capital SRT: ${capital:,.2f}")
    st.write(f"Piso mínimo: ${piso:,.2f}")
    st.write(f"CAPU: ${capu:,.2f}")
    st.write(f"IAPU: ${iapu:,.2f}")
    st.success(f"**Total estimado: ${total:,.2f}**")

elif tipo == "Gran invalidez":
    st.subheader("Gran Invalidez")
    for mes, valor in gran_invalidez_valores.items():
        st.write(f"{mes}: ${valor:,.2f} por mes")
    st.info("La prestación es mensual y se actualiza periódicamente. No hay fórmula única.")

elif tipo == "ILT":
    st.subheader("ILT (Incapacidad Temporaria)")
    st.markdown("La ART debe abonar el salario completo conforme Art. 208 LCT + aumentos según convenios o aumentos generales.")
    st.info("Usar promedio de salarios últimos 6 meses si son variables.")

# --- Botón de WhatsApp ---
telefono = "5491134567890"
mensaje = "Hola, quisiera recibir asesoramiento sobre una indemnización laboral."
whatsapp_url = f"https://wa.me/{telefono}?text={mensaje.replace(' ', '%20')}"
st.markdown(f"[\ud83d\udcde Chatear por WhatsApp]({whatsapp_url})", unsafe_allow_html=True)

st.caption("*Esta herramienta es orientativa. Para un cálculo preciso o representación legal, contactá a un profesional.*")

