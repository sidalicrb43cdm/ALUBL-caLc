import base64
import datetime as dt
import math
import os
import urllib.parse

import pandas as pd
import streamlit as st


def render_window_visual(
    width_cm,
    height_cm,
    opening_system,
    central_mode="Française",
    top_divisions=1,
    bottom_divisions=1,
    left_divisions=1,
    right_divisions=1,
):
    width_cm = max(float(width_cm), 1.0)
    height_cm = max(float(height_cm), 1.0)

    svg_width, svg_height = 380, 260
    padding = 24
    max_frame_w, max_frame_h = 250, 150
    scale = min(max_frame_w / width_cm, max_frame_h / height_cm)
    frame_w = width_cm * scale
    frame_h = height_cm * scale
    x = (svg_width - frame_w) / 2
    y = padding + 18

    if opening_system in {"Coulissant", "Coulissant (جرار)", "3 Rails"}:
        left_panel = (
            f"<rect x='{x + 10}' y='{y + 10}' width='{frame_w / 2 - 14}' height='{frame_h - 20}' rx='6' fill='#eef6ff' stroke='#2e6fe6' stroke-width='3' />"
        )
        right_panel = (
            f"<rect x='{x + frame_w / 2 + 4}' y='{y + 10}' width='{frame_w / 2 - 14}' height='{frame_h - 20}' rx='6' fill='#eef6ff' stroke='#2e6fe6' stroke-width='3' />"
        )
        arrows = (
            f"<line x1='{x + 16}' y1='{y + frame_h / 2}' x2='{x + frame_w - 16}' y2='{y + frame_h / 2}' stroke='#1f4e79' stroke-width='3' />"
            f"<path d='M {x + frame_w - 28} {y + frame_h / 2 - 8} L {x + frame_w - 12} {y + frame_h / 2} L {x + frame_w - 28} {y + frame_h / 2 + 8}' fill='none' stroke='#1f4e79' stroke-width='3' />"
            f"<path d='M {x + 28} {y + frame_h / 2 + 8} L {x + 12} {y + frame_h / 2} L {x + 28} {y + frame_h / 2 - 8}' fill='none' stroke='#1f4e79' stroke-width='3' />"
        )
        content = f"{left_panel}{right_panel}{arrows}"
    elif opening_system in {"Ouvrant 1 vantail", "Française (فتح عادي)"}:
        panel = f"<rect x='{x + 10}' y='{y + 10}' width='{frame_w - 20}' height='{frame_h - 20}' rx='8' fill='#f7fbff' stroke='#1f4e79' stroke-width='4' />"
        marker = f"<line x1='{x + frame_w / 2}' y1='{y + 12}' x2='{x + frame_w / 2}' y2='{y + frame_h - 12}' stroke='#1f4e79' stroke-width='3' />"
        handle = f"<circle cx='{x + frame_w / 2 + 18}' cy='{y + frame_h / 2}' r='5' fill='#2e6fe6' />"
        content = f"{panel}{marker}{handle}"
    elif opening_system == "Ouvrant 2 vantaux":
        left_panel = f"<rect x='{x + 10}' y='{y + 10}' width='{(frame_w - 24) / 2}' height='{frame_h - 20}' rx='8' fill='#f7fbff' stroke='#1f4e79' stroke-width='4' />"
        right_panel = f"<rect x='{x + frame_w / 2 + 4}' y='{y + 10}' width='{(frame_w - 24) / 2}' height='{frame_h - 20}' rx='8' fill='#f7fbff' stroke='#1f4e79' stroke-width='4' />"
        divider = f"<line x1='{x + frame_w / 2}' y1='{y + 12}' x2='{x + frame_w / 2}' y2='{y + frame_h - 12}' stroke='#1f4e79' stroke-width='3' />"
        content = f"{left_panel}{right_panel}{divider}"
    elif opening_system == "Soufflet":
        panel = f"<rect x='{x + 10}' y='{y + 10}' width='{frame_w - 20}' height='{frame_h - 20}' rx='8' fill='#f7fbff' stroke='#1f4e79' stroke-width='4' />"
        diagonal = f"<line x1='{x + 16}' y1='{y + frame_h - 16}' x2='{x + frame_w - 16}' y2='{y + 16}' stroke='#2e6fe6' stroke-width='3' />"
        arrows = f"<path d='M {x + frame_w - 30} {y + 20} L {x + frame_w - 12} {y + 14} L {x + frame_w - 24} {y + 36}' fill='none' stroke='#1f4e79' stroke-width='2.5' />"
        content = f"{panel}{diagonal}{arrows}"
    elif opening_system == "Porte-fenêtre":
        panel = f"<rect x='{x + 10}' y='{y + 10}' width='{frame_w - 20}' height='{frame_h - 20}' rx='10' fill='#f7fbff' stroke='#1f4e79' stroke-width='4' />"
        handle = f"<circle cx='{x + frame_w / 2 + 24}' cy='{y + frame_h / 2}' r='5' fill='#2e6fe6' />"
        content = f"{panel}{handle}"
    elif opening_system == "Combiné (Centre + Fixes)":
        central_x, central_y = 92, 68
        central_w, central_h = 196, 124
        top_y, bottom_y = 24, 212
        left_x, right_x = 28, 328
        top_panel_h, bottom_panel_h = 36, 36
        left_panel_w, right_panel_w = 52, 52

        fixed_style = "fill='#eaf4ff' stroke='#1f4e79' stroke-width='2'"
        divider_style = "stroke='#6d92b7' stroke-width='1.5'"

        top_panel = f"<rect x='{central_x}' y='{top_y}' width='{central_w}' height='{top_panel_h}' rx='6' {fixed_style} />"
        bottom_panel = f"<rect x='{central_x}' y='{bottom_y}' width='{central_w}' height='{bottom_panel_h}' rx='6' {fixed_style} />"
        left_panel = f"<rect x='{left_x}' y='{central_y}' width='{left_panel_w}' height='{central_h}' rx='6' {fixed_style} />"
        right_panel = f"<rect x='{right_x}' y='{central_y}' width='{right_panel_w}' height='{central_h}' rx='6' {fixed_style} />"

        def make_divisions(panel_x, panel_y, panel_w, panel_h, count, vertical):
            if count <= 1:
                return ""
            if vertical:
                gap = max(2.0, (panel_h - 8) / count)
                parts = []
                for i in range(count):
                    seg_y = panel_y + 4 + i * gap
                    seg_h = max(6.0, gap - 2)
                    parts.append(
                        f"<rect x='{panel_x + 4}' y='{seg_y:.1f}' width='{panel_w - 8}' height='{seg_h:.1f}' rx='3' fill='#dcecff' stroke='#6d92b7' stroke-width='1' />"
                    )
                return "".join(parts)
            gap = max(2.0, (panel_w - 8) / count)
            parts = []
            for i in range(count):
                seg_x = panel_x + 4 + i * gap
                seg_w = max(6.0, gap - 2)
                parts.append(
                    f"<rect x='{seg_x:.1f}' y='{panel_y + 4}' width='{seg_w:.1f}' height='{panel_h - 8}' rx='3' fill='#dcecff' stroke='#6d92b7' stroke-width='1' />"
                )
            return "".join(parts)

        top_divisions_svg = make_divisions(central_x, top_y, central_w, top_panel_h, top_divisions, False)
        bottom_divisions_svg = make_divisions(central_x, bottom_y, central_w, bottom_panel_h, bottom_divisions, False)
        left_divisions_svg = make_divisions(left_x, central_y, left_panel_w, central_h, left_divisions, True)
        right_divisions_svg = make_divisions(right_x, central_y, right_panel_w, central_h, right_divisions, True)

        central_frame = f"<rect x='{central_x + 12}' y='{central_y + 10}' width='{central_w - 24}' height='{central_h - 20}' rx='8' fill='#f9fcff' stroke='#2e6fe6' stroke-width='3' />"
        if central_mode == "Coulissant":
            central_content = (
                f"<rect x='{central_x + 30}' y='{central_y + 24}' width='{(central_w - 60) / 2 - 4}' height='{central_h - 48}' rx='6' fill='#eef6ff' stroke='#2e6fe6' stroke-width='2.5' />"
                f"<rect x='{central_x + central_w / 2 + 4}' y='{central_y + 24}' width='{(central_w - 60) / 2 - 4}' height='{central_h - 48}' rx='6' fill='#eef6ff' stroke='#2e6fe6' stroke-width='2.5' />"
                f"<line x1='{central_x + central_w / 2}' y1='{central_y + 24}' x2='{central_x + central_w / 2}' y2='{central_y + central_h - 24}' stroke='#1f4e79' stroke-width='2.5' />"
                f"<path d='M {central_x + central_w - 34} {central_y + central_h / 2 - 7} L {central_x + central_w - 18} {central_y + central_h / 2} L {central_x + central_w - 34} {central_y + central_h / 2 + 7}' fill='none' stroke='#1f4e79' stroke-width='2.5' />"
                f"<path d='M {central_x + 34} {central_y + central_h / 2 + 7} L {central_x + 18} {central_y + central_h / 2} L {central_x + 34} {central_y + central_h / 2 - 7}' fill='none' stroke='#1f4e79' stroke-width='2.5' />"
            )
        else:
            central_content = (
                f"<line x1='{central_x + 28}' y1='{central_y + 24}' x2='{central_x + central_w - 28}' y2='{central_y + central_h - 24}' stroke='#2e6fe6' stroke-width='2.5' />"
                f"<line x1='{central_x + central_w - 28}' y1='{central_y + 24}' x2='{central_x + 28}' y2='{central_y + central_h - 24}' stroke='#2e6fe6' stroke-width='2.5' />"
                f"<text x='{central_x + central_w / 2}' y='{central_y + central_h / 2 + 8}' text-anchor='middle' font-size='24' font-family='Arial' font-weight='700' fill='#2e6fe6'>X</text>"
            )

        content = (
            f"{top_panel}{bottom_panel}{left_panel}{right_panel}"
            f"{top_divisions_svg}{bottom_divisions_svg}{left_divisions_svg}{right_divisions_svg}"
            f"{central_frame}{central_content}"
        )
    elif opening_system in {"Fixe (ثابت)", "Fix haut", "Fix bas", "Fix droite", "Fix gauche"}:
        if opening_system == "Fix haut":
            panel = f"<rect x='{x + 8}' y='{y + 8}' width='{frame_w - 16}' height='{frame_h - 16}' rx='8' fill='#f7fbff' stroke='#1f4e79' stroke-width='4' />"
            marker = f"<line x1='{x + frame_w / 2}' y1='{y + 10}' x2='{x + frame_w / 2}' y2='{y + frame_h - 10}' stroke='#1f4e79' stroke-width='3' />"
            label = f"<text x='{svg_width / 2}' y='{y + frame_h / 2 + 8}' text-anchor='middle' font-size='22' font-family='Arial' font-weight='700' fill='#1f4e79'>H</text>"
        elif opening_system == "Fix bas":
            panel = f"<rect x='{x + 8}' y='{y + 8}' width='{frame_w - 16}' height='{frame_h - 16}' rx='8' fill='#f7fbff' stroke='#1f4e79' stroke-width='4' />"
            marker = f"<line x1='{x + frame_w / 2}' y1='{y + 10}' x2='{x + frame_w / 2}' y2='{y + frame_h - 10}' stroke='#1f4e79' stroke-width='3' />"
            label = f"<text x='{svg_width / 2}' y='{y + frame_h / 2 + 8}' text-anchor='middle' font-size='22' font-family='Arial' font-weight='700' fill='#1f4e79'>B</text>"
        elif opening_system == "Fix droite":
            panel = f"<rect x='{x + 8}' y='{y + 8}' width='{frame_w - 16}' height='{frame_h - 16}' rx='8' fill='#f7fbff' stroke='#1f4e79' stroke-width='4' />"
            marker = f"<line x1='{x + 10}' y1='{y + frame_h / 2}' x2='{x + frame_w - 10}' y2='{y + frame_h / 2}' stroke='#1f4e79' stroke-width='3' />"
            label = f"<text x='{svg_width / 2}' y='{y + frame_h / 2 + 8}' text-anchor='middle' font-size='22' font-family='Arial' font-weight='700' fill='#1f4e79'>R</text>"
        elif opening_system == "Fix gauche":
            panel = f"<rect x='{x + 8}' y='{y + 8}' width='{frame_w - 16}' height='{frame_h - 16}' rx='8' fill='#f7fbff' stroke='#1f4e79' stroke-width='4' />"
            marker = f"<line x1='{x + 10}' y1='{y + frame_h / 2}' x2='{x + frame_w - 10}' y2='{y + frame_h / 2}' stroke='#1f4e79' stroke-width='3' />"
            label = f"<text x='{svg_width / 2}' y='{y + frame_h / 2 + 8}' text-anchor='middle' font-size='22' font-family='Arial' font-weight='700' fill='#1f4e79'>L</text>"
        else:
            panel = f"<rect x='{x + 8}' y='{y + 8}' width='{frame_w - 16}' height='{frame_h - 16}' rx='8' fill='#f7fbff' stroke='#1f4e79' stroke-width='4' />"
            marker = ""
            label = f"<text x='{svg_width / 2}' y='{y + frame_h / 2 + 8}' text-anchor='middle' font-size='28' font-family='Arial' font-weight='700' fill='#1f4e79'>FX</text>"
        content = f"{panel}{marker}{label}"
    else:
        content = (
            f"<rect x='{x + 8}' y='{y + 8}' width='{frame_w - 16}' height='{frame_h - 16}' rx='8' fill='#f9fcff' stroke='#2e6fe6' stroke-width='3' />"
            f"<line x1='{x + 20}' y1='{y + 20}' x2='{x + frame_w - 20}' y2='{y + frame_h - 20}' stroke='#2e6fe6' stroke-width='3' />"
            f"<line x1='{x + frame_w - 20}' y1='{y + 20}' x2='{x + 20}' y2='{y + frame_h - 20}' stroke='#2e6fe6' stroke-width='3' />"
            f"<text x='{svg_width / 2}' y='{y + frame_h / 2 + 8}' text-anchor='middle' font-size='30' font-family='Arial' font-weight='700' fill='#2e6fe6'>X</text>"
        )

    svg = f"""
    <svg width="{svg_width}" height="{svg_height}" viewBox="0 0 {svg_width} {svg_height}" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Window preview">
        <rect width="100%" height="100%" fill="#ffffff" rx="14" />
        <rect x="18" y="16" width="344" height="228" rx="14" fill="#f5f9fd" stroke="#dce7f2" stroke-width="2" />
        {content}
        <text x="{svg_width / 2}" y="240" text-anchor="middle" font-size="14" fill="#355c7d" font-family="Arial">{opening_system} • {width_cm:.0f} × {height_cm:.0f} cm</text>
    </svg>
    """
    return svg


