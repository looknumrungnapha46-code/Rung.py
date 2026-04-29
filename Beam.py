import streamlit as st
import math
import plotly.graph_objects as go

st.set_page_config(page_title="RC Beam Design", layout="centered")

st.title("🏗️ RC Beam Design (ACI 318 / มยผ.)")

# ------------------------
# MATERIAL
# ------------------------
st.sidebar.header("Material")
fc = st.sidebar.number_input("fc' (MPa)", value=28.0)
fy = st.sidebar.number_input("fy (MPa)", value=420.0)

# ------------------------
# LOAD
# ------------------------
st.sidebar.header("Load")
D = st.sidebar.number_input("Dead Load (kN/m)", value=5.0)
L = st.sidebar.number_input("Live Load (kN/m)", value=3.0)

wu = 1.2 * D + 1.6 * L

# ------------------------
# BEAM INPUT
# ------------------------
st.header("📏 Beam Input")

L_beam = st.number_input("Span (m)", value=5.0)
b = st.number_input("Width b (mm)", value=250.0)
h = st.number_input("Height h (mm)", value=500.0)
cover = st.number_input("Cover (mm)", value=40.0)

d = h - cover - 10  # approx

# ------------------------
# REBAR DB
# ------------------------
rebar_db = {
    "DB12": 113,
    "DB16": 201,
    "DB20": 314,
    "DB25": 491,
    "DB28": 616,
    "DB32": 804
}

# ------------------------
# CALCULATION
# ------------------------
if st.button("ออกแบบคาน"):
    Mu = wu * L_beam**2 / 8  # kN-m
    Mu_Nmm = Mu * 1e6
    phi = 0.9

    # iterate As
    As = 100
    for _ in range(50):
        a = (As * fy) / (0.85 * fc * b)
        Mn = As * fy * (d - a/2)
        phiMn = phi * Mn
        As = As * (Mu_Nmm / phiMn)

    st.subheader("📊 ผลลัพธ์")
    st.write(f"Mu = {Mu:.2f} kN·m")
    st.write(f"As required = {As:.2f} mm²")

    # ------------------------
    # SELECT REBAR
    # ------------------------
    selected = None

    for name, area in rebar_db.items():
        n = math.ceil(As / area)
        As_provide = n * area

        if As_provide >= As:
            selected = (name, n, As_provide)
            break

    if selected:
        bar, qty, As_use = selected
        st.success(f"ใช้ {bar} จำนวน {qty} เส้น (As = {As_use:.2f} mm²)")
    else:
        st.error("❌ ต้องเพิ่มขนาดคาน")

    # ------------------------
    # DRAW (PLOTLY)
    # ------------------------
    st.subheader("📐 หน้าตัดคาน")

    fig = go.Figure()

    # beam rectangle
    fig.add_shape(
        type="rect",
        x0=0, y0=0,
        x1=b, y1=h,
        line=dict(width=2)
    )

    # draw bars
    if selected:
        spacing = b / (qty + 1)
        for i in range(qty):
            x = spacing * (i + 1)
            y = cover

            fig.add_shape(
                type="circle",
                x0=x-10, y0=y-10,
                x1=x+10, y1=y+10,
                line=dict(width=2)
            )

    fig.update_layout(
        width=400,
        height=500,
        xaxis=dict(range=[0, b], title="mm"),
        yaxis=dict(range=[0, h], title="mm"),
        showlegend=False
    )

    st.plotly_chart(fig)
