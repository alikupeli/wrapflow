import streamlit as st
import pandas as pd
from datetime import datetime

# Ekran Ayarları (Geniş Ekran Stüdyo Modu)
st.set_page_config(
    page_title="WrapFlow Proforma - Araç Kaplama & PPF", 
    page_icon="🚗", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Orijinal JSON Veri Tabanı Entegrasyonu (Session State Kontrolü)
if "app_data" not in st.session_state:
    st.session_state.app_data = {
      "invoice": {
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
          "materialType": "TİP5"
        },
        "parts": [], # [ { "partName": "Sol Ön Çamurluk", "applications": [...] } ]
        "discountAmount": 440.00,
        "taxRate": 20,
        "additionalNotes": "Araç kabulünde ön kaputta 1 adet mikro taş izi tespit edilmiş olup, kaplama öncesi lokal rötuş uygulanacaktır. Sağ ön kapıya şerit ve logo uygulaması dahildir."
      },
      "materials": [
        {"name": "SAĞ DİREK KAPLAMA", "category": "CAST FOLYO KAPLAMA", "tierPrices": {"5500": 0, "TİP5": 0, "CAST": 100, "UV BASKI": 0}, "defaultPrice": 50},
        {"name": "MAVİ ŞERİT", "category": "KAPLAMA", "tierPrices": {"5500": 25, "TİP5": 150, "CAST": 0, "UV BASKI": 0}, "defaultPrice": 50},
        {"name": "POLİS YAZI", "category": "KAPLAMA", "tierPrices": {"5500": 10, "TİP5": 35, "CAST": 0, "UV BASKI": 0}, "defaultPrice": 50}
      ],
      "bodyParts": ["Ön Kaput", "Ön Tampon", "Sağ Ön Çamurluk", "Sol Ön Çamurluk", "Sağ Ön Kapı", "Sol Ön Kapı", "Tavan", "Arka Tampon"],
      "materialTypes": ["5500", "TİP5", "CAST", "UV BASKI"],
      "exchangeRates": {"USD_TRY": 48.9485, "EUR_TRY": 55.7274, "GBP_TRY": 64.7815},
      "active_currency": "TRY"
    }

# --- BİREBİR ÜST BİLGİ ŞERİDİ (TEMA VE KURLAR) ---
st.markdown(
    f"""
    <div style="background-color:#1a1c23; padding:10px; border-radius:6px; margin-bottom:20px; display:flex; justify-content:space-between; align-items:center; border:1px solid #333;">
        <div style="font-size:13px; color:#aaa;">
            <span style="color:#00ffcc; font-weight:bold;">● CANLI PİYASA KURLARI:</span> &nbsp;&nbsp; 
            <b>USD/TL:</b> {st.session_state.app_data['exchangeRates']['USD_TRY']:.2f} &nbsp;&nbsp;|&nbsp;&nbsp; 
            <b>EUR/TL:</b> {st.session_state.app_data['exchangeRates']['EUR_TRY']:.2f} &nbsp;&nbsp;|&nbsp;&nbsp; 
            <b>GBP/TL:</b> {st.session_state.app_data['exchangeRates']['GBP_TRY']:.2f}
        </div>
        <div style="font-size:12px; color:#888;">
            <b>WrapFlow Proforma</b> v1.2.0 | Apex Wrap Studio
        </div>
    </div>
    """, 
    unsafe_allowed_html=True
)

# Üst Sağ Para Birimi Seçici Simülasyonu
col_title, col_curr = st.columns([3, 1])
with col_title:
    st.title("🚗 WrapFlow İş Emri & Teklif Oluşturucu")
with col_curr:
    selected_currency = st.radio("Para Birimi", ["₺ TL", "$ USD", "€ EUR"], horizontal=True)
    st.session_state.app_data["active_currency"] = selected_currency.split(" ")[1]

st.markdown("---")

# --- 1. ARAÇ & MÜŞTERİ KÜNYESİ (GÖRSELDEKİ BİRİNCİ BLOK) ---
st.subheader("📋 Araç & Müşteri Künyesi")
c1, c2, c3 = st.columns(3)