st.set_page_config(
    page_title="AluBL Calculator - الورشة", page_icon="🪟", layout="centered"
)

logo_path = os.path.join(os.path.dirname(__file__), "logo.jpg")
if os.path.exists(logo_path):
    with open(logo_path, "rb") as image_file:
        encoded_logo = base64.b64encode(image_file.read()).decode("utf-8")

    st.markdown(
        f"""
        <div style="display:flex; justify-content:center; margin-bottom:20px;">
            <img src="data:image/jpeg;base64,{encoded_logo}" alt="Profile logo"
                 style="width:120px; height:120px; border-radius:50%; object-fit:cover; border:3px solid #f0f0f0;" />
        </div>
        """,
        unsafe_allow_html=True,
    )

st.title("🪟 AluBL Calculator - حاسبة الورشة للألومنيوم")

# إدخال بيانات الزبون والمشروع
st.sidebar.header("معلومات الزبون والمشروع")
client_name = st.sidebar.text_input("اسم الزبون", "محمد")
client_email = st.sidebar.text_input("رقم الهاتف أو البريد", "0500000000")

# نظام الفتح
opening_system = st.sidebar.selectbox(
    "نظام الفتح",
    [
        "Française (فتح عادي)",
        "Coulissant (جرار)",
        "Coulissant",
        "3 Rails",
        "Ouvrant 1 vantail",
        "Ouvrant 2 vantaux",
        "Soufflet",
        "Porte-fenêtre",
        "Fixe (ثابت)",
        "Fix haut",
        "Fix bas",
        "Fix droite",
        "Fix gauche",
        "Combiné (Centre + Fixes)",
    ],
)

