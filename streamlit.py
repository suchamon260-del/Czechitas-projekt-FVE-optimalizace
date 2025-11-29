import streamlit as st
import pandas as pd
from main_FVE import spocitej_vysledky
from streamlit_grafy import vytvor_heatmapa_navratnost, vytvor_heatmapa_naklad, vytvor_graf_leto_vs_zima
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
    "Aplikace analyzuje vaši roční spotřebu elektřiny a navrhne optimální kombinaci výkonu fotovoltaické elektrárny a kapacity bateriového úložiště."
    "</p>",
    unsafe_allow_html=True
)

st.text("")
st.markdown("""
**Jak to funguje:**

1. Nahrajete svůj CSV soubor s roční spotřebou elektřiny z Portálu naměřených dat  
2. Vaše data spotřeby se sloučí s modelovanou solární výrobou a provede se simulace chování celé sestavy
3. Zobrazí se doporučené řešení pro váš dům a přehledné grafy
""")

st.text("")

uploaded_file = st.file_uploader("Přetáhněte sem svůj CSV soubor nebo jej vyberte z počítače.", type="csv", key="spotreba_csv")

st.text("")

if uploaded_file is not None:
    with st.spinner("Počítám..."):
        vysledek = spocitej_vysledky(uploaded_file)

        uploaded_file.seek(0)

        with st.expander("**Jak číst výsledky**"):st.markdown(
        "- **Roční náklady** – kolik v průměru ročně zaplatíte za elektřinu po instalaci elektrárny "
"včetně rozpočítané investice do elektrárny a baterie  \n"
"- **Roční úspora** – o kolik méně ročně zaplatíte za elektřinu oproti stavu bez elektrárny "
"bez započtení investice do elektrárny a baterie \n"
        "- **Návratnost** – za kolik let se vrátí investice do systému při této roční úspoře  \n"
        "- **Investice po dotaci** – částka, kterou zaplatíte po započtení dotace"
    )
        st.text("")
        
        zobraz_shrnuti(vysledek)
        
        st.text("")

        st.subheader("Grafické znázornění výsledků")
        st.text("")

        figure_heatmap_naklad = vytvor_heatmapa_naklad(vysledek)
        st.plotly_chart(figure_heatmap_naklad, use_container_width=True)
        st.markdown("Pozn. Žlutý rámeček označuje doporučenou kombinaci výkonu elektrárny a kapacity baterie. "
    "Při najetí myší na libovolné pole v grafu se zobrazí detailní informace pro danou sestavu "
    "(roční náklady, soběstačnost, návratnost a roční úspora)."
)
        st.text("")

        figure_leto_zima = vytvor_graf_leto_vs_zima(uploaded_file)
        st.plotly_chart(figure_leto_zima, use_container_width=True)
        # figure_heatmap_navratnost = vytvor_heatmapa_navratnost(vysledek)
        # st.plotly_chart(figure_heatmap_navratnost, use_container_width=True)
        st.markdown("Pozn. Z průběhu solární výroby je vidět, že je vhodné fotovoltaickou elektrárnu kombinovat "
    "s baterií. Ta umožní lépe využít přebytky vyrobené elektřiny v době, kdy "
    "slunce nesvítí a spotřeba v domácnosti je vyšší."
)



        