with c1:
    st.markdown("**👤 MÜŞTERİ BİLGİLERİ**")
    cust_name = st.text_input("Müşteri Adı / Firma Ünvanı *", value=st.session_state.app_data["invoice"]["customer"]["name"])
    cust_phone = st.text_input("Telefon Numarası *", value=st.session_state.app_data["invoice"]["customer"]["phone"])
    cust_city = st.text_input("İl / İlçe", value=st.session_state.app_data["invoice"]["customer"]["city"])
    cust_tax = st.text_input("VKN / TCKN", value=st.session_state.app_data["invoice"]["customer"]["taxNumber"])

with c2:
    st.markdown("**🚘 ARAÇ KÜNYESİ**")
    v_plate = st.text_input("Araç Plakası *", value=st.session_state.app_data["invoice"]["vehicle"]["plate"])
    v_brand = st.text_input("Araç Markası *", value=st.session_state.app_data["invoice"]["vehicle"]["brand"])
    v_model = st.text_input("Model / Paket *", value=st.session_state.app_data["invoice"]["vehicle"]["model"])
    v_mat_type = st.selectbox("Bağımsız Malzeme & Fiyatlandırma Türü", st.session_state.app_data["materialTypes"], index=1)

with c3:
    st.markdown("**📅 TARİH & UYGULAMA ZAMANI**")
    inv_no = st.text_input("Teklif / Proforma No", value=st.session_state.app_data["invoice"]["invoiceNo"])
    app_date = st.date_input("Uygulama Tarihi", datetime.strptime(st.session_state.app_data["invoice"]["invoiceDate"], "%Y-%m-%d"))

# Künye verilerini güncelleme
st.session_state.app_data["invoice"]["customer"]["name"] = cust_name
st.session_state.app_data["invoice"]["customer"]["phone"] = cust_phone
st.session_state.app_data["invoice"]["customer"]["city"] = cust_city
st.session_state.app_data["invoice"]["customer"]["taxNumber"] = cust_tax
st.session_state.app_data["invoice"]["vehicle"]["plate"] = v_plate
st.session_state.app_data["invoice"]["vehicle"]["brand"] = v_brand
st.session_state.app_data["invoice"]["vehicle"]["model"] = v_model
st.session_state.app_data["invoice"]["invoiceNo"] = inv_no

st.markdown("---")

# --- KÜTÜPHANE YÖNETİM PANELİ (YANDAN AÇILIR PANEL YERİNE BURADA) ---
with st.expander("⚙️ Malzeme Kütüphanesi ve Fiyat Tanımlama Odası (Ekle/Çıkar/Düzenle)"):
    st.markdown("Buradan eklediğiniz malzemeler aşağıdaki dinamik listelerde anında görünür.")
    mat_df = pd.DataFrame([
        {
            "Malzeme Adı": m["name"],
            "Kategori": m["category"],
            "5500 Fiyat ($)": m["tierPrices"]["5500"],
            "TİP5 Fiyat ($)": m["tierPrices"]["TİP5"],
            "CAST Fiyat ($)": m["tierPrices"]["CAST"]
        } for m in st.session_state.app_data["materials"]
    ])
    st.dataframe(mat_df, use_container_width=True)
    
    cx1, cx2, cx3, cx4, cx5 = st.columns(5)
    with cx1: new_m_name = st.text_input("Yeni Malzeme Adı")
    with cx2: new_m_cat = st.text_input("Kategori Türü")
    with cx3: p_5500 = st.number_input("5500 ($)", value=0.0)
    with cx4: p_tip5 = st.number_input("TİP5 ($)", value=0.0)
    with cx5: p_cast = st.number_input("CAST ($)", value=0.0)
    
    if st.button("➕ Yeni Malzemeyi Kütüphaneye Kaydet"):
        if new_m_name:
            st.session_state.app_data["materials"].append({
                "name": new_m_name,
                "category": new_m_cat,
                "tierPrices": {"5500": p_5500, "TİP5": p_tip5, "CAST": p_cast, "UV BASKI": 0},
                "defaultPrice": 50
            })
            st.success("Malzeme kütüphaneye eklendi!")
            st.rerun()

st.markdown("---")

# --- 2. DİNAMİK PARÇA VE İŞLEM EKLEME MOTORU (GÖRSELDEKİ İKİNCİ BLOK) ---
st.subheader("🛠️ Araç Parçaları & Yapılacak İşlemler Listesi")
st.caption("Kaporta parçalarını seçerek; her parçaya birden çok malzemeyi dilediğiniz tarife veya fiyatla tanımlayabilirsiniz.")

col_sel_part, col_btn_add = st.columns([3, 1])
with col_sel_part:
    active_part = st.selectbox("Kütüphaneden Kaporta Parçası Seç...", st.session_state.app_data["bodyParts"])
with col_btn_add:
    st.write(" ") # Hizalama boşluğu
    if st.button("➕ Parçayı Teklife Ekle", use_container_width=True):
        # Eğer bu parça daha önce eklenmediyse fatura listesine boş olarak ekle
        if not any(p["partName"] == active_part for p in st.session_state.app_data["invoice"]["parts"]):
            st.session_state.app_data["invoice"]["parts"].append({
                "partName": active_part,
                "applications": []
            })
            st.rerun()

# --- 3. DİNAMİK LİSTELEME VE HESAPLAMA ALANI (GÖRSELDEKİ SOL ÖN ÇAMURLUK ÖRNEĞİ) ---
subtotal = 0.0

if st.session_state.app_data["invoice"]["parts"]:
    for part_idx, part_item in enumerate(st.session_state.app_data["invoice"]["parts"]):
        st.markdown(f"### 🔲 {part_item['partName']}")
        
        # Parçanın altındaki işlemler için dinamik form satırları
        with st.container():
            # Başlık Satırı
            h1, h2, h3, h4, h5, h6 = st.columns([3, 2, 2, 1, 2, 2])
            h1.write("<small>UYGULANAN MALZEME / İŞLEM</small>", unsafe_allowed_html=True)
            h2.write("<small>MALZEME CİNSİ (TIER)</small>", unsafe_allowed_html=True)
            h3.write("<small>BİRİM FİYAT ($)</small>", unsafe_allowed_html=True)
            h4.write("<small>MİKTAR</small>", unsafe_allowed_html=True)
            h5.write("<small>TUTAR (TL)</small>", unsafe_allowed_html=True)
            h6.write("<small>NOT / AÇIKLAMA</small>", unsafe_allowed_html=True)
            
            # Mevcut kayıtlı alt uygulamaları listeleme
            rem_idx = None
            for app_idx, app in enumerate(part_item["applications"]):
                c_m, c_c, c_bf, c_q, c_t, c_n = st.columns([3, 2, 2, 1, 2, 2])
                c_m.write(f"**{app['name']}**")
                c_c.write(f"`{app['materialType']}`")
                c_bf.write(f"${app['usd_base']:.2f}")
                c_q.write(str(app['quantity']))
                
                # Anlık Döviz Kuru Çevirici (Dolar Fiyatını TL'ye Çevirir)
                calculated_tl = app['usd_base'] * st.session_state.app_data["exchangeRates"]["USD_TRY"] * app['quantity']
                subtotal += calculated_tl
                
                c_t.write(f"**₺{calculated_tl:,.2f}**")
                c_n.write(app['notes'])
            
            # Her parçanın altına yeni malzeme/satır ekleme bölümü (Görseldeki sarı buton alanı)
            with st.expander(f"➕ {part_item['partName']} İçin Yeni Malzeme / İşlem Satırı Ekle"):
                s1, s2, s3, s4 = st.columns(4)
                with s1:
                    sel_mat = st.selectbox("Malzeme Seç", [m["name"] for m in st.session_state.app_data["materials"]], key=f"mat_{part_idx}")
                with s2:
                    sel_type = st.selectbox("Cinsi", st.session_state.app_data["materialTypes"], key=f"type_{part_idx}")
                with s3:
                    qty = st.number_input("Miktar", min_value=1, value=1, key=f"qty_{part_idx}")
                with s4:
                    note_str = st.text_input("Açıklama", value="Standart", key=f"note_{part_idx}")
                
                if st.button("⚡ Malzemeyi Satıra İşle", key=f"btn_{part_idx}"):
                    # Kütüphaneden fiyat bulma mantığı
                    mat_obj = next(m for m in st.session_state.app_data["materials"] if m["name"] == sel_mat)
                    usd_price = mat_obj["tierPrices"].get(sel_type, mat_obj["defaultPrice"])
                    
                    if usd_price == 0:
                        usd_price = mat_obj["defaultPrice"]
                        
                    part_item["applications"].append({
                        "name": sel_mat,
                        "materialType": sel_type,
                        "usd_base": usd_price,
                        "quantity": qty,
                        "notes": note_str
                    })
                    st.toast("İşlem başarıyla eklendi!")
                    st.rerun()
        
        # Parça Toplamı Hesaplama
        part_tot = sum(a['usd_base'] * st.session_state.app_data['exchangeRates']['USD_TRY'] * a['quantity'] for a in part_item['applications'])
        st.markdown(f"<div style='text-align:right; color:#00ffcc; font-weight:bold;'>Parça Toplamı: ₺{part_tot:,.2f}</div>", unsafe_allowed_html=True)
        st.markdown("---")

# --- 4. MALİYET & FİYATLANDIRMA ÖZETİ (SAĞ ALT KUTU) ---
st.subheader("📊 Maliyet & Fiyatlandırma Özeti")
cx_left, cx_right = st.columns(2)

with cx_left:
    st.markdown("**¼ İŞ EMRİ & ÖZEL NOTLAR (MÜŞTERİ TALEPLERİ / EKSPERTİZ)**")
    additional_notes = st.text_area("Evrak altında çıkacak özel notlar", value=st.session_state.app_data["invoice"]["additionalNotes"])
    st.session_state.app_data["invoice"]["additionalNotes"] = additional_notes

with cx_right:
    st.markdown("<div style='background-color:#1e2430; padding:20px; border-radius:8px;'>", unsafe_allowed_html=True)
    st.write(f"**Ara Toplam:** ₺{subtotal:,.2f}")
    
    # İskonto/İndirim Girişi
    discount = st.number_input("İskonto / İndirim (TL):", value=float(st.session_state.app_data["invoice"]["discountAmount"]))
    st.session_state.app_data["invoice"]["discountAmount"] = discount
    
    # KDV Hesaplama
    tax_rate = st.session_state.app_data["invoice"]["taxRate"]
    total_before_tax = subtotal - discount
    tax_amount = total_before_tax * (tax_rate / 100)
    grand_total = total_before_tax + tax_amount
    
    st.write(f"**KDV Oranı (%{tax_rate}):** ₺{tax_amount:,.2f}")
    st.markdown("---")
    
    # Para Birimi Çevirici Motoru
    active_curr = st.session_state.app_data["active_currency"][0]
    if "USD" in active_curr:
        display_total = grand_total / st.session_state.app_data["exchangeRates"]["USD_TRY"]
        symbol = "\$"
    elif "EUR" in active_curr:
        display_total = grand_total / st.session_state.app_data["exchangeRates"]["EUR_TRY"]
        symbol = "€"
    else:
        display_total = grand_total
        symbol = "₺"
        
    st.metric(label="TOPLAM TUTAR", value=f"{symbol}{display_total:,.2f}")
    st.markdown("</div>", unsafe_allowed_html=True)

# Temizleme Butonu
if st.session_state.app_data["invoice"]["parts"]:
    st.markdown("---")
    if st.button("🗑 Tüm Formu Temizle ve Yeni Araç Kabulü Yap", use_container_width=True):
        st.session_state.app_data["invoice"]["parts"] = []
        st.rerun()
                                                           