leaf_count = st.sidebar.selectbox(
    "Nombre de vantaux",
    [1, 2, 3, 4],
    index=0,
)

composite_center_mode = "Française"
top_divisions = 1
bottom_divisions = 1
left_divisions = 1
right_divisions = 1

if opening_system == "Combiné (Centre + Fixes)":
    composite_center_mode = st.sidebar.selectbox(
        "نوع النافذة المركزية", ["Française", "Coulissant", "Fixe"]
    )
    st.sidebar.caption("اختيار عدد التقسيمات لكل جهة")
    top_divisions = st.sidebar.slider("تقسيمات أعلى", 1, 6, 1)
    bottom_divisions = st.sidebar.slider("تقسيمات أسفل", 1, 6, 1)
    left_divisions = st.sidebar.slider("تقسيمات يسار", 1, 6, 1)
    right_divisions = st.sidebar.slider("تقسيمات يمين", 1, 6, 1)

# اختيار نوع البروفيل والأسعار
profile_options = {
    "TPR": 5500.0,
    "SNPAN": 6300.0,
    "BB77": 7500.0,
    "Gammes Classiques": 4800.0,
}

selected_profile = st.sidebar.selectbox(
    "نوع البروفيل", list(profile_options.keys())
)
aluminum_price_per_m = st.sidebar.number_input(
    "سعر المتر (دج)",
    min_value=0.0,
    value=float(profile_options[selected_profile]),
    step=100.0,
)

