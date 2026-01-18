import streamlit as st
import pandas as pd

# Sayfa Ayarları
st.set_page_config(page_title="Finansal Zaman Makinesi", layout="wide")

# TÜRKÇE PARA FORMATI FONKSİYONU
def format_tl(amount):
    return f"{amount:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

st.title("🚀 Finansal Zaman Makinesi: Enflasyon & Yatırım Analizi")
st.markdown("""
Bu araç, paranızın **enflasyon karşısındaki erimesini** hesaplarken, aynı zamanda **Döviz ve Emtia** gibi yatırım araçlarındaki fırsat maliyetini analiz eder.
""")

# --- VERİ SETLERİ ---

# 1. ENFLASYON ORANLARI (Yıllık %)
inflation_rates = {
    2010: {'TUIK': 6.40,  'ENAG': 6.40,   'ITO': 6.60},
    2011: {'TUIK': 10.45, 'ENAG': 10.45,  'ITO': 11.00},
    2012: {'TUIK': 6.16,  'ENAG': 6.16,   'ITO': 9.00},
    2013: {'TUIK': 7.40,  'ENAG': 7.40,   'ITO': 7.80},
    2014: {'TUIK': 8.17,  'ENAG': 8.17,   'ITO': 8.50},
    2015: {'TUIK': 8.81,  'ENAG': 8.81,   'ITO': 9.20},
    2016: {'TUIK': 8.53,  'ENAG': 8.53,   'ITO': 7.70},
    2017: {'TUIK': 11.92, 'ENAG': 11.92,  'ITO': 9.50},
    2018: {'TUIK': 20.30, 'ENAG': 20.30,  'ITO': 17.50},
    2019: {'TUIK': 11.84, 'ENAG': 11.84,  'ITO': 13.40},
    2020: {'TUIK': 14.60, 'ENAG': 36.72,  'ITO': 17.00},
    2021: {'TUIK': 36.08, 'ENAG': 82.81,  'ITO': 45.00},
    2022: {'TUIK': 64.27, 'ENAG': 137.55, 'ITO': 92.97},
    2023: {'TUIK': 64.77, 'ENAG': 127.21, 'ITO': 74.88},
    2024: {'TUIK': 44.38, 'ENAG': 83.40,  'ITO': 55.27}
}

# 2. VARLIK FİYATLARI (Yıl Sonu Kapanış - Yaklaşık TL)
# USD: Dolar, EUR: Euro, GBP: Sterlin, GOLD: Gram Altın, SILVER: Gram Gümüş, BIST: Bist100
asset_prices = {
    2010: {'USD': 1.54, 'EUR': 2.05, 'GBP': 2.40, 'GOLD': 65,   'SILVER': 1.60, 'BIST': 660},
    2011: {'USD': 1.89, 'EUR': 2.45, 'GBP': 2.95, 'GOLD': 98,   'SILVER': 1.90, 'BIST': 512},
    2012: {'USD': 1.78, 'EUR': 2.35, 'GBP': 2.85, 'GOLD': 96,   'SILVER': 1.80, 'BIST': 782},
    2013: {'USD': 2.13, 'EUR': 2.93, 'GBP': 3.50, 'GOLD': 82,   'SILVER': 1.40, 'BIST': 678},
    2014: {'USD': 2.32, 'EUR': 2.82, 'GBP': 3.60, 'GOLD': 88,   'SILVER': 1.30, 'BIST': 857},
    2015: {'USD': 2.91, 'EUR': 3.17, 'GBP': 4.30, 'GOLD': 100,  'SILVER': 1.50, 'BIST': 717},
    2016: {'USD': 3.52, 'EUR': 3.70, 'GBP': 4.35, 'GOLD': 130,  'SILVER': 1.90, 'BIST': 781},
    2017: {'USD': 3.77, 'EUR': 4.54, 'GBP': 5.10, 'GOLD': 158,  'SILVER': 2.10, 'BIST': 1153},
    2018: {'USD': 5.29, 'EUR': 6.05, 'GBP': 6.70, 'GOLD': 218,  'SILVER': 2.80, 'BIST': 912},
    2019: {'USD': 5.95, 'EUR': 6.65, 'GBP': 7.80, 'GOLD': 291,  'SILVER': 3.50, 'BIST': 1144},
    2020: {'USD': 7.43, 'EUR': 9.10, 'GBP': 10.10, 'GOLD': 454, 'SILVER': 6.30, 'BIST': 1476},
    2021: {'USD': 13.30,'EUR': 15.10,'GBP': 18.00, 'GOLD': 780, 'SILVER': 10.00,'BIST': 1857},
    2022: {'USD': 18.70,'EUR': 19.95,'GBP': 22.50, 'GOLD': 1096,'SILVER': 14.50,'BIST': 5509},
    2023: {'USD': 29.50,'EUR': 32.60,'GBP': 37.50, 'GOLD': 1960,'SILVER': 23.00,'BIST': 7470},
    2024: {'USD': 34.50,'EUR': 37.50,'GBP': 44.00, 'GOLD': 3000,'SILVER': 34.00,'BIST': 9500}
}

