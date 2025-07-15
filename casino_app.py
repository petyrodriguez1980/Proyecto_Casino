import streamlit as st
import streamlit.components.v1 as components
import uuid
import hashlib

st.set_page_config(layout="wide")

# ----------- AUTENTICACIÓN -----------
def hash_password(pwd):
    return hashlib.sha256(pwd.encode()).hexdigest()

USUARIOS = {
    "responsable": hash_password("admin123"),
    "usuario": hash_password("crupier123")
}

if "autenticado" not in st.session_state:
    st.session_state.autenticado = False
    st.session_state.rol = None

if not st.session_state.autenticado:
    st.sidebar.title("🔐 Iniciar sesión")
    usuario = st.sidebar.text_input("Usuario")
    contrasena = st.sidebar.text_input("Contraseña", type="password")

    if usuario and contrasena:
        if usuario in USUARIOS:
            if hash_password(contrasena) == USUARIOS[usuario]:
                st.session_state.autenticado = True
                st.session_state.rol = "Responsable" if usuario == "responsable" else "Usuario"
                st.rerun()
            else:
                st.sidebar.error("❌ Contraseña incorrecta")
        else:
            st.sidebar.warning("⚠️ Usuario no encontrado")

if not st.session_state.autenticado:
    st.stop()

rol = st.session_state.rol

# Botón cerrar sesión
with st.sidebar:
    if st.button("🔓 Cerrar sesión"):
        st.session_state.autenticado = False
        st.session_state.rol = None
        st.rerun()

# ----------- RELOJ JAVASCRIPT -----------
def mostrar_reloj_js():
    reloj_html = """
    <div style="text-align: center;">
        <h3>🕒 <span id="reloj">--:--:--</span></h3>
    </div>
    <script>
    const reloj = document.getElementById("reloj");
    function actualizarHora() {
        const ahora = new Date();
        const horas = String(ahora.getHours()).padStart(2, '0');
        const minutos = String(ahora.getMinutes()).padStart(2, '0');
        const segundos = String(ahora.getSeconds()).padStart(2, '0');
        reloj.textContent = `${horas}:${minutos}:${segundos}`;
    }
    setInterval(actualizarHora, 1000);
    actualizarHora();
    </script>
    """
    components.html(reloj_html, height=80)

# ----------- INICIALIZACIÓN -----------
if "empleados" not in st.session_state:
    st.session_state.empleados = []

if "finalizaron_jornada" not in st.session_state:
    st.session_state.finalizaron_jornada = []

if "mesas" not in st.session_state:
    nombres_mesas = ["RA1", "RA2", "RA3", "RA4", "BJ1", "BJ2", "PK1", "iT-PK", "iT-BJ", "TEXAS", "PB", "Mini PB"]
    st.session_state.mesas = {nombre: [] for nombre in nombres_mesas}
else:
    nombres_mesas = list(st.session_state.mesas.keys())

if "confirmar_liberacion" not in st.session_state:
    st.session_state.confirmar_liberacion = {}

if "confirmar_eliminacion" not in st.session_state:
    st.session_state.confirmar_eliminacion = {}

# ----------- SOLO PARA RESPONSABLES -----------
if rol == "Responsable":

    # FORMULARIO LATERAL
    if "nombre_nuevo" not in st.session_state:
        st.session_state.nombre_nuevo = ""
    if "categoria_nueva" not in st.session_state:
        st.session_state.categoria_nueva = "Seleccionar"
    if "reset_form" not in st.session_state:
        st.session_state.reset_form = False

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

    # 🎰 MESAS
    st.markdown("## 🃏 Área de mesas de trabajo")
    col_mesas = st.columns(4)

    for i, (nombre_mesa, empleados_mesa) in enumerate(st.session_state.mesas.items()):
        with col_mesas[i % 4]:
            with st.container():
                st.markdown(f"""<div style='border: 2px solid #ccc; border-radius: 12px; padding: 10px; margin-bottom: 10px; background-color: #f9f9f9;'>
                    <h4 style='text-align: center;'>🃏 {nombre_mesa}</h4>""", unsafe_allow_html=True)
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

    # 🛋️ SALA DE DESCANSO
    col_descanso, col_reloj = st.columns([6, 1])
    with col_descanso:
        st.markdown("## 🛋️ Sala de descanso")
    with col_reloj:
        mostrar_reloj_js()

    if st.button("📦 ASIGNAR empleados a sus mesas"):
        for emp in st.session_state.empleados:
            if emp["mesa"] is None and emp["mesa_asignada"]:
                destino = emp["mesa_asignada"]
                emp["mesa"] = destino
                st.session_state.mesas[destino].append(emp)
                emp["mesa_asignada"] = None
        st.success("Todos los empleados asignados fueron enviados a sus mesas.")
        st.rerun()

    for emp in st.session_state.empleados:
        if emp["mesa"] is None:
            with st.expander(f"👤 {emp['nombre']} ({emp['categoria']})", expanded=False):
                emp["mesa_asignada"] = st.selectbox("Asignar a mesa:", [None] + nombres_mesas,
                    index=0 if not emp["mesa_asignada"] else nombres_mesas.index(emp["mesa_asignada"]) + 1,
                    key=f"mesa_asig_{emp['id']}")
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

# ----------- ASIGNACIONES PENDIENTES (VISIBLES A TODOS) -----------
st.markdown("### 📝 Asignaciones pendientes")
for emp in st.session_state.empleados:
    if emp["mesa"] is None and emp["mesa_asignada"]:
        st.info(f"{emp['nombre']} será enviado a **{emp['mesa_asignada']}**. " +
                (f"Mensaje: _{emp['mensaje']}_" if emp['mensaje'] else ""))

# ----------- FINALIZARON JORNADA -----------
with st.sidebar:
    if st.session_state.finalizaron_jornada:
        st.markdown("#### ✅ Finalizaron jornada")
        for emp in st.session_state.finalizaron_jornada:
            st.markdown(f"- 👋 {emp['nombre']} ({emp['categoria']})")
