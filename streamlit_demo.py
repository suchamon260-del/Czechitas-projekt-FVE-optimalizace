import streamlit as st
from main_FVE import spocitej_vysledky
from streamlit_grafy import vytvor_heatmapa_naklad, vytvor_graf_leto_vs_zima
from streamlit_shrnuti import zobraz_shrnuti

st.markdown(
    """
    <h2 style='text-align: center;'>
        Optimální velikost fotovoltaické elektrárny a baterie pro váš dům
    </h2>
    """,
    unsafe_allow_html=True
)

st.text("")

st.markdown(
    "<p style='font-size:20px; font-weight:bold;'>"
    "Tato demo aplikace pracuje s ukázkovými daty spotřeby jedné české domácnosti. "
    "Volitelně můžete nahrát vlastní CSV soubor ze smart metru a nechat si spočítat výsledky pro svůj dům."
    "</p>",
    unsafe_allow_html=True
)

st.text("")

st.markdown("""
1. Pokud nic nenahrajete, aplikace použije ukázkový soubor `Spotreby_bez_FVE.csv`
2. Pokud nahrajete vlastní CSV, použijí se vaše data
3. Proběhne simulace FVE + baterie
4. Zobrazí se doporučené řešení a grafy
""")

st.text("")

uploaded_file = st.file_uploader(
    "Volitelné: nahrajte svůj CSV soubor.",
    type="csv",
    key="spotreba_csv_demo"
)

st.text("")

if uploaded_file is None:
    st.info("Používám ukázková data `Spotreby_bez_FVE.csv`.")
    soubor_spotreby = "Spotreby_bez_FVE.csv"
else:
    st.success("Soubor byl nahrán.")
    soubor_spotreby = uploaded_file

with st.spinner("Počítám..."):
    vysledek = spocitej_vysledky(soubor_spotreby)

    if uploaded_file is not None:
        uploaded_file.seek(0)

    st.text("")
    zobraz_shrnuti(vysledek)
    st.text("")

    st.subheader("Grafické znázornění výsledků")

    figure_heatmap_naklad = vytvor_heatmapa_naklad(vysledek)
    st.plotly_chart(figure_heatmap_naklad, use_container_width=True)

    st.text("")

    figure_leto_zima = vytvor_graf_leto_vs_zima(soubor_spotreby)
    st.plotly_chart(figure_leto_zima, use_container_width=True)