# الأبعاد العامة
st.sidebar.header("الأبعاد الأساسية (بالسنتيمتر)")
width = st.sidebar.number_input(
    "العرض الكلي (سم)", min_value=10.0, value=120.0, step=1.0
)
height = st.sidebar.number_input(
    "الارتفاع الكلي (سم)", min_value=10.0, value=140.0, step=1.0
)
color = st.sidebar.selectbox(
    "لون الألومنيوم", ["Blanc", "Gris anthracite", "Noir", "Effet bois"]
)

include_glass = st.sidebar.checkbox("إضافة الزجاج", value=True)
include_roller_shutter = st.sidebar.checkbox("إضافة volet roulant", value=False)
include_joint = st.sidebar.checkbox("Avec Joint", value=True)

st.sidebar.header("الحاشية / المارجن")
margin_mode = st.sidebar.selectbox(
    "نوع المارجن",
    ["Montant fixe (DA)", "Pourcentage (%)"],
)
margin_value = st.sidebar.number_input(
    "قيمة المارجن",
    min_value=0.0,
    value=0.0,
    step=100.0,
)

st.subheader("🪟 معاينة الشكل")
st.markdown(
    f"<div style='display:flex; justify-content:center;'><div>{render_window_visual(width, height, opening_system, composite_center_mode, top_divisions, bottom_divisions, left_divisions, right_divisions)}</div></div>",
    unsafe_allow_html=True,
)
glass_price = (
    st.sidebar.number_input(
        "سعر الزجاج للمتر المربع (دج)", min_value=0.0, value=4500.0
    )
    if include_glass
    else 0.0
)
roller_shutter_price = (
    st.sidebar.number_input(
        "سعر volet roulant للمتر المربع (دج)", min_value=0.0, value=3000.0
    )
    if include_roller_shutter
    else 0.0
)

