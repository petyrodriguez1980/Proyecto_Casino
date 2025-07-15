import streamlit as st
from datetime import datetime
import time
import uuid

st.set_page_config(layout="wide")

# 🕒 Reloj centrado arriba
col_r1, col_r2, col_r3 = st.columns([4, 2, 4])
with col_r2:
    st.markdown("### 🕒 " + datetime.now().strftime("%H:%M:%S"))

# Inicialización
if "empleados" not in st.session_state:
    st.session_state.empleados = []

if "finalizaron_jornada" not in st.session_state:
    st.session_state.finalizaron_jornada = []

if "mesas" not in st.session_state:
    nombres_mesas = ["RA1", "RA2", "RA3", "RA4", "BJ1", "BJ2", "PK1", "iT-PK", "iT-BJ", "TEXAS", "PB", "Mini PB"]
    st.session_state.mesas = {nombre: [] for nombre in nombres_mesas}
else:
    nombres_mesas = list(st.session_state.mesas.keys())

# Inicializar campos del formulario
if "nombre_nuevo" not in st.session_state:
    st.session_state.nombre_nuevo = ""
if "categoria_nueva" not in st.session_state:
    st.session_state.categoria_nueva = "Seleccionar"
if "reset_form" not in st.session_state:
    st.session_state.reset_form = False

# ➕ Agregar empleados
with st.sidebar:
    st.markdown("## ➕ Agregar empleado")

    if st.session_state.reset_form:
        st.session_state.nombre_nuevo = ""
        st.session_state.categoria_nueva = "Seleccionar"
        st.session_state.reset_form = False

    nombre_nuevo = st.text_input("Nombre", value=st.session_state.nombre_nuevo, key="nombre_nuevo")
    opciones_categoria = ["Seleccionar", "Jefe de Mesa", "Crupier de 1º", "Crupier de 2º", "Crupier de 3º"]
    categoria_nueva = st.selectbox("Categoría", opciones_categoria, index=opciones_categoria.index(st.session_state.categoria_nueva), key="categoria_nueva")

    if st.button("Agregar"):
        if not nombre_nuevo:
            st.warning("Por favor ingresa un nombre.")
        elif categoria_nueva == "Seleccionar":
            st.warning("Por favor selecciona una categoría válida.")
        else:
            nuevo = {
                "id": str(uuid.uuid4()),
                "nombre": nombre_nuevo,
                "categoria": categoria_nueva,
                "foto": None,
                "mesa": None,
                "mesa_asignada": None,
                "mensaje": ""
            }
            st.session_state.empleados.append(nuevo)
            st.success(f"{nombre_nuevo} agregado a sala de descanso.")
            st.session_state.reset_form = True
            st.rerun()

# 🎰 Área de mesas
st.markdown("## 🃏 Área de mesas de trabajo")
col_mesas = st.columns(4)

if "confirmar_liberacion" not in st.session_state:
    st.session_state.confirmar_liberacion = {}

for i, (nombre_mesa, empleados_mesa) in enumerate(st.session_state.mesas.items()):
    with col_mesas[i % 4]:
        with st.container():
            st.markdown(
                f"""
                <div style='border: 2px solid #ccc; border-radius: 12px; padding: 10px; margin-bottom: 10px; background-color: #f9f9f9;'>
                    <h4 style='text-align: center;'>🃏 {nombre_mesa}</h4>
                """,
                unsafe_allow_html=True
            )

            for emp in empleados_mesa:
                st.markdown(f"- 👤 {emp['nombre']} ({emp['categoria']})")
                confirmar = st.session_state.confirmar_liberacion.get(emp["id"], False)

                if not confirmar:
                    if st.button(f"❌ Liberar", key=f"lib_{emp['id']}"):
                        st.session_state.confirmar_liberacion[emp["id"]] = True
                        st.rerun()
                else:
                    col1, col2 = st.columns([1, 1])
                    with col1:
                        if st.button("✅ Confirmar", key=f"confirm_{emp['id']}"):
                            empleados_mesa.remove(emp)
                            emp["mesa"] = None
                            st.session_state.confirmar_liberacion.pop(emp["id"])
                            st.rerun()
                    with col2:
                        if st.button("❌ Cancelar", key=f"cancel_{emp['id']}"):
                            st.session_state.confirmar_liberacion.pop(emp["id"])
                            st.rerun()

            st.markdown("</div>", unsafe_allow_html=True)

# 🛋️ SALA DE DESCANSO + ELIMINACIÓN
col_descanso, col_reloj = st.columns([6, 1])

# 📦 Asignar empleados
if st.button("📦 ASIGNAR empleados a sus mesas"):
    for emp in st.session_state.empleados:
        if emp["mesa"] is None and emp["mesa_asignada"]:
            destino = emp["mesa_asignada"]
            emp["mesa"] = destino
            st.session_state.mesas[destino].append(emp)
            emp["mesa_asignada"] = None
    st.success("Todos los empleados asignados fueron enviados a sus mesas.")
    st.rerun()

with col_descanso:
    st.markdown("## 🛋️ Sala de descanso")
with col_reloj:
    st.markdown("### 🕒")
    st.markdown(f"**{datetime.now().strftime('%H:%M:%S')}**")

if "confirmar_eliminacion" not in st.session_state:
    st.session_state.confirmar_eliminacion = {}

for emp in st.session_state.empleados:
    if emp["mesa"] is None:
        with st.expander(f"👤 {emp['nombre']} ({emp['categoria']})", expanded=False):
            emp["mesa_asignada"] = st.selectbox(
                "Asignar a mesa:", [None] + nombres_mesas,
                index=0 if not emp["mesa_asignada"] else nombres_mesas.index(emp["mesa_asignada"]) + 1,
                key=f"mesa_asig_{emp['id']}"
            )
            emp["mensaje"] = st.text_input("Mensaje opcional:", key=f"msg_{emp['id']}")

            if not st.session_state.confirmar_eliminacion.get(emp["id"], False):
                if st.button("🛑 Finalizar jornada", key=f"fin_{emp['id']}"):
                    st.session_state.confirmar_eliminacion[emp["id"]] = True
                    st.rerun()
            else:
                col1, col2 = st.columns([1, 1])
                with col1:
                    if st.button("✅ Confirmar salida", key=f"conf_out_{emp['id']}"):
                        st.session_state.empleados.remove(emp)
                        st.session_state.finalizaron_jornada.append(emp)
                        st.session_state.confirmar_eliminacion.pop(emp["id"])
                        st.rerun()
                with col2:
                    if st.button("❌ Cancelar", key=f"canc_out_{emp['id']}"):
                        st.session_state.confirmar_eliminacion.pop(emp["id"])
                        st.rerun()

# 📝 Asignaciones pendientes
st.markdown("### 📝 Asignaciones pendientes")
for emp in st.session_state.empleados:
    if emp["mesa"] is None and emp["mesa_asignada"]:
        st.info(f"{emp['nombre']} será enviado a **{emp['mesa_asignada']}**. "
                + (f"Mensaje: _{emp['mensaje']}_" if emp['mensaje'] else ""))

# ✅ Finalizaron jornada (en el sidebar)
with st.sidebar:
    if st.session_state.finalizaron_jornada:
        st.markdown("#### ✅ Finalizaron jornada")
        for emp in st.session_state.finalizaron_jornada:
            st.markdown(f"- 👋 {emp['nombre']} ({emp['categoria']})")