# 3. NET ASGARİ ÜCRET
min_wage = {
    2010: 576, 2011: 658, 2012: 739, 2013: 803, 2014: 891,
    2015: 1000, 2016: 1300, 2017: 1404, 2018: 1603, 2019: 2020,
    2020: 2324, 2021: 2825, 2022: 5500, 2023: 11402, 2024: 17002
}

# --- ARAYÜZ ---

col1, col2 = st.columns([1, 2])

with col1:
    st.info("📊 **Giriş Paneli**")
    tutar = st.number_input("Geçmişteki Tutar (TL)", min_value=100, value=7000, step=100)
    baslangic_yili = st.selectbox("Hangi Yıldaki Paran?", range(2010, 2024))
    
    st.write("---")
    st.caption("Veriler yıl sonu kapanış fiyatları baz alınarak hesaplanmıştır.")

# --- HESAPLAMA MOTORU ---
if baslangic_yili:
    # 1. ENFLASYON HESABI
    sources = ['TUIK', 'ENAG', 'ITO']
    inflation_results = {}
    
    for source in sources:
        val = tutar
        for y in range(baslangic_yili, 2025):
            rate = inflation_rates[y][source]
            val = val * (1 + rate / 100)
        inflation_results[source] = val

    # 2. ASGARİ ÜCRET HESABI
    old_min_wage = min_wage[baslangic_yili]
    wage_ratio = tutar / old_min_wage
    current_min_wage = min_wage[2024]
    wage_indexed_value = wage_ratio * current_min_wage

    # 3. YATIRIM HESABI (Euro, Sterlin, Gümüş Eklendi)
    investment_results = {}
    # assets listesindeki sıraya göre grafikte görünecek
    assets = ['USD', 'EUR', 'GBP', 'GOLD', 'SILVER', 'BIST']
    asset_names = {
        'USD': 'Dolar ($)', 
        'EUR': 'Euro (€)', 
        'GBP': 'Sterlin (£)', 
        'GOLD': 'Altın (Gr)', 
        'SILVER': 'Gümüş (Gr)', 
        'BIST': 'Borsa (BIST100)'
    }
    
    for asset in assets:
        price_then = asset_prices[baslangic_yili][asset]
        price_now = asset_prices[2024][asset]
        
        amount_bought = tutar / price_then
        current_val = amount_bought * price_now
        investment_results[asset_names[asset]] = current_val

# --- SONUÇLARI GÖSTERME ---
with col2:
    st.subheader(f"🔍 Analiz Sonuçları ({baslangic_yili} -> 2024)")
    
    # METRİKLER
    c1, c2, c3 = st.columns(3)
    c1.metric(label="TÜİK'e Göre Değeri", value=f"{format_tl(inflation_results['TUIK'])} TL")
    c2.metric(label="ENAG'a Göre Değeri", value=f"{format_tl(inflation_results['ENAG'])} TL")
    c3.metric(
        label="Asgari Ücret Bazlı Değeri", 
        value=f"{format_tl(wage_indexed_value)} TL",
        help=f"{baslangic_yili} yılında paranız {wage_ratio:.1f} asgari ücret ediyordu. Bugün aynı oranda asgari ücret bu kadar ediyor."
    )
    st.caption(f"ℹ️ **Asgari Ücret Açıklaması:** {baslangic_yili} yılında bu para ile yaklaşık **{wage_ratio:.1f} adet** asgari ücret alınıyordu. Bugünün asgari ücretiyle hesaplandığında karşılığı yukarıdaki gibidir.")

    st.divider()

    # TABLO
    st.markdown("### 💰 Yatırım Yapsaydınız (Fırsat Maliyeti)")
    st.write(f"{baslangic_yili} yılında {format_tl(tutar)} TL ile yatırım yapsaydınız bugün kaç paranız olurdu?")
    
    inv_data = {
        "Yatırım Aracı": list(investment_results.keys()),
        "Bugünkü Değer (TL)": [format_tl(v) for v in investment_results.values()],
        "Ham Değer": [v for v in investment_results.values()]
    }
    df_inv = pd.DataFrame(inv_data)
    
    st.dataframe(
        df_inv[["Yatırım Aracı", "Bugünkü Değer (TL)"]].style.apply(
            lambda x: ['background-color: #d4edda' if i == df_inv['Ham Değer'].idxmax() else '' for i in range(len(x))], 
            axis=0
        ),
        use_container_width=True,
        hide_index=True
    )

    # GRAFİK
    st.markdown("### 📈 Görsel Kıyaslama")
    
    all_data = {
        'Kategori': ['Ana Para', 'TÜİK', 'ENAG', 'Asgari Ücret Endeksi'] + list(investment_results.keys()),
        'Değer (TL)': [tutar, inflation_results['TUIK'], inflation_results['ENAG'], wage_indexed_value] + list(investment_results.values())
    }
    df_chart = pd.DataFrame(all_data)
    
    st.bar_chart(df_chart, x='Kategori', y='Değer (TL)', color='Kategori')