# --- قسم التحكم اليدوي في القياسات (Mode Manuel) ---
st.subheader("🛠️ حساب وتقطيع الألومنيوم (Débitage)")

# حسابات افتراضية دقيقة تناسب الورشة
col1, col2 = st.columns(2)

with col1:
  dormant_h = height
  dormant_w = width
  traverse_val = width - 10

  manual_dormant_h = st.number_input(
      "طول عمود الحلق (Dormant Vertical)", value=float(dormant_h), step=1.0
  )
  manual_dormant_w = st.number_input(
      "طول عرض الحلق (Dormant Horizontal)", value=float(dormant_w), step=1.0
  )
  manual_traverse = st.number_input(
      "طول العارضة الوسطى (Traverse)", value=float(traverse_val), step=1.0
  )

with col2:
  ouvrant_h = height - 6
  ouvrant_w = (width / 2) - 8

  manual_ouvrant_h = st.number_input(
      "طول القائم المتحرك (Ouvrant Montant)", value=float(ouvrant_h), step=1.0
  )
  manual_ouvrant_w = st.number_input(
      "طول الشباك المتحرك (Ouvrant Traverse)",
      value=float(ouvrant_w),
      step=1.0,
  )

# Définition des variables de type d'ouverture avant les calculs
opening_is_fixed = opening_system in {
    "Fixe (ثابت)",
    "Fix haut",
    "Fix bas",
    "Fix droite",
    "Fix gauche",
}
opening_is_sliding = opening_system in {"Coulissant", "Coulissant (جرار)", "3 Rails"} or (
    opening_system == "Combiné (Centre + Fixes)"
    and composite_center_mode == "Coulissant"
)

if opening_system == "3 Rails":
    rails_qty = 3
else:
    rails_qty = 2 if opening_is_sliding else 0

if opening_system in {"Ouvrant 1 vantail", "Française (فتح عادي)", "Soufflet", "Porte-fenêtre"}:
    leaf_count = max(1, min(leaf_count, 1))
elif opening_system in {"Ouvrant 2 vantaux"}:
    leaf_count = max(1, min(leaf_count, 2))
elif opening_system == "3 Rails":
    leaf_count = max(1, min(leaf_count, 3))
else:
    leaf_count = max(1, min(leaf_count, 4))

# الحسابات المالية
effective_width_m = width / 100.0
effective_height_m = height / 100.0
metre_lineaire = ((manual_dormant_h + manual_dormant_w) * 2) / 100.0
bar_length_m = 6.5
sliding_rails_length_m = (rails_qty * (width / 100.0)) if opening_is_sliding else 0.0
parclose_perimeter_m = ((width + height) * 2 / 100.0) + 0.4
parclose_length_m = max(0.0, parclose_perimeter_m)

hinge_count_per_leaf = 3 if height >= 180 else 2
hinges_needed = max(0, leaf_count * hinge_count_per_leaf)
aluminum_length_needed_m = metre_lineaire + sliding_rails_length_m
bars_needed = math.ceil(aluminum_length_needed_m / bar_length_m) if aluminum_length_needed_m > 0 else 0
bar_purchase_length_m = bars_needed * bar_length_m
bar_waste_m = max(0.0, bar_purchase_length_m - aluminum_length_needed_m)
aluminum_cost = aluminum_length_needed_m * aluminum_price_per_m
vitrage_price = (
    (effective_width_m * effective_height_m) * glass_price
    if include_glass
    else 0.0
)
roller_shutter_cost = (
    (effective_width_m * effective_height_m) * roller_shutter_price
    if include_roller_shutter
    else 0.0
)
base_total_cost = aluminum_cost + vitrage_price + roller_shutter_cost
if margin_mode == "Montant fixe (DA)":
    margin_amount = margin_value
else:
    margin_amount = base_total_cost * (margin_value / 100.0)
final_total_cost = base_total_cost + margin_amount
total_cost = final_total_cost

# عرض النتائج
st.subheader("📊 ملخص التكلفة")
info_text = (
    f"الزبون: {client_name}\n"
    f"البروفيل: {selected_profile} (سعر المتر: {aluminum_price_per_m:,.2f} دج)\n"
    f"النظام: {opening_system}\n"
    f"المتر الطولي الإجمالي: {metre_lineaire:.2f} م.ط\n"
    f"Longueur aluminium estimée: {aluminum_length_needed_m:.2f} m\n"
    f"Parclose estimée: {parclose_length_m:.2f} m\n"
    f"Paumelles nécessaires: {hinges_needed}\n"
    f"Barres d'aluminium nécessaires (6,5 m): {bars_needed} barre(s)\n"
    f"Longueur totale achetée: {bar_purchase_length_m:.2f} m | Déchet: {bar_waste_m:.2f} m\n"
    f"تكلفة الألومنيوم: {aluminum_cost:,.2f} دج"
)

if include_glass:
  info_text += f"\nتكلفة الزجاج: {vitrage_price:,.2f} دج"
else:
  info_text += "\nالزجاج: بدون زجاج"

if include_roller_shutter:
  info_text += f"\nتكلفة volet roulant: {roller_shutter_cost:,.2f} دج"
else:
  info_text += "\nالفتحة: بدون volet roulant"

if margin_mode == "Montant fixe (DA)":
  info_text += f"\nالمرجع / المارجن: {margin_value:,.2f} دج"
else:
  info_text += f"\nالمرجع / المارجن: {margin_value:.2f}%"

info_text += f"\nالمجموع قبل المارجن: {base_total_cost:,.2f} دج"
info_text += f"\nالسعر النهائي بعد المارجن: {final_total_cost:,.2f} دج"

st.info(info_text)
st.success(f"💰 **السعر النهائي بعد المارجن: {final_total_cost:,.2f} دج**")

# جدول القص
st.subheader("📜 جدول القص اليدوي (Carnet de débit)")
debit_data = {
    "Section": ["Dormant", "Dormant", "Ouvrant", "Ouvrant", "Traverse"],
    "Désignation": [
        "Pièce verticale",
        "Pièce horizontale",
        "Montant",
        "Traverse",
        "Traverse centrale",
    ],
    "Quantité": [2, 2, 2, 2, 1],
    "Longueur (cm)": [
        manual_dormant_h,
        manual_dormant_w,
        manual_ouvrant_h,
        manual_ouvrant_w,
        manual_traverse,
    ],
}
df_debit = pd.DataFrame(debit_data)
st.dataframe(df_debit, use_container_width=True)

# --- Liste d'achats des accessoires ---
st.subheader("🧰 Liste d'achats des accessoires")

opening_is_fixed = opening_system in {
    "Fixe (ثابت)",
    "Fix haut",
    "Fix bas",
    "Fix droite",
    "Fix gauche",
}
opening_is_sliding = opening_system in {"Coulissant", "Coulissant (جرار)", "3 Rails"} or (
    opening_system == "Combiné (Centre + Fixes)"
    and composite_center_mode == "Coulissant"
)

perimeter_m = (width + height) * 2 / 100.0
brackets_qty = max(4, math.ceil(perimeter_m * 2))
if opening_system in {"Ouvrant 2 vantaux", "Porte-fenêtre"}:
    handles_qty = 2
elif opening_system in {"Ouvrant 1 vantail", "Soufflet", "Française (فتح عادي)"}:
    handles_qty = 1
else:
    handles_qty = 0 if opening_is_fixed else (2 if width >= 100 else 1)

if opening_system == "3 Rails":
    rails_qty = 3
else:
    rails_qty = 2 if opening_is_sliding else 0

if opening_system in {"Ouvrant 1 vantail", "Française (فتح عادي)", "Soufflet", "Porte-fenêtre"}:
    leaf_count = max(1, min(leaf_count, 1))
elif opening_system in {"Ouvrant 2 vantaux"}:
    leaf_count = max(1, min(leaf_count, 2))
elif opening_system == "3 Rails":
    leaf_count = max(1, min(leaf_count, 3))
else:
    leaf_count = max(1, min(leaf_count, 4))

rollers_qty = 4 if opening_is_sliding else 0

accessory_rows = [
    {
        "Accessoire": "Équerres",
        "Quantité": brackets_qty,
        "Détail": f"Base calculée sur le périmètre ({perimeter_m:.2f} m)",
    },
    {
        "Accessoire": "Vantaux",
        "Quantité": leaf_count,
        "Détail": "Nombre de vantaux selon le type d'ouverture",
    },
    {
        "Accessoire": "Poignées",
        "Quantité": handles_qty,
        "Détail": "1 poignée par ouvrant, minimum 1",
    },
    {
        "Accessoire": "Parclose",
        "Quantité": max(1, math.ceil(parclose_length_m / 3.0)),
        "Détail": f"Longueur estimée : {parclose_length_m:.2f} m, à prévoir en profil / élément de finition",
    },
    {
        "Accessoire": "Paumelles",
        "Quantité": hinges_needed,
        "Détail": f"{hinge_count_per_leaf} paumelles par vantail selon la hauteur ({height:.0f} cm)",
    },
]

if opening_is_sliding:
    accessory_rows.append(
        {
            "Accessoire": "Rails de coulissement",
            "Quantité": rails_qty,
            "Détail": "Nombre de rails adapté au type de coulissant",
        }
    )
    accessory_rows.append(
        {
            "Accessoire": "Roulettes",
            "Quantité": rollers_qty,
            "Détail": "4 roulettes pour une baie coulissante",
        }
    )

if include_joint:
    joint_length_m = round(perimeter_m + 0.5, 2)
    joint_rolls_qty = max(1, math.ceil(joint_length_m / 3.0))
    accessory_rows.append(
        {
            "Accessoire": "Joints (rouleaux de 3 m)",
            "Quantité": joint_rolls_qty,
            "Détail": f"Longueur totale nécessaire : {joint_length_m:.2f} m",
        }
    )

accessory_df = pd.DataFrame(accessory_rows)
st.dataframe(accessory_df, use_container_width=True, hide_index=True)
st.caption("Calcul automatique basé sur les dimensions de la fenêtre et le système d'ouverture.")


# دالة التقرير
def build_project_report():
  report = f"""--- وصل طلب / فكرة مشروع - AluBL ---
التاريخ: {dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
اسم الزبون: {client_name}
الهاتف/البريد: {client_email}
----------------------------------------
البروفيل: {selected_profile} | السعر: {aluminum_price_per_m:,.2f} دج
نظام الفتح: {opening_system} | اللون: {color}
الابعاد: العرض {width} سم | الارتفاع: {height} سم
--- تفاصيل القص اليدوية ---
- Dormant Vertical: {manual_dormant_h} سم
- Dormant Horizontal: {manual_dormant_w} سم
- Ouvrant Montant: {manual_ouvrant_h} سم
- Ouvrant Traverse: {manual_ouvrant_w} سم
- Traverse: {manual_traverse} سم
- Longueur aluminium estimée: {aluminum_length_needed_m:.2f} m
- Parclose estimée: {parclose_length_m:.2f} m
- Paumelles nécessaires: {hinges_needed}
- Barres d'aluminium nécessaires (6,5 m): {bars_needed} barre(s)
- Longueur totale achetée: {bar_purchase_length_m:.2f} m | Déchet: {bar_waste_m:.2f} m
----------------------------------------
المجموع قبل المارجن: {base_total_cost:,.2f} دج
المرجع / المارجن: {margin_value:.2f} {'دج' if margin_mode == 'Montant fixe (DA)' else '%'}
المجموع النهائي بعد المارجن: {final_total_cost:,.2f} دج
----------------------------------------
AluBL Workshop - El Harrach
"""
  return report


report_data = build_project_report()
st.download_button(
    label="📥 تحميل ورقة الزبون والتقرير (Fiche/Bon)",
    data=report_data,
    file_name=f"AluBL_Bon_{client_name}.txt",
    mime="text/plain",
)

# حفظ السجل
history_file = "alubl_history.csv"
if st.button("💾 حفظ الطلبية في السجل (Historique)"):
  new_record = {
      "التاريخ": [dt.datetime.now().strftime("%Y-%m-%d %H:%M")],
      "الزبون": [client_name],
      "الهاتف": [client_email],
      "البروفيل": [selected_profile],
      "النظام": [opening_system],
      "العرض (سم)": [width],
      "الارتفاع (سم)": [height],
      "التكلفة (دج)": [total_cost],
  }
  df_new = pd.DataFrame(new_record)
  if os.path.exists(history_file):
    df_new.to_csv(
        history_file, mode="a", header=False, index=False, encoding="utf-8-sig"
    )
  else:
    df_new.to_csv(history_file, index=False, encoding="utf-8-sig")
  st.success("✅ تم حفظ الطلبية في السجل بنجاح!")

if os.path.exists(history_file):
  st.subheader("📂 سجل الطلبيات السابقة (Historique des Clients)")
  df_history = pd.read_csv(history_file, encoding="utf-8-sig")

  client_filter = st.text_input(
      "🔎 Filtrer par nom du client",
      placeholder="Saisir un nom pour afficher uniquement ses commandes",
  )

  if client_filter:
      filtered_history = df_history[
          df_history["الزبون"].astype(str).str.contains(client_filter, case=False, na=False)
      ]
  else:
      filtered_history = df_history

  if filtered_history.empty:
      st.warning("Aucune commande trouvée pour ce client.")
  else:
      total_filtered = (
          pd.to_numeric(filtered_history["التكلفة (دج)"], errors="coerce")
          .fillna(0)
          .sum()
      )
      col_a, col_b = st.columns(2)
      with col_a:
          st.metric("Nombre de commandes", len(filtered_history))
      with col_b:
          st.metric("Total des commandes filtrées (دج)", f"{total_filtered:,.2f}")
      st.dataframe(filtered_history, use_container_width=True)

      client_name_for_export = client_filter.strip() or "Tous les clients"
      export_lines = [
          "Devis Global du Client",
          f"Client: {client_name_for_export}",
          f"Nombre de commandes: {len(filtered_history)}",
          f"Total général: {total_filtered:,.2f} دج",
          "",
          "Détails des commandes:",
      ]
      for _, row in filtered_history.iterrows():
          export_lines.append(
              f"- {row['التاريخ']} | Client: {row['الزبون']} | Profil: {row['البروفيل']} | Système: {row['النظام']} | Coût: {row['التكلفة (دج)']:,.2f} دج"
          )

      st.download_button(
          label="📄 Télécharger le Devis Global du Client",
          data="\n".join(export_lines),
          file_name=f"Devis_{client_name_for_export.replace(' ', '_')}.txt",
          mime="text/plain",
      )

      whatsapp_message = (
          f"Bonjour {client_name_for_export},\n\n"
          f"Voici le résumé de vos commandes :\n"
          f"- Nombre de commandes : {len(filtered_history)}\n"
          f"- Montant total : {total_filtered:,.2f} دج\n\n"
          "Détails :\n"
          + "\n".join(
              f"• {row['التاريخ']} | {row['البروفيل']} | {row['النظام']} | {row['التكلفة (دج)']:,.2f} دج"
              for _, row in filtered_history.iterrows()
          )
      )

      whatsapp_url = (
          "https://wa.me/?text="
          + urllib.parse.quote(whatsapp_message)
      )

      st.link_button("💬 Envoyer sur WhatsApp", whatsapp_url)
      st.markdown("---")
st.subheader("📋 تفاصيل السلعة وجدول القص (Bon de Coupe)")
import pandas as pd
df_coupes = pd.DataFrame({
    "Piece": [
        "Dormant Largeur", 
        "Dormant Hauteur", 
        "Ouvrant Largeur", 
        "Ouvrant Hauteur"
    ],
    "Nombre": [2, 2, 2, 2],
    "Mesure_mm": [
        "Largeur - 50", 
        "Hauteur - 50", 
        "Sur Mesure", 
        "Sur Mesure"
    ],
})
st.dataframe(df_coupes, use_container_width=True)