"""
Inflation Wizard — Turkish Lira purchasing power analyzer.

Compares your money's value across years using three inflation
sources (TUIK, ENAG, ITO), minimum wage indexing, and
opportunity cost analysis with various investment instruments.

Usage:
    streamlit run app.py
"""

import streamlit as st
import pandas as pd

# ── page config ─────────────────────────────────

st.set_page_config(page_title="Inflation Wizard", layout="wide")


# ── helpers ─────────────────────────────────────

def format_tl(amount):
    """Format number as Turkish Lira (1.234,56 style)."""
    return f"{amount:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def compound(principal, rates):
    """Apply compound inflation/growth rates to a principal."""
    val = principal
    for r in rates:
        val *= (1 + r / 100)
    return val


# ── data ────────────────────────────────────────

# yillik enflasyon oranlari (%)
INFLATION = {
    2010: {"TUIK": 6.40,  "ENAG": 6.40,   "ITO": 6.60},
    2011: {"TUIK": 10.45, "ENAG": 10.45,  "ITO": 11.00},
    2012: {"TUIK": 6.16,  "ENAG": 6.16,   "ITO": 9.00},
    2013: {"TUIK": 7.40,  "ENAG": 7.40,   "ITO": 7.80},
    2014: {"TUIK": 8.17,  "ENAG": 8.17,   "ITO": 8.50},
    2015: {"TUIK": 8.81,  "ENAG": 8.81,   "ITO": 9.20},
    2016: {"TUIK": 8.53,  "ENAG": 8.53,   "ITO": 7.70},
    2017: {"TUIK": 11.92, "ENAG": 11.92,  "ITO": 9.50},
    2018: {"TUIK": 20.30, "ENAG": 20.30,  "ITO": 17.50},
    2019: {"TUIK": 11.84, "ENAG": 11.84,  "ITO": 13.40},
    2020: {"TUIK": 14.60, "ENAG": 36.72,  "ITO": 17.00},
    2021: {"TUIK": 36.08, "ENAG": 82.81,  "ITO": 45.00},
    2022: {"TUIK": 64.27, "ENAG": 137.55, "ITO": 92.97},
    2023: {"TUIK": 64.77, "ENAG": 127.21, "ITO": 74.88},
    2024: {"TUIK": 44.38, "ENAG": 83.40,  "ITO": 55.27},
}

# yil sonu varlik fiyatlari (TL)
ASSETS = {
    2010: {"USD": 1.54,  "EUR": 2.05,  "GBP": 2.40,  "GOLD": 65,   "SILVER": 1.60,  "BIST": 660},
    2011: {"USD": 1.89,  "EUR": 2.45,  "GBP": 2.95,  "GOLD": 98,   "SILVER": 1.90,  "BIST": 512},
    2012: {"USD": 1.78,  "EUR": 2.35,  "GBP": 2.85,  "GOLD": 96,   "SILVER": 1.80,  "BIST": 782},
    2013: {"USD": 2.13,  "EUR": 2.93,  "GBP": 3.50,  "GOLD": 82,   "SILVER": 1.40,  "BIST": 678},
    2014: {"USD": 2.32,  "EUR": 2.82,  "GBP": 3.60,  "GOLD": 88,   "SILVER": 1.30,  "BIST": 857},
    2015: {"USD": 2.91,  "EUR": 3.17,  "GBP": 4.30,  "GOLD": 100,  "SILVER": 1.50,  "BIST": 717},
    2016: {"USD": 3.52,  "EUR": 3.70,  "GBP": 4.35,  "GOLD": 130,  "SILVER": 1.90,  "BIST": 781},
    2017: {"USD": 3.77,  "EUR": 4.54,  "GBP": 5.10,  "GOLD": 158,  "SILVER": 2.10,  "BIST": 1153},
    2018: {"USD": 5.29,  "EUR": 6.05,  "GBP": 6.70,  "GOLD": 218,  "SILVER": 2.80,  "BIST": 912},
    2019: {"USD": 5.95,  "EUR": 6.65,  "GBP": 7.80,  "GOLD": 291,  "SILVER": 3.50,  "BIST": 1144},
    2020: {"USD": 7.43,  "EUR": 9.10,  "GBP": 10.10, "GOLD": 454,  "SILVER": 6.30,  "BIST": 1476},
    2021: {"USD": 13.30, "EUR": 15.10, "GBP": 18.00, "GOLD": 780,  "SILVER": 10.00, "BIST": 1857},
    2022: {"USD": 18.70, "EUR": 19.95, "GBP": 22.50, "GOLD": 1096, "SILVER": 14.50, "BIST": 5509},
    2023: {"USD": 29.50, "EUR": 32.60, "GBP": 37.50, "GOLD": 1960, "SILVER": 23.00, "BIST": 7470},
    2024: {"USD": 34.50, "EUR": 37.50, "GBP": 44.00, "GOLD": 3000, "SILVER": 34.00, "BIST": 9500},
}

# net asgari ucret (TL)
MIN_WAGE = {
    2010: 576,  2011: 658,  2012: 739,  2013: 803,  2014: 891,
    2015: 1000, 2016: 1300, 2017: 1404, 2018: 1603, 2019: 2020,
    2020: 2324, 2021: 2825, 2022: 5500, 2023: 11402, 2024: 17002,
}

ASSET_LABELS = {
    "USD":    "Dolar ($)",
    "EUR":    "Euro (€)",
    "GBP":    "Sterlin (£)",
    "GOLD":   "Gram Altin",
    "SILVER": "Gram Gumus",
    "BIST":   "BIST-100",
}

TARGET_YEAR = 2024


# ── UI ──────────────────────────────────────────

st.title("Inflation Wizard")
st.markdown(
    "Paranizin enflasyon karsisindaki erimesini hesaplayip, "
    "yatirim yapsaydiniz ne olacagini gosteriyor."
)

col_input, col_result = st.columns([1, 2])

with col_input:
    st.markdown("**Giris**")
    tutar = st.number_input("Tutar (TL)", min_value=100, value=10000, step=500)
    yil = st.selectbox("Hangi yildaki paran?", range(2010, TARGET_YEAR))

    st.divider()
    kaynak = st.radio(
        "Enflasyon kaynagi",
        ["TUIK", "ENAG", "ITO"],
        horizontal=True,
        help="TUIK: resmi veri, ENAG: bagimsiz ekonomistler, ITO: Istanbul Ticaret Odasi"
    )


# ── calculations ────────────────────────────────

# enflasyon hesabi (3 kaynak)
inflation_vals = {}
for src in ["TUIK", "ENAG", "ITO"]:
    rates = [INFLATION[y][src] for y in range(yil, TARGET_YEAR + 1)]
    inflation_vals[src] = compound(tutar, rates)

# secilen kaynaga gore reel deger
selected_inflation = inflation_vals[kaynak]

# asgari ucret endeksi
wage_ratio = tutar / MIN_WAGE[yil]
wage_indexed = wage_ratio * MIN_WAGE[TARGET_YEAR]

# yatirim firsati
investments = {}
for key, label in ASSET_LABELS.items():
    bought = tutar / ASSETS[yil][key]
    now = bought * ASSETS[TARGET_YEAR][key]
    change_pct = ((now - tutar) / tutar) * 100
    investments[label] = {"value": now, "change": change_pct, "units": round(bought, 2)}

# en iyi yatirim
best = max(investments.items(), key=lambda x: x[1]["value"])

# yillik kumulatif enflasyon tablosu
yearly_data = []
running = tutar
for y in range(yil, TARGET_YEAR + 1):
    rate = INFLATION[y][kaynak]
    running *= (1 + rate / 100)
    yearly_data.append({
        "Yil": y,
        "Enflasyon (%)": f"%{rate}",
        "Kumulatif Deger (TL)": format_tl(running),
    })


# ── results ─────────────────────────────────────

with col_result:
    st.subheader(f"{yil} → {TARGET_YEAR} Analizi")

    # ana metrikler
    m1, m2, m3 = st.columns(3)
    m1.metric(
        f"{kaynak} Enflasyonu ile",
        f"{format_tl(selected_inflation)} TL",
        delta=f"{((selected_inflation - tutar) / tutar * 100):+.0f}%",
        delta_color="off",
    )
    m2.metric(
        "Asgari Ucret Endeksi",
        f"{format_tl(wage_indexed)} TL",
        help=f"{yil}'de {wage_ratio:.1f} asgari ucret ediyordu",
    )
    m3.metric(
        f"En Iyi Yatirim ({best[0]})",
        f"{format_tl(best[1]['value'])} TL",
        delta=f"{best[1]['change']:+.0f}%",
    )

    st.caption(
        f"{yil} yilinda {format_tl(tutar)} TL ile "
        f"**{wage_ratio:.1f} asgari ucret** aliniyordu. "
        f"Bugunku karsiligi {format_tl(wage_indexed)} TL."
    )

    st.divider()

    # yatirim tablosu
    st.markdown("**Yatirim Yapsaydiniz**")
    st.write(
        f"{yil}'de {format_tl(tutar)} TL ile alsaydiniz, "
        f"{TARGET_YEAR} sonunda kac TL olurdu:"
    )

    inv_rows = []
    for label, data in investments.items():
        inv_rows.append({
            "Yatirim Araci": label,
            "Alinan Miktar": data["units"],
            "Bugunku Deger (TL)": format_tl(data["value"]),
            "Degisim (%)": f"%{data['change']:+.1f}",
        })

    df_inv = pd.DataFrame(inv_rows)
    st.dataframe(df_inv, use_container_width=True, hide_index=True)

    st.divider()

    # grafik
    st.markdown("**Karsilastirma**")

    chart_data = {
        "Kategori": [
            "Ana Para",
            f"{kaynak} Enflasyonu",
            "Asgari Ucret Endeksi",
        ] + list(investments.keys()),
        "Deger (TL)": [
            tutar,
            selected_inflation,
            wage_indexed,
        ] + [d["value"] for d in investments.values()],
    }
    df_chart = pd.DataFrame(chart_data)
    st.bar_chart(df_chart, x="Kategori", y="Deger (TL)")

    st.divider()

    # yillik tablo
    with st.expander(f"Yillik {kaynak} Enflasyon Tablosu"):
        st.dataframe(pd.DataFrame(yearly_data), use_container_width=True, hide_index=True)


# ── footer ──────────────────────────────────────

st.divider()
st.caption(
    "Veriler yaklasik yil sonu kapanis fiyatlarina dayanmaktadir. "
    "Yatirim tavsiyesi degildir."
)