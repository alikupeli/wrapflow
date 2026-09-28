import streamlit as st
import pandas as pd
from datetime import datetime

# Sayfa Ayarları ve Tema Zorlaması
st.set_page_config(
    page_title="WrapFlow Proforma v1.2.0", 
    page_icon="🚗", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Gönderilen Orijinal JSON Verisinin Eksiksiz Entegrasyonu (Session State Kontrolü)
if "app_data" not in st.session_state:
    st.session_state.app_data = {
      "appName": "WrapFlow Proforma Araç Kaplama & PPF",
      "version": "1.2.0",
      "backupDate": "28.09.2026 20:12:53",
      "invoice": {
        "id": "inv-initial-01",
        "invoiceNo": "PRF-2026-0042",
        "invoiceDate": "2026-09-28",
        "customer": {
          "name": "Ahmet Karadeniz",
          "company": "Karadeniz Lojistik Ltd.",
          "phone": "+90 (532) 456 78 90",
          "email": "ahmet.karadeniz@example.com",
          "city": "İstanbul / Sarıyer",
          "taxNumber": "12345678901"
        },
        "vehicle": {
          "plate": "34 PR 911",
          "brand": "Porsche",
          "model": "911 GT3 RS",
          "materialType": "TİP5",
          "applicationDate": "2026-09-28"
        },
        "parts": [],
        "currency": "TRY",
        "discountRate": 0,
        "discountAmount": 0,
        "taxRate": 20,
        "additionalNotes": "Araç kabulünde ön kaputta 1 adet mikro taş izi tespit edilmiş olup, kaplama öncesi lokal rötuş uygulanacaktır. Sağ ön kapıya şerit ve logo uygulaması dahildir.",
        "workshop": {
          "name": "APEX WRAP STUDIO & PPF CENTER",
          "subtitle": "Profesyonel Araç Koruma, Renk Değişimi ve Detaylandırma Merkezi",
          "phone": "+90 (212) 555 44 33 / +90 (532) 777 88 99",
          "email": "iletisim@apexwrap.com.tr",
          "address": "Oto Sanayi Sitesi 4. Blok No: 28 Maslak / İstanbul",
          "taxInfo": "Maslak V.D. - 1234567890 | Tic. Sicil: 987654",
          "bankAccount": "TR12 0006 2000 1234 5678 9012 34 (Garanti BBVA - Apex Wrap Ltd.)",
          "terms": [
            "Uygulama sonrası ilk 7-10 gün araç basınçlı suyla yıkanmamalıdır.",
            "15. iş gününde ücretsiz kontrol ve kenar bitiş sabitleme randevusu önerilir.",
            "İşbu form iş onay belgesi ve proforma fatura niteliğindedir."
          ]
        },
        "exchangeRates": {
          "USD_TRY": 48.9485,
          "EUR_TRY": 55.7274,
          "GBP_TRY": 64.7815,
          "lastUpdated": "19:56",
          "isManualOverride": False
        }
      },
      "materials": [
        {"name": "SAĞ DİREK KAPLAMA", "brand": "Standart", "category": "CAST FOLYO KAPLAMA", "tierPrices": {"5500": 0, "TİP5": 0, "CAST": 100, "UV BASKI": 0}, "defaultPrice": 50, "id": "mat-1"},
        {"name": "MAVİ ŞERİT", "brand": "Standart", "category": "KAPLAMA", "tierPrices": {"5500": 25, "TİP5": 150, "CAST": 0, "UV BASKI": 0}, "defaultPrice": 50, "id": "mat-2"},
        {"name": "POLİS YAZI", "brand": "Standart", "category": "KAPLAMA", "tierPrices": {"5500": 10, "TİP5": 35, "CAST": 0, "UV BASKI": 0}, "defaultPrice": 50, "id": "mat-3"}
      ],
      "bodyParts": [
        {"id": "bp-hood", "name": "Ön Kaput", "category": "Ön Bölüm"},
        {"id": "bp-front-bumper", "name": "Ön Tampon", "category": "Ön Bölüm"},
        {"id": "bp-front-fender-r", "name": "Sağ Ön Çamurluk", "category": "Ön Bölüm"},
        {"id": "bp-front-fender-l", "name": "Sol Ön Çamurluk", "category": "Ön Bölüm"},
        {"id": "bp-front-door-r", "name": "Sağ Ön Kapı", "category": "Yan Bölüm"},
        {"id": "bp-front-door-l", "name": "Sol Ön Kapı", "category": "Yan Bölüm"}
      ],
      "materialTypes": ["5500", "TİP5", "CAST", "UV BASKI"]
    }

# --- YAN PANEL (SIDEBAR) ---
with st.sidebar:
    st.title("WrapFlow Pro")
    st.caption(f"Sürüm: {st.session_state.app_data['version']}")
    st.markdown("---")
    
    st.header("💱 Döviz Kurları")
    usd_rate = st.number_input("USD / TRY", value=st.session_state.app_data["invoice"]["exchangeRates"]["USD_TRY"], format="%.4f")
    eur_rate = st.number_input("EUR / TRY", value=st.session_state.app_data["invoice"]["exchangeRates"]["EUR_TRY"], format="%.4f")
    st.session_state.app_data["invoice"]["exchangeRates"]["USD_TRY"] = usd_rate
    st.session_state.app_data["invoice"]["exchangeRates"]["EUR_TRY"] = eur_rate
    
    st.markdown("---")
    st.header("⚙️ Fiyat Tanımlama")
    with st.expander("➕ Yeni Malzeme/İş Ekle"):
        new_mat_name = st.text_input("Malzeme veya İş Adı")
        new_mat_cat = st.text_input("Kategori")
        new_price_5500 = st.number_input("5500 Fiyatı ($)", value=0.0)
        new_price_tip5 = st.number_input("TİP5 Fiyatı ($)", value=0.0)
        new_price_cast = st.number_input("CAST Fiyatı ($)", value=0.0)
        
        if st.button("Malzemeyi Listeye Kaydet"):
            if new_mat_name:
                st.session_state.app_data["materials"].append({
                    "name": new_mat_name,
                    "brand": "Standart",
                    "category": new_mat_cat,
                    "tierPrices": {"5500": new_price_5500, "TİP5": new_price_tip5, "CAST": new_price_cast, "UV BASKI": 0},
                    "defaultPrice": 50,
                    "id": f"mat-custom"
                })
                st.success("Malzeme eklendi!")
                st.rerun()

# --- ANA EKRAN ---
st.title(f"🚗 {st.session_state.app_data['invoice']['workshop']['name']}")
st.caption(st.session_state.app_data['invoice']['workshop']['subtitle'])

# 1. Müşteri & Araç Düzenleme
with st.container():
    st.subheader("📝 Müşteri & Araç Bilgilerini Düzenle")
    c1, c2, c3 = st.columns(3)
    with c1:
        inv_no = st.text_input("Fatura / Proforma No", value=st.session_state.app_data["invoice"]["invoiceNo"])
        cust_name = st.text_input("Müşteri Adı Soyadı", value=st.session_state.app_data["invoice"]["customer"]["name"])
    with c2:
        v_plate = st.text_input("Araç Plakası", value=st.session_state.app_data["invoice"]["vehicle"]["plate"])
        v_brand = st.text_input("Araç Markası", value=st.session_state.app_data["invoice"]["vehicle"]["brand"])
    with c3:
        v_model = st.text_input("Araç Modeli", value=st.session_state.app_data["invoice"]["vehicle"]["model"])
        tax_rate = st.number_input("KDV Oranı (%)", value=st.session_state.app_data["invoice"]["taxRate"])

    st.session_state.app_data["invoice"]["invoiceNo"] = inv_no
    st.session_state.app_data["invoice"]["customer"]["name"] = cust_name
    st.session_state.app_data["invoice"]["vehicle"]["plate"] = v_plate
    st.session_state.app_data["invoice"]["vehicle"]["brand"] = v_brand
    st.session_state.app_data["invoice"]["vehicle"]["model"] = v_model
    st.session_state.app_data["invoice"]["taxRate"] = tax_rate

st.markdown("---")

# 2. Malzeme Seçim ve Ekleme
with st.container():
    st.subheader("🛠️ Parça Uygulaması ve Malzeme Seçimi")
    col_p, col_m, col_t, col_q = st.columns(4)
    
    with col_p:
        part_options = [p["name"] for p in st.session_state.app_data["bodyParts"]]
        selected_part = st.selectbox("Uygulanacak Araç Parçası", part_options)
    with col_m:
        mat_options = [m["name"] for m in st.session_state.app_data["materials"]]
        selected_mat = st.selectbox("Kullanılacak Malzeme / İşçilik", mat_options)
    with col_t:
        selected_type = st.selectbox("Malzeme Türü (Tier)", st.session_state.app_data["materialTypes"])
    with col_q:
        qty = st.number_input("Adet / Adetler", min_value=1, value=1)
        
    notes = st.text_input("Özel durum notu (İsteğe bağlı)")
    
    if st.button("⚡ Parçayı Proformaya Ekle", use_container_width=True):
        mat_obj = next(m for m in st.session_state.app_data["materials"] if m["name"] == selected_mat)
        base_usd = mat_obj["tierPrices"].get(selected_type, 0)
        if base_usd == 0:
            base_usd = mat_obj["defaultPrice"]
            
        calculated_price_try = base_usd * usd_rate
        
        new_part_entry = {
            "partName": selected_part,
            "applications": [{
                "name": selected_mat,
                "materialType": selected_type,
                "price": calculated_price_try,
                "quantity": qty,
                "notes": notes if notes else "Standart"
            }]
        }
        st.session_state.app_data["invoice"]["parts"].append(new_part_entry)
        st.toast(f"{selected_part} listeye eklendi!")

# --- FATURA ÖNİZLEME ---
st.markdown("---")
st.subheader("📋 Dijital Proforma Fatura")

# Üst özet kartları
c_info1, c_info2 = st.columns(2)
with c_info1:
    st.info(f"**Müşteri:** {st.session_state.app_data['invoice']['customer']['name']} | **Fatura No:** {st.session_state.app_data['invoice']['invoiceNo']}")
with c_info2:
    st.success(f"**Araç:** {st.session_state.app_data['invoice']['vehicle']['brand']} {st.session_state.app_data['invoice']['vehicle']['model']} [{st.session_state.app_data['invoice']['vehicle']['plate']}]")

if st.session_state.app_data["invoice"]["parts"]:
    # Eklenen Parçaların Listelenmesi
    table_data = []
    subtotal = 0.0
    
    for p in st.session_state.app_data["invoice"]["parts"]:
        for app in p["applications"]:
            item_total = app["price"] * app["quantity"]
            subtotal += item_total
            table_data.append({
                "Uygulanan Parça": p["partName"],
                "Hizmet/Malzeme": app["name"],
                "Tür (Tier)": app["materialType"],
                "Adet": app["quantity"],
                "Birim Fiyat": f"{app['price']:.2f} TL",
                "Toplam Tutar": f"{item_total:.2f} TL",
                "Notlar": app["notes"]
            })
            
    st.dataframe(pd.DataFrame(table_data), use_container_width=True)
    
    # Hesaplama alanı
    discount = st.number_input("İndirim Tutarı (TL)", value=0.0)
    total_before_tax = subtotal - discount
    tax_amount = total_before_tax * (tax_rate / 100)
    grand_total = total_before_tax + tax_amount
    
