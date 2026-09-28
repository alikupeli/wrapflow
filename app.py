import streamlit as st
import pandas as pd
import json
from datetime import datetime

# Sayfa Genişlik Ayarları (Mobil Uyumlu)
st.set_page_config(page_title="WrapFlow Proforma", page_icon="🚗", layout="wide")

# Kullanıcının Paylaştığı Orijinal JSON Veri Yapısı
INITIAL_DATA = {
  "appName": "WrapFlow Proforma Araç Kaplama & PPF",
  "version": "1.2.0",
  "invoice": {
    "invoiceNo": "PRF-2026-0042",
    "issueDate": "2026-09-28",
    "customer": {
      "name": "Ahmet Karadeniz",
      "company": "Karadeniz Lojistik Ltd.",
      "phone": "+90 (532) 456 78 90",
      "city": "İstanbul / Sarıyer"
    },
    "vehicle": {
      "plate": "34 PR 911",
      "brand": "Porsche",
      "model": "911 GT3 RS"
    }
  },
  "materials": [
    {"name": "SAĞ DİREK KAPLAMA", "tierPrices": {"CAST": 100}, "defaultPrice": 50, "id": "mat-1"},
    {"name": "MAVİ ŞERİT", "tierPrices": {"5500": 25, "TİP5": 150}, "defaultPrice": 50, "id": "mat-2"},
    {"name": "POLİS YAZI", "tierPrices": {"5500": 10, "TİP5": 35}, "defaultPrice": 50, "id": "mat-3"}
  ],
  "bodyParts": [
    {"id": "bp-hood", "name": "Ön Kaput", "category": "Ön Bölüm"},
    {"id": "bp-bumper", "name": "Ön Tampon", "category": "Ön Bölüm"},
    {"id": "bp-door-r", "name": "Sağ Ön Kapı", "category": "Yan Bölüm"},
    {"id": "bp-fender-l", "name": "Sol Ön Çamurluk", "category": "Ön Bölüm"}
  ],
  "materialTypes": ["5500", "TİP5", "CAST", "UV BASKI"],
  "exchangeRates": {"USD_TRY": 48.9485, "EUR_TRY": 55.7274}
}

# Session State ile Verileri Hafızada Tutma
if "invoice_items" not in st.session_state:
    st.session_state.invoice_items = []

# --- ARAYÜZ TASARIMI ---
st.title("🚗 WrapFlow Proforma - Canlı Test Ekranı")
st.caption("Veri yapısı entegre edildi. Şimdi tasarımı ve eksikleri canlı test edebiliriz.")

# Üst Bar - Özet Bilgiler
col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label="Müşteri", value=INITIAL_DATA["invoice"]["customer"]["name"])
with col2:
    st.metric(label="Araç", value=f"{INITIAL_DATA['invoice']['vehicle']['brand']} {INITIAL_DATA['invoice']['vehicle']['model']}")
with col3:
    st.metric(label="Dolar Kuru (USD/TRY)", value=f"{INITIAL_DATA['exchangeRates']['USD_TRY']} TL")

st.markdown("---")

# Dinamik Fatura Kalemi Ekleme Bölümü
st.subheader("🛠️ Parça ve Malzeme Seçim Alanı")

col_part, col_mat, col_type, col_qty = st.columns([2, 2, 2, 1])

with col_part:
    selected_part = st.selectbox("Uygulanacak Parça", [p["name"] for p in INITIAL_DATA["bodyParts"]])
with col_mat:
    selected_mat = st.selectbox("Malzeme / İşçilik", [m["name"] for m in INITIAL_DATA["materials"]])
with col_type:
    selected_type = st.selectbox("Malzeme Türü (Tier)", INITIAL_DATA["materialTypes"])
with col_qty:
    quantity = st.number_input("Adet", min_value=1, value=1)

if st.button("➕ Listeye Ekle", use_container_width=True):
    # Fiyat hesaplama mantığı (JSON'dan tierPrice çekme)
    mat_obj = next(m for m in INITIAL_DATA["materials"] if m["name"] == selected_mat)
    base_price_usd = mat_obj["tierPrices"].get(selected_type, mat_obj["defaultPrice"])
    
    # Eğer fiyat 0 girildiyse varsayılan fiyatı al
    if base_price_usd == 0:
        base_price_usd = mat_obj["defaultPrice"]
        
    price_try = base_price_usd * INITIAL_DATA["exchangeRates"]["USD_TRY"]
    total_try = price_try * quantity
    
    st.session_state.invoice_items.append({
        "Parça": selected_part,
        "Malzeme": selected_mat,
        "Tür": selected_type,
        "Adet": quantity,
        "Birim Fiyat (USD)": f"${base_price_usd:.2f}",
        "Toplam (TRY)": f"{total_try:.2f} TL"
    })
    st.success(f"{selected_part} için {selected_mat} başarıyla eklendi!")

# Eklenen Maddeleri Tablo Halinde Gösterme
if st.session_state.invoice_items:
    st.subheader("📋 Güncel Fatura Listesi")
    df = pd.DataFrame(st.session_state.invoice_items)
    st.dataframe(df, use_container_width=True)
    
    if st.button("🗑️ Listeyi Temizle"):
        st.session_state.invoice_items = []
        st.rerun()
else:
    st.info("Henüz fatura kalemi eklenmedi. Yukarıdan parça seçip 'Listeye Ekle' butonuna basabilirsiniz.")
