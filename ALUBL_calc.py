import streamlit as st
import pandas as pd
import datetime as dt
import os
import base64
import streamlit.components.v1 as components

# ==========================================
# 📐 الدالة الدقيقة لحساب الأمتار الطولية والبارات
# ==========================================
def calculate_detailed_project(
    opening_system,
    width_cm,
    height_cm,
    has_travars,
    profile_price_per_m_linear,
    include_glass,
    glass_price_per_m2,
    include_roller_shutter,
    roller_shutter_price_per_m2,
):
    width_m = width_cm / 100.0
    height_m = height_cm / 100.0
    surface_m2 = width_m * height_m
    perimeter_m = (width_m + height_m) * 2.0

    sys_lower = opening_system.lower()
    
    if "23000" in sys_lower:
        total_linear_meters = float(perimeter_m * 1.6 + (has_travars * width_m))
        cadre_m = perimeter_m
        ouvrant_h = height_m - 0.065
        ouvrant_w = (width_m + 0.06) / 2.0
        ouvrant_m = (ouvrant_h * 4.0) + (ouvrant_w * 4.0) + (has_travars * width_m)
    elif "42000" in sys_lower:
        total_linear_meters = float(perimeter_m * 1.8 + (has_travars * width_m))
        cadre_m = perimeter_m * 1.1
        ouvrant_m = total_linear_meters - cadre_m
    elif "cloison" in sys_lower:
        total_linear_meters = float(perimeter_m + (has_travars * width_m))
        cadre_m = perimeter_m
        ouvrant_m = 0.0
    else:
        total_linear_meters = float(perimeter_m * 1.7 + (has_travars * width_m))
        cadre_m = perimeter_m
        ouvrant_m = total_linear_meters - cadre_m

    bar_length = 6.0
    cadre_bars = int(cadre_m // bar_length) + (1 if (cadre_m % bar_length) > 0 else 0)
    ouvrant_bars = int(ouvrant_m // bar_length) + (1 if (ouvrant_m % bar_length) > 0 else 0)
    total_bars_needed = cadre_bars + ouvrant_bars

    aluminum_cost = total_linear_meters * profile_price_per_m_linear
    glass_cost = surface_m2 * glass_price_per_m2 if include_glass else 0.0
    roller_shutter_cost = surface_m2 * roller_shutter_price_per_m2 if include_roller_shutter else 0.0

    total_base_cost = aluminum_cost + glass_cost + roller_shutter_cost
    return total_linear_meters, surface_m2, aluminum_cost, glass_cost, roller_shutter_cost, total_base_cost, cadre_m, ouvrant_m, cadre_bars, ouvrant_bars, total_bars_needed

# ==========================================
# 🖼️ دالة رسم النافذة SVG
# ==========================================
def render_window_visual(width_cm, height_cm, opening_system):
    width_cm = max(float(width_cm), 10.0)
    height_cm = max(float(height_cm), 10.0)
    svg_width, svg_height = 380, 250
    frame_w, frame_h = 240.0, 150.0
    x, y = 70.0, 30.0
    sys_lower = opening_system.lower()

    if "coulison" in sys_lower or "23000" in sys_lower or "coulissant" in sys_lower:
        half_w = frame_w / 2.0
        inner_drawings = f"""
        <rect x="{x + 4}" y="{y + 4}" width="{half_w - 6}" height="{frame_h - 8}" fill="#e6f2ff" stroke="#1f4e79" stroke-width="2" rx="3"/>
        <rect x="{x + half_w + 2}" y="{y + 4}" width="{half_w - 6}" height="{frame_h - 8}" fill="#e6f2ff" stroke="#1f4e79" stroke-width="2" rx="3"/>
        """
    else:
        inner_drawings = f"""
        <rect x="{x + 4}" y="{y + 4}" width="{frame_w - 8}" height="{frame_h - 8}" fill="#f7fbff" stroke="#1f4e79" stroke-width="2" rx="3"/>
        """

    svg_code = f"""
    <html>
    <body style="margin:0; background:transparent; display:flex; justify-content:center; align-items:center;">
        <svg width="{svg_width}" height="{svg_height}" viewBox="0 0 {svg_width} {svg_height}" xmlns="http://www.w3.org/2000/svg">
            <rect width="100%" height="100%" fill="#ffffff" rx="14" />
            <rect x="15" y="10" width="{svg_width - 30}" height="{svg_height - 20}" rx="12" fill="#f5f9fd" stroke="#dce7f2" stroke-width="2" />
            <rect x="{x}" y="{y}" width="{frame_w}" height="{frame_h}" fill="none" stroke="#1f4e79" stroke-width="4" rx="4" />
            {inner_drawings}
            <text x="{svg_width / 2}" y="215" text-anchor="middle" font-size="14" font-weight="bold" fill="#355c7d" font-family="Arial">{opening_system} • {width_cm:.0f} × {height_cm:.0f} cm</text>
        </svg>
    </body>
    </html>
    """
    return svg_code

st.set_page_config(page_title="AluBL Calculator", page_icon="🪟", layout="centered")

# إجبار التنسيق العام على اليمين
st.markdown("""
<style>
    .stApp {
        direction: rtl;
        text-align: right;
    }
    label, .stSelectbox, .stTextInput, .stNumberInput {
        direction: rtl;
        text-align: right;
    }
</style>
""", unsafe_allow_html=True)

# معالجة اللوغو
logo_path = os.path.join(os.path.dirname(__file__), "logo.jpg")
encoded_logo = ""
if os.path.exists(logo_path):
    with open(logo_path, "rb") as image_file:
        encoded_logo = base64.b64encode(image_file.read()).decode("utf-8")
    st.markdown(
        f"""
        <div style="display:flex; justify-content:center; margin-bottom:20px;">
            <img src="data:image/jpeg;base64,{encoded_logo}" alt="Logo"
                 style="width:120px; height:120px; border-radius:50%; object-fit:cover; border:3px solid #f0f0f0;" />
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("<h1 style='text-align: center; color: #1f4e79;'>🪟 AluBL Calculator - حاسبة الورشة</h1>", unsafe_allow_html=True)

st.sidebar.header("معلومات الزبون والمشروع")
client_name = st.sidebar.text_input("اسم الزبون", "محمد")
client_phone = st.sidebar.text_input("رقم الهاتف", "0500000000")

opening_system = st.sidebar.selectbox(
    "نظام الفتح والأنظمة",
    ["Série 23000 (Coulissant)", "Série 42000 (Française)", "Cloison TPR", "Port Blcon", "Coulison", "Fnêtr", "Fix", "3 Rai", "4 Rai"]
)

has_travars = st.sidebar.number_input("عدد الترافارسات (Travars)", min_value=0, value=0, step=1)

profile_options = {"TPR": 1500.0, "23000 (Économique)": 4500.0, "42000 (Classique)": 5200.0, "BB77": 7500.0}
selected_profile = st.sidebar.selectbox("نوع البروفيل", list(profile_options.keys()))
aluminum_price_per_m_linear = st.sidebar.number_input("سعر المتر الخطي (دج)", min_value=0.0, value=float(profile_options.get(selected_profile, 5000.0)), step=100.0)

st.sidebar.header("الأبعاد الأساسية (سم)")
width = st.sidebar.number_input("العرض الكلي (سم)", min_value=10.0, value=100.0, step=1.0)
height = st.sidebar.number_input("الارتفاع الكلي (سم)", min_value=10.0, value=100.0, step=1.0)

include_glass = st.sidebar.checkbox("إضافة الزجاج", value=False)
glass_price = st.sidebar.number_input("سعر الزجاج للمتر المربع (دج)", min_value=0.0, value=7500.0) if include_glass else 0.0

include_roller_shutter = st.sidebar.checkbox("إضافة volet roulant", value=False)
roller_shutter_price = st.sidebar.number_input("سعر volet roulant للمتر المربع (دج)", min_value=0.0, value=10000.0) if include_roller_shutter else 0.0

st.sidebar.header("الحاشية / المارجن")
margin_mode = st.sidebar.selectbox("نوع المارجن", ["Montant fixe (DA)", "Pourcentage (%)"])
margin_value = st.sidebar.number_input("قيمة المارجن", min_value=0.0, value=0.0, step=100.0)

st.markdown("<h3 style='color: #1f4e79;'>معاينة الشكل الهندسي</h3>", unsafe_allow_html=True)
components.html(render_window_visual(width, height, opening_system), height=255)

# الحسابات
total_linear_meters, surface_m2, aluminum_cost, glass_cost, roller_shutter_cost, base_total_cost, cadre_m, ouvrant_m, cadre_bars, ouvrant_bars, total_bars_needed = calculate_detailed_project(
    opening_system, width, height, has_travars, aluminum_price_per_m_linear, include_glass, glass_price, include_roller_shutter, roller_shutter_price
)

st.markdown("---")
st.markdown("<h3 style='color: #1f4e79;'>📏 مخططات القص واستهلاك البارات (Bars de 6m)</h3>", unsafe_allow_html=True)

sys_lower = opening_system.lower()
if "23000" in sys_lower:
    ouv_h_23 = height - 6.5
    ouv_w_23 = (width / 2.0) + 3.0
    st.markdown(f"""
    <div style='background-color: #e8f4fd; padding: 12px; border-radius: 8px; border-right: 4px solid #1f4e79;'>
        <b>قص ألومنيوم سلسلة 23000 (مقاس {width:.0f} × {height:.0f} سم):</b><br>
        • ارتفاع الضلفة (H): <b>{ouv_h_23:.1f} سم</b> (الارتفاع الكلي - 6.5 سم)<br>
        • عرض الضلفة (L): <b>{ouv_w_23:.1f} سم</b> (عدد 2 قطع)
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown(f"""
    <div style='background-color: #e8f4fd; padding: 12px; border-radius: 8px; border-right: 4px solid #1f4e79;'>
        <b>مخطط القص (مقاس {width:.0f} × {height:.0f} سم)</b>
    </div>
    """, unsafe_allow_html=True)

col_b1, col_b2, col_b3 = st.columns(3)
with col_b1:
    st.metric("بارات الكادر (Cadre)", f"{cadre_bars} بار", f"{cadre_m:.2f} م.ط")
with col_b2:
    st.metric("بارات الضلف (Ouvrants)", f"{ouvrant_bars} بار", f"{ouvrant_m:.2f} م.ط")
with col_b3:
    st.metric("إجمالي البارات (6m)", f"{total_bars_needed} بار", f"المجموع: {total_linear_meters:.2f} م.ط")

margin_amount = margin_value if margin_mode == "Montant fixe (DA)" else base_total_cost * (margin_value / 100.0)
final_total_cost = base_total_cost + margin_amount

st.markdown("---")
st.markdown("<h3 style='color: #1f4e79;'>📊 ملخص التكلفة المفصلة</h3>", unsafe_allow_html=True)
st.markdown(f"• المتر الطولي للألومنيوم: <b>{total_linear_meters:.2f} م.ط</b> (التكلفة: <b>{aluminum_cost:,.2f} دج</b>)", unsafe_allow_html=True)
if include_glass:
    st.markdown(f"• تكلفة الزجاج ({surface_m2:.2f} م²): <b>{glass_cost:,.2f} دج</b>", unsafe_allow_html=True)
if include_roller_shutter:
    st.markdown(f"• تكلفة Volet Roulant ({surface_m2:.2f} م²): <b>{roller_shutter_cost:,.2f} دج</b>", unsafe_allow_html=True)

st.markdown(f"<div style='background-color: #d4edda; padding: 15px; border-radius: 8px; color: #155724; font-size: 18px; font-weight: bold; text-align: center; margin-top: 15px;'>المجموع النهائي الحقيقي: {final_total_cost:,.2f} دج</div>", unsafe_allow_html=True)

history_file = "alubl_history.csv"
col_btn1, col_btn2 = st.columns(2)

with col_btn1:
    if st.button("📄 حفظ كـ Devis فقط"):
        new_record = {"التاريخ": [dt.datetime.now().strftime("%Y-%m-%d %H:%M")], "الزبون": [client_name], "الهاتف": [client_phone], "النظام": [f"{opening_system} ({width:.0f}x{height:.0f}cm)"], "الحالة": ["📄 Devis"], "التكلفة (دج)": [final_total_cost]}
        df_new = pd.DataFrame(new_record)
        df_new.to_csv(history_file, mode="a", header=not os.path.exists(history_file), index=False, encoding="utf-8-sig")
        st.success("تم الحفظ بنجاح!")
        st.rerun()

with col_btn2:
    if st.button("✅ تأكيد الإنجاز (Commande)"):
        new_record = {"التاريخ": [dt.datetime.now().strftime("%Y-%m-%d %H:%M")], "الزبون": [client_name], "الهاتف": [client_phone], "النظام": [f"{opening_system} ({width:.0f}x{height:.0f}cm)"], "الحالة": ["✅ Commande"], "التكلفة (دج)": [final_total_cost]}
        df_new = pd.DataFrame(new_record)
        df_new.to_csv(history_file, mode="a", header=not os.path.exists(history_file), index=False, encoding="utf-8-sig")
        st.success("تم تأكيد الطلبية!")
        st.rerun()