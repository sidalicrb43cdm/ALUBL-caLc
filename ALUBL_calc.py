import streamlit as st
import pandas as pd
import datetime as dt
import os
import base64
import streamlit.components.v1 as components

CHUTE_FILE = "workshop_chutes.csv"
RAW_STOCK_FILE = "workshop_raw_stock.csv"
BON_HISTORY_FILE = "workshop_bons_history.csv"
DEVIS_HISTORY_FILE = "workshop_devis_history.csv"

# ==========================================
# 📥 دالة إدارة أرشيف الـ Devis
# ==========================================
def manage_devis_archive(action, data_dict=None, index_to_update=None, new_status=None, index_to_delete=None):
    if not os.path.exists(DEVIS_HISTORY_FILE):
        df_init = pd.DataFrame(columns=["التاريخ", "اسم الزبون", "رقم الهاتف", "النظام", "المقاسات (سم)", "المبلغ (دج)", "الحالة"])
        df_init.to_csv(DEVIS_HISTORY_FILE, index=False, encoding="utf-8-sig")

    if action == "add" and data_dict:
        new_row = pd.DataFrame([data_dict])
        new_row.to_csv(DEVIS_HISTORY_FILE, mode="a", header=False, index=False, encoding="utf-8-sig")
    
    elif action == "update_status" and index_to_update is not None and new_status is not None:
        try:
            df = pd.read_csv(DEVIS_HISTORY_FILE)
            if index_to_update in df.index:
                df.at[index_to_update, "الحالة"] = new_status
                df.to_csv(DEVIS_HISTORY_FILE, index=False, encoding="utf-8-sig")
        except Exception:
            pass

    elif action == "delete" and index_to_delete is not None:
        try:
            df = pd.read_csv(DEVIS_HISTORY_FILE)
            if index_to_delete in df.index:
                df = df.drop(index_to_delete).reset_index(drop=True)
                df.to_csv(DEVIS_HISTORY_FILE, index=False, encoding="utf-8-sig")
        except Exception:
            pass

    try:
        return pd.read_csv(DEVIS_HISTORY_FILE)
    except Exception:
        return pd.DataFrame(columns=["التاريخ", "اسم الزبون", "رقم الهاتف", "النظام", "المقاسات (سم)", "المبلغ (دج)", "الحالة"])

# ==========================================
# 📥 دالة إدارة وإدخال المخزون الجديد
# ==========================================
def manage_raw_stock(action, profile_type="", bars_count=0, bar_length=6.0, index_to_delete=None):
    if not os.path.exists(RAW_STOCK_FILE):
        df_init = pd.DataFrame(columns=["التاريخ", "النوع / النظام", "عدد البارات", "طول البار (م)", "إجمالي الأمتار (م)"])
        df_init.to_csv(RAW_STOCK_FILE, index=False, encoding="utf-8-sig")

    if action == "add":
        total_meters = bars_count * bar_length
        new_row = pd.DataFrame({
            "التاريخ": [dt.datetime.now().strftime("%Y-%m-%d %H:%M")],
            "النوع / النظام": [profile_type],
            "عدد البارات": [bars_count],
            "طول البار (م)": [bar_length],
            "إجمالي الأمتار (م)": [total_meters]
        })
        new_row.to_csv(RAW_STOCK_FILE, mode="a", header=False, index=False, encoding="utf-8-sig")
    
    elif action == "delete" and index_to_delete is not None:
        try:
            df = pd.read_csv(RAW_STOCK_FILE)
            if index_to_delete in df.index:
                df = df.drop(index_to_delete).reset_index(drop=True)
                df.to_csv(RAW_STOCK_FILE, index=False, encoding="utf-8-sig")
        except Exception:
            pass

    try:
        df = pd.read_csv(RAW_STOCK_FILE)
        return df
    except Exception:
        return pd.DataFrame(columns=["التاريخ", "النوع / النظام", "عدد البارات", "طول البار (م)", "إجمالي الأمتار (م)"])

# ==========================================
# 🗑️ دالة حذف سطر من ملف البقايا (Chutes)
# ==========================================
def delete_chute_row(index_to_delete):
    if os.path.exists(CHUTE_FILE):
        try:
            df = pd.read_csv(CHUTE_FILE)
            if index_to_delete in df.index:
                df = df.drop(index_to_delete).reset_index(drop=True)
                df.to_csv(CHUTE_FILE, index=False, encoding="utf-8-sig")
                return True
        except Exception:
            pass
    return False

# ==========================================
# 🔍 دالة فحص مخزون الشوط واستغلاله للورشة
# ==========================================
def check_workshop_chutes(req_cadre, req_ouvrant, req_parclose):
    if not os.path.exists(CHUTE_FILE):
        return 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, "لا توجد بقايا (Chutes) مسجلة في مخزون الورشة حالياً."
    
    try:
        df_chutes = pd.read_csv(CHUTE_FILE)
        total_cadre_stock = df_chutes["شوط الكادر (م)"].sum() if "شوط الكادر (م)" in df_chutes.columns else 0.0
        total_ouvrant_stock = df_chutes["شوط الضلف (م)"].sum() if "شوط الضلف (م)" in df_chutes.columns else 0.0
        total_parclose_stock = df_chutes["شوط الباركلوز (م)"].sum() if "شوط الباركلوز (م)" in df_chutes.columns else 0.0
    except Exception:
        return 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, "خطأ في قراءة ملف مخزون البقايا."

    cadre_from_stock = min(req_cadre, total_cadre_stock)
    ouvrant_from_stock = min(req_ouvrant, total_ouvrant_stock)
    parclose_from_stock = min(req_parclose, total_parclose_stock)

    msg = f"""
💡 تنبيه مخزون الورشة (Chutes Stock):
- الكادر: متوفر في الورشة {total_cadre_stock:.2f} م (سيتم استغلال: {cadre_from_stock:.2f} م)
- الضلف: متوفر في الورشة {total_ouvrant_stock:.2f} م (سيتم استغلال: {ouvrant_from_stock:.2f} م)
- الباركلوز: متوفر في الورشة {total_parclose_stock:.2f} م (سيتم استغلال: {parclose_from_stock:.2f} م)
    """
    return cadre_from_stock, ouvrant_from_stock, parclose_from_stock, total_cadre_stock, total_ouvrant_stock, total_parclose_stock, msg

# ==========================================
# 📐 الدالة الدقيقة لحساب الأمتار، البارات، والشوط
# ==========================================
def calculate_detailed_project(
    opening_system, width_cm, height_cm, has_travars, profile_price_per_m_linear,
    include_glass, glass_price_per_m2, include_roller_shutter, roller_shutter_price_per_m2
):
    width_m = width_cm / 100.0
    height_m = height_cm / 100.0
    surface_m2 = width_m * height_m
    perimeter_m = (width_m + height_m) * 2.0
    sys_lower = opening_system.lower()
    
    bar_length = 6.0 if ("23000" in sys_lower or "42000" in sys_lower) else 6.5
    is_fix_only = "fix" in sys_lower

    if "23000" in sys_lower:
        cadre_m = perimeter_m
        ouvrant_h = height_m - 0.065
        ouvrant_w = (width_m + 0.06) / 2.0
        ouvrant_m = ((ouvrant_h * 2.0) + (ouvrant_w * 2.0)) * 2.0 + (has_travars * width_m)
        parclose_m = perimeter_m
    elif "42000" in sys_lower:
        cadre_m = perimeter_m * 1.1
        ouvrant_m = perimeter_m * 1.2
        parclose_m = perimeter_m
    elif is_fix_only:
        cadre_m = perimeter_m
        ouvrant_m = 0.0
        parclose_m = perimeter_m
    else:
        cadre_m = perimeter_m
        ouvrant_m = perimeter_m * 1.2
        parclose_m = perimeter_m

    c_stock, o_stock, p_stock, tot_c_stock, tot_o_stock, tot_p_stock, stock_msg = check_workshop_chutes(cadre_m, ouvrant_m, parclose_m)

    net_cadre_m = max(0.0, cadre_m - c_stock)
    net_ouvrant_m = max(0.0, ouvrant_m - o_stock)
    net_parclose_m = max(0.0, parclose_m - p_stock)

    cadre_bars = int(net_cadre_m // bar_length) + (1 if (net_cadre_m % bar_length) > 0 else 0) if net_cadre_m > 0 else 0
    cadre_chute = (cadre_bars * bar_length) - net_cadre_m if cadre_bars > 0 else 0.0

    if is_fix_only:
        ouvrant_bars = 0
        ouvrant_chute = 0.0
    else:
        ouvrant_bars = int(net_ouvrant_m // bar_length) + (1 if (net_ouvrant_m % bar_length) > 0 else 0) if net_ouvrant_m > 0 else 0
        ouvrant_chute = (ouvrant_bars * bar_length) - net_ouvrant_m if ouvrant_bars > 0 else 0.0

    parclose_bars = int(net_parclose_m // bar_length) + (1 if (net_parclose_m % bar_length) > 0 else 0) if net_parclose_m > 0 else 0
    parclose_chute = (parclose_bars * bar_length) - net_parclose_m if parclose_bars > 0 else 0.0

    total_bars_needed = cadre_bars + ouvrant_bars + parclose_bars
    total_linear_meters = float(cadre_m + ouvrant_m + parclose_m + (has_travars * width_m))
    
    aluminum_cost = total_linear_meters * profile_price_per_m_linear
    glass_cost = surface_m2 * glass_price_per_m2 if include_glass else 0.0
    roller_shutter_cost = surface_m2 * roller_shutter_price_per_m2 if include_roller_shutter else 0.0

    total_base_cost = aluminum_cost + glass_cost + roller_shutter_cost
    return (
        total_linear_meters, surface_m2, aluminum_cost, glass_cost, roller_shutter_cost, 
        total_base_cost, cadre_m, ouvrant_m, parclose_m, cadre_bars, ouvrant_bars, 
        parclose_bars, cadre_chute, ouvrant_chute, parclose_chute, total_bars_needed, bar_length, is_fix_only,
        c_stock, o_stock, p_stock, stock_msg
    )

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

# ==========================================
# 📄 دوال طباعة الـ Devis و الـ Bon
# ==========================================
def generate_bon_de_livraison_html(client_name, client_phone, opening_system, width, height, surface_m2, final_total_cost):
    date_str = dt.datetime.now().strftime("%Y-%m-%d %H:%M")
    return f"""
    <!DOCTYPE html>
    <html dir="rtl" lang="ar">
    <head><meta charset="UTF-8"><title>وصل تسليم</title>
    <style>body {{ font-family: Arial, sans-serif; text-align: right; padding: 20px; }} .box {{ max-width: 800px; margin: auto; padding: 30px; border: 1px solid #ddd; border-radius: 10px; }} th, td {{ border: 1px solid #ddd; padding: 12px; }} th {{ background-color: #1f4e79; color: white; }}</style>
    </head>
    <body><div class="box">
        <h2>وصل تسليم طلبية (Bon de Livraison)</h2>
        <p><b>الزبون:</b> {client_name} | <b>الهاتف:</b> {client_phone} | <b>التاريخ:</b> {date_str}</p>
        <table width="100%" style="border-collapse: collapse;">
            <tr><th>النظام</th><th>الأبعاد</th><th>المساحة</th></tr>
            <tr><td>{opening_system}</td><td>{width:.0f} × {height:.0f} سم</td><td>{surface_m2:.2f} م²</td></tr>
        </table>
        <h3>المجموع الكلي: {final_total_cost:,.2f} دج</h3>
    </div><script>window.onload = function() {{ window.print(); }}</script></body></html>
    """

def generate_devis_html(client_name, client_phone, opening_system, width, height, surface_m2, final_total_cost):
    date_str = dt.datetime.now().strftime("%Y-%m-%d %H:%M")
    return f"""
    <!DOCTYPE html>
    <html dir="rtl" lang="ar">
    <head><meta charset="UTF-8"><title>عرض سعر</title>
    <style>body {{ font-family: Arial, sans-serif; text-align: right; padding: 20px; }} .box {{ max-width: 800px; margin: auto; padding: 30px; border: 1px solid #ddd; border-radius: 10px; }} th, td {{ border: 1px solid #ddd; padding: 12px; }} th {{ background-color: #28a745; color: white; }}</style>
    </head>
    <body><div class="box">
        <h2>عرض سعر (Devis)</h2>
        <p><b>الزبون:</b> {client_name} | <b>الهاتف:</b> {client_phone} | <b>التاريخ:</b> {date_str}</p>
        <table width="100%" style="border-collapse: collapse;">
            <tr><th>النظام</th><th>الأبعاد</th><th>المساحة</th></tr>
            <tr><td>{opening_system}</td><td>{width:.0f} × {height:.0f} سم</td><td>{surface_m2:.2f} م²</td></tr>
        </table>
        <h3>مبلغ عرض السعر: {final_total_cost:,.2f} دج</h3>
    </div><script>window.onload = function() {{ window.print(); }}</script></body></html>
    """

st.set_page_config(page_title="AluBL Calculator", page_icon="🪟", layout="centered")

st.markdown("""
<style>
    .stApp { direction: rtl; text-align: right; }
    label, .stSelectbox, .stTextInput, .stNumberInput { direction: rtl; text-align: right; }
</style>
""", unsafe_allow_html=True)

logo_path = os.path.join(os.path.dirname(__file__), "logo.jpg")
if os.path.exists(logo_path):
    with open(logo_path, "rb") as image_file:
        encoded_logo = base64.b64encode(image_file.read()).decode("utf-8")
    st.markdown(f"""
        <div style="display:flex; justify-content:center; margin-bottom:20px;">
            <img src="data:image/jpeg;base64,{encoded_logo}" alt="Logo" style="width:120px; height:120px; border-radius:50%; object-fit:cover; border:3px solid #f0f0f0;" />
        </div>
    """, unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center; color: #1f4e79;'>🪟 AluBL Calculator - حاسبة الورشة والمخزون</h1>", unsafe_allow_html=True)

# 🔄 القائمة الجانبية المحدثة
menu_choice = st.sidebar.selectbox(
    "الوضع الأساسي", 
    [
        "📄 إنشاء وطباعة Devis (عرض سعر للزبون)", 
        "📊 أرشيف وإحصائيات الـ Devis", 
        "🪟 حساب مشروع الورشة والقص (Chutes & Profils)", 
        "📦 إدخال وإدارة المخزون الجديد (Stock Initial)", 
        "🗂️ أرشيف وصلات التسليم (Bons)"
    ]
)

# =========================================================================
# 1️⃣ صفحة إنشاء وطباعة Devis وحفظه في الأرشيف
# =========================================================================
if menu_choice == "📄 إنشاء وطباعة Devis (عرض سعر للزبون)":
    st.markdown("---")
    st.markdown("<h3 style='color: #28a745;'>📄 قسم إعداد وطباعة وحفظ عرض السعر (Devis)</h3>", unsafe_allow_html=True)
    
    col_d1, col_d2 = st.columns(2)
    with col_d1:
        client_name = st.text_input("اسم الزبون", "محمد", key="devis_name")
        client_phone = st.text_input("رقم الهاتف", "0500000000", key="devis_phone")
        opening_system = st.selectbox(
            "نظام الفتح والأنظمة",
            ["Série 23000 (Coulissant)", "Série 42000 (Française)", "Cloison TPR", "Port Blcon", "Coulison", "Fnêtr", "Fix", "3 Rai", "4 Rai"],
            key="devis_sys"
        )
    with col_d2:
        width = st.number_input("العرض الكلي (سم)", min_value=10.0, value=100.0, step=1.0, key="devis_w")
        height = st.number_input("الارتفاع الكلي (سم)", min_value=10.0, value=100.0, step=1.0, key="devis_h")
        profile_options = {"23000 (Économique)": 4500.0, "42000 (Classique)": 5200.0, "TPR": 1500.0, "BB77": 7500.0}
        selected_profile = st.selectbox("نوع البروفيل", list(profile_options.keys()), key="devis_prof")
        profile_price = st.number_input("سعر المتر الخطي (دج)", min_value=0.0, value=float(profile_options.get(selected_profile, 5000.0)), step=100.0, key="devis_pp")

    include_glass = st.checkbox("إضافة الزجاج في الـ Devis", value=False, key="devis_glas_chk")
    glass_price = st.number_input("سعر الزجاج للمتر المربع (دج)", min_value=0.0, value=7500.0, key="devis_glas_p") if include_glass else 0.0

    include_roller_shutter = st.checkbox("إضافة volet roulant في الـ Devis", value=False, key="devis_v_chk")
    roller_shutter_price = st.number_input("سعر volet roulant للمتر المربع (دج)", min_value=0.0, value=10000.0, key="devis_v_p") if include_roller_shutter else 0.0

    margin_mode = st.selectbox("نوع المارجن / الفائدة", ["Montant fixe (DA)", "Pourcentage (%)"], key="devis_m_mode")
    margin_value = st.number_input("قيمة المارجن", min_value=0.0, value=0.0, step=100.0, key="devis_m_val")

    width_m = width / 100.0
    height_m = height / 100.0
    surface_m2 = width_m * height_m
    perimeter_m = (width_m + height_m) * 2.0
    
    sys_l_d = opening_system.lower()
    lin_m = perimeter_m * 1.8 if "23000" in sys_l_d else (perimeter_m * 2.2 if "42000" in sys_l_d else perimeter_m * 1.5)

    dev_alu_cost = lin_m * profile_price
    dev_glass_cost = surface_m2 * glass_price if include_glass else 0.0
    dev_v_cost = surface_m2 * roller_shutter_price if include_roller_shutter else 0.0
    dev_base_total = dev_alu_cost + dev_glass_cost + dev_v_cost
    
    dev_margin_amt = margin_value if margin_mode == "Montant fixe (DA)" else dev_base_total * (margin_value / 100.0)
    dev_final_total = dev_base_total + dev_margin_amt

    st.markdown(f"<div style='background-color: #d4edda; padding: 15px; border-radius: 8px; color: #155724; font-size: 18px; font-weight: bold; text-align: center; margin-top: 15px;'>مبلغ عرض السعر الإجمالي للزبون: {dev_final_total:,.2f} دج</div>", unsafe_allow_html=True)

    devis_html_content = generate_devis_html(client_name, client_phone, opening_system, width, height, surface_m2, dev_final_total)

    col_btn1, col_btn2, col_btn3 = st.columns(3)
    with col_btn1:
        if st.button("💾 حفظ Devis في الأرشيف"):
            devis_record = {
                "التاريخ": dt.datetime.now().strftime("%Y-%m-%d %H:%M"),
                "اسم الزبون": client_name,
                "رقم الهاتف": client_phone,
                "النظام": opening_system,
                "المقاسات (سم)": f"{width:.0f}x{height:.0f}",
                "المبلغ (دج)": dev_final_total,
                "الحالة": "En attente (قيد الانتظار)"
            }
            manage_devis_archive("add", data_dict=devis_record)
            st.success("✅ تم حفظ الـ Devis في الأرشيف بنجاح!")
    with col_btn2:
        if st.button("🖨️ طباعة Devis"):
            components.html(devis_html_content, height=600, scrolling=True)
    with col_btn3:
        st.download_button(
            label="💾 تحميل HTML",
            data=devis_html_content,
            file_name=f"Devis_{client_name}.html",
            mime="text/html"
        )

# =========================================================================
# 2️⃣ أرشيف وإحصائيات الـ Devis (مع تتبع الحالة Valide / Non valide)
# =========================================================================
elif menu_choice == "📊 أرشيف وإحصائيات الـ Devis":
    st.markdown("---")
    st.markdown("<h3 style='color: #1f4e79;'>📊 أرشيف الـ Devis ومتابعة حالة العمل (Valide / Non Valide)</h3>", unsafe_allow_html=True)
    
    df_devis = manage_devis_archive("get")
    if not df_devis.empty:
        # إحصائيات سريعة حسب اليوم
        df_devis["اليوم"] = pd.to_datetime(df_devis["التاريخ"]).dt.strftime("%Y-%m-%d")
        selected_date = st.selectbox("اختر اليوم لعرض ملخص الـ Devis المنجزة فيه", options=df_devis["اليوم"].unique())
        
        df_filtered_day = df_devis[df_devis["اليوم"] == selected_date]
        total_devis_day = len(df_filtered_day)
        total_amount_day = df_filtered_day["المبلغ (دج)"].sum()
        
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            st.metric(f"عدد الـ Devis في يوم {selected_date}", f"{total_devis_day} Devis")
        with col_s2:
            st.metric(f"المجموع المالي للـ Devis في اليوم", f"{total_amount_day:,.2f} دج")

        st.markdown("---")
        st.markdown("<h4 style='color: #1f4e79;'>📋 تفاصيل وتغيير حالة الـ Devis (الخدمة Valide / Non Valide)</h4>", unsafe_allow_html=True)
        st.dataframe(df_devis, use_container_width=True)

        col_u1, col_u2, col_u3 = st.columns(3)
        with col_u1:
            row_idx = st.number_input("رقم السطر (Index) للـ Devis", min_value=0, max_value=max(0, len(df_devis)-1), step=1)
        with col_u2:
            new_status = st.selectbox("اختر الحالة الجديدة", ["✅ Validé (خدمناه)", "❌ Non validé (مخدمناهش)", "⏳ En attente (قيد الانتظار)"])
        with col_u3:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🔄 تحديث حالة الـ Devis"):
                manage_devis_archive("update_status", index_to_update=row_idx, new_status=new_status)
                st.success("✅ تم تحديث حالة الـ Devis بنجاح!")
                st.rerun()

        st.markdown("---")
        del_idx = st.number_input("رقم السطر (Index) للحذف النهائي", min_value=0, max_value=max(0, len(df_devis)-1), step=1, key="del_d")
        if st.button("🗑️ حذف هذا الـ Devis من الأرشيف"):
            manage_devis_archive("delete", index_to_delete=del_idx)
            st.success("تم الحذف بنجاح!")
            st.rerun()
    else:
        st.info("لا يوجد أي Devis مسجل في الأرشيف حالياً.")

# =========================================================================
# 3️⃣ حساب مشروع الورشة والقص (Chutes & Profils)
# =========================================================================
elif menu_choice == "🪟 حساب مشروع الورشة والقص (Chutes & Profils)":
    st.markdown("---")
    st.markdown("<h3 style='color: #1f4e79;'>🪟 حساب تفاصيل الورشة، استغلال الشوط، ومخططات القص</h3>", unsafe_allow_html=True)
    
    client_name = st.sidebar.text_input("اسم الزبون للمشروع", "محمد")
    client_phone = st.sidebar.text_input("رقم الهاتف", "0500000000")
    opening_system = st.sidebar.selectbox("نظام الفتح والأنظمة", ["Série 23000 (Coulissant)", "Série 42000 (Française)", "Cloison TPR", "Port Blcon", "Coulison", "Fnêtr", "Fix", "3 Rai", "4 Rai"])
    has_travars = st.sidebar.number_input("عدد الترافارسات (Travars)", min_value=0, value=0, step=1)
    
    profile_options = {"23000 (Économique)": 4500.0, "42000 (Classique)": 5200.0, "TPR": 1500.0, "BB77": 7500.0}
    selected_profile = st.sidebar.selectbox("نوع البروفيل", list(profile_options.keys()))
    aluminum_price_per_m_linear = st.sidebar.number_input("سعر المتر الخطي (دج)", min_value=0.0, value=float(profile_options.get(selected_profile, 5000.0)), step=100.0)

    st.sidebar.header("الأبعاد الأساسية (سم)")
    width = st.sidebar.number_input("العرض الكلي (سم)", min_value=10.0, value=100.0, step=1.0)
    height = st.sidebar.number_input("الارتفاع الكلي (سم)", min_value=10.0, value=100.0, step=1.0)

    include_glass = st.sidebar.checkbox("إضافة الزجاج", value=False)
    glass_price = st.sidebar.number_input("سعر الزجاج للمتر المربع (دج)", min_value=0.0, value=7500.0) if include_glass else 0.0

    include_roller_shutter = st.sidebar.checkbox("إضافة volet roulant", value=False)
    roller_shutter_price = st.sidebar.number_input("سعر volet roulant للمتر المربع (دج)", min_value=0.0, value=10000.0) if include_roller_shutter else 0.0

    margin_mode = st.sidebar.selectbox("نوع المارجن", ["Montant fixe (DA)", "Pourcentage (%)"])
    margin_value = st.sidebar.number_input("قيمة المارجن", min_value=0.0, value=0.0, step=100.0)

    components.html(render_window_visual(width, height, opening_system), height=255)

    (
        total_linear_meters, surface_m2, aluminum_cost, glass_cost, roller_shutter_cost, 
        base_total_cost, cadre_m, ouvrant_m, parclose_m, cadre_bars, ouvrant_bars, 
        parclose_bars, cadre_chute, ouvrant_chute, parclose_chute, total_bars_needed, bar_length, is_fix_only,
        c_stock, o_stock, p_stock, stock_msg
    ) = calculate_detailed_project(
        opening_system, width, height, has_travars, aluminum_price_per_m_linear, include_glass, glass_price, include_roller_shutter, roller_shutter_price
    )

    st.markdown("---")
    st.info(stock_msg)

    margin_amount = margin_value if margin_mode == "Montant fixe (DA)" else base_total_cost * (margin_value / 100.0)
    final_total_cost = base_total_cost + margin_amount

    st.markdown(f"<div style='background-color: #d4edda; padding: 15px; border-radius: 8px; color: #155724; font-size: 18px; font-weight: bold; text-align: center;'>المجموع الكلي للمشروع: {final_total_cost:,.2f} دج</div>", unsafe_allow_html=True)

    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("✅ تأكيد الإنجاز ودخول الورشة (Commander & Update Stock)"):
            chute_data = {
                "التاريخ": [dt.datetime.now().strftime("%Y-%m-%d %H:%M")],
                "الزبون": [client_name],
                "النظام": [opening_system],
                "شوط الكادر (م)": [round(cadre_chute, 2)],
                "شوط الضلف (م)": [round(ouvrant_chute, 2)],
                "شوط الباركلوز (م)": [round(parclose_chute, 2)]
            }
            pd.DataFrame(chute_data).to_csv(CHUTE_FILE, mode="a", header=not os.path.exists(CHUTE_FILE), index=False, encoding="utf-8-sig")
            st.success("✅ تم تأكيد الطلبية بنجاح وتحديث الشوط!")

    with col_btn2:
        if st.button("🖨️ طباعة وصل تسليم الطلبية (Bon de Livraison)"):
            bl_html = generate_bon_de_livraison_html(client_name, client_phone, opening_system, width, height, surface_m2, final_total_cost)
            pd.DataFrame({
                "التاريخ": [dt.datetime.now().strftime("%Y-%m-%d %H:%M")],
                "الزبون": [client_name],
                "الهاتف": [client_phone],
                "النظام": [opening_system],
                "المقاسات": [f"{width:.0f}x{height:.0f}cm"],
                "المبلغ الإجمالي (دج)": [final_total_cost]
            }).to_csv(BON_HISTORY_FILE, mode="a", header=not os.path.exists(BON_HISTORY_FILE), index=False, encoding="utf-8-sig")
            components.html(bl_html, height=600, scrolling=True)

# =========================================================================
# 4️⃣ إدخال وإدارة المخزون الجديد (Stock Initial)
# =========================================================================
elif menu_choice == "📦 إدخال وإدارة المخزون الجديد (Stock Initial)":
    st.markdown("---")
    st.markdown("<h3 style='color: #1f4e79;'>📦 إدخال بارات ألومنيوم جديدة للورشة (Stock Initial)</h3>", unsafe_allow_html=True)
    
    with st.form("stock_form"):
        stock_profile_type = st.selectbox("نوع النظام أو البروفيل", ["Série 23000", "Série 42000", "Cloison TPR", "BB77", "Fix"])
        stock_bars_count = st.number_input("عدد البارات الجديدة", min_value=1, value=10, step=1)
        stock_bar_length = st.number_input("طول البار الواحد (متر)", min_value=1.0, value=6.0, step=0.5)
        if st.form_submit_button("إضافة للمخزون 📥"):
            manage_raw_stock("add", stock_profile_type, stock_bars_count, stock_bar_length)
            st.success("تمت إضافة البارات بنجاح!")

    df_raw = manage_raw_stock("get")
    if not df_raw.empty:
        st.dataframe(df_raw, use_container_width=True)
        raw_del_index = st.number_input("رقم السطر للحذف", min_value=0, max_value=max(0, len(df_raw)-1), step=1, key="raw_del")
        if st.button("🗑️ حذف السطر من المخزون الخام"):
            manage_raw_stock("delete", index_to_delete=raw_del_index)
            st.success("تم الحذف بنجاح!")
            st.rerun()

# =========================================================================
# 5️⃣ أرشيف وصلات التسليم (Bons)
# =========================================================================
else:
    st.markdown("---")
    st.markdown("<h3 style='color: #1f4e79;'>🗂️ أرشيف وصلات التسليم (Bons de Livraison)</h3>", unsafe_allow_html=True)
    if os.path.exists(BON_HISTORY_FILE):
        df_bons = pd.read_csv(BON_HISTORY_FILE)
        if not df_bons.empty:
            st.dataframe(df_bons, use_container_width=True)
            st.download_button("📥 تحميل الأرشيف CSV", data=df_bons.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig"), file_name="Bons_Archive.csv", mime="text/csv")
        else:
            st.info("الأرشيف فارغ.")
    else:
        st.info("لا توجد وصلات تسليم مسجلة.")