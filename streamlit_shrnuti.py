import pandas as pd
import streamlit as st

def zobraz_shrnuti(vysledek: pd.DataFrame):
    df = vysledek.copy()

    pocet_variant = len(df)
    min_kWp = df["vykon_FVE_instalovany_kWp"].min()
    max_kWp = df["vykon_FVE_instalovany_kWp"].max()
    min_bat = df["kapacita_baterie_kWh"].min()
    max_bat = df["kapacita_baterie_kWh"].max()

    best_celk = df.loc[df["Rocni_naklad_Kc"].idxmin()]
    df_bez_best = df.drop(index=best_celk.name)

    mensi = df_bez_best[
        (df_bez_best["kapacita_baterie_kWh"] == 5) &
        (df_bez_best["vykon_FVE_instalovany_kWp"].between(4, 6))
    ]
    vetsi = df_bez_best[
        df_bez_best["vykon_FVE_instalovany_kWp"].between(8, 10) &
        df_bez_best["kapacita_baterie_kWh"].between(5, 10)
    ]

    best_mensi = mensi.loc[mensi["Rocni_naklad_Kc"].idxmin()] if not mensi.empty else None
    best_vetsi = vetsi.loc[vetsi["Rocni_naklad_Kc"].idxmin()] if not vetsi.empty else None

    st.subheader("Doporučujeme tuto kombinaci")
    st.markdown(
        f"**Elektrárna:** {int(best_celk['vykon_FVE_instalovany_kWp'])} kWp  \n"
        f"**Baterie:** {int(best_celk['kapacita_baterie_kWh'])} kWh  \n"
        f"- Roční náklady: **{int(best_celk['Rocni_naklad_Kc']):,} Kč**  \n"
        f"- Roční úspora: **{int(best_celk['Uspora_Kc']):,} Kč**  \n"
        f"- Odhadovaná návratnost: **{best_celk['Navratnost_roky']:.1f} let**  \n"
        f"- Investice po dotaci: **{int(best_celk['Investice_po_dotaci_Kc']):,} Kč**"
        .replace(",", " ")
    )

    st.subheader("Další zajímavé kombinace")

    if best_mensi is not None:
        st.markdown(
        "<u><b>Menší sestavy</b></u> (4–6 kWp, baterie 5 kWh)  \n\n"
        f"**Elektrárna:** {int(best_mensi['vykon_FVE_instalovany_kWp'])} kWp  \n"
        f"**Baterie:** {int(best_mensi['kapacita_baterie_kWh'])} kWh  \n"
        f"- Roční náklady: **{int(best_mensi['Rocni_naklad_Kc']):,} Kč**  \n"
        f"- Roční úspora: **{int(best_mensi['Uspora_Kc']):,} Kč**  \n"
        f"- Odhadovaná návratnost: **{best_mensi['Navratnost_roky']:.1f} let**  \n"
        f"- Investice po dotaci: **{int(best_mensi['Investice_po_dotaci_Kc']):,} Kč**"
        .replace(",", " "),
        unsafe_allow_html=True
    )

    if best_vetsi is not None:
        st.markdown(
        "<u><b>Větší sestavy</b></u> (8–10 kWp, baterie 5–10 kWh)  \n\n"
        f"**Elektrárna:** {int(best_vetsi['vykon_FVE_instalovany_kWp'])} kWp  \n"
        f"**Baterie:** {int(best_vetsi['kapacita_baterie_kWh'])} kWh  \n"
        f"- Roční náklady: **{int(best_vetsi['Rocni_naklad_Kc']):,} Kč**  \n"
        f"- Roční úspora: **{int(best_vetsi['Uspora_Kc']):,} Kč**  \n"
        f"- Odhadovaná návratnost: **{best_vetsi['Navratnost_roky']:.1f} let**  \n"
        f"- Investice po dotaci: **{int(best_vetsi['Investice_po_dotaci_Kc']):,} Kč**"
        .replace(",", " "),
        unsafe_allow_html=True
    )
