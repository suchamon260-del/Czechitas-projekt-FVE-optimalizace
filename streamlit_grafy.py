import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from PVGIS import nacti_PVGIS
from Spotreby_bez_FVE import nacti_spotreby_bez_FVE


def vytvor_heatmapa_navratnost(vysledek):
    vykony = sorted(vysledek["vykon_FVE_instalovany_kWp"].unique())
    baterie = sorted(vysledek["kapacita_baterie_kWh"].unique())
    pivot_navr = vysledek.pivot_table(
        index="vykon_FVE_instalovany_kWp",
        columns="kapacita_baterie_kWh",
        values="Navratnost_roky"
    ).reindex(index=vykony, columns=baterie)

    figure = px.imshow(
        pivot_navr.round(1),
        labels=dict(
            x="Kapacita baterie [kWh]",
            y="Výkon FVE [kWp]",
            color="Doba návratnosti [roky]"
        ),
        title="Doba návratnosti podle výkonu FVE a kapacity baterie",
        text_auto=".1f",
        aspect="auto"
    )

    figure.update_xaxes(type="category")
    figure.update_yaxes(type="category")

    figure.update_traces(
        hovertemplate="Výkon FVE: %{y} kWp<br>Kapacita baterie: %{x} kWh<br>Doba návratnosti: %{z:.1f} roku<extra></extra>"
    )

    figure.update_layout(
        margin=dict(l=60, r=20, t=60, b=60)
    )
    return figure


def vytvor_heatmapa_naklad(vysledek):
    vykony = sorted(vysledek["vykon_FVE_instalovany_kWp"].unique(), reverse=True)
    baterie = sorted(vysledek["kapacita_baterie_kWh"].unique())

    pivot_naklad = (
        vysledek.pivot_table(
            index="vykon_FVE_instalovany_kWp",
            columns="kapacita_baterie_kWh",
            values="Rocni_naklad_Kc"
        )
        .reindex(index=vykony, columns=baterie)
    )

    pivot_sobe = (
        vysledek.pivot_table(
            index="vykon_FVE_instalovany_kWp",
            columns="kapacita_baterie_kWh",
            values="sobestacnost_pct"
        )
        .reindex(index=vykony, columns=baterie)
    )

    pivot_navratnost = (
        vysledek.pivot_table(
            index="vykon_FVE_instalovany_kWp",
            columns="kapacita_baterie_kWh",
            values="Navratnost_roky"
        )
        .reindex(index=vykony, columns=baterie)
    )

    pivot_uspora = (
        vysledek.pivot_table(
            index="vykon_FVE_instalovany_kWp",
            columns="kapacita_baterie_kWh",
            values="Uspora_Kc"
        )
        .reindex(index=vykony, columns=baterie)
    )

def vytvor_heatmapa_naklad(vysledek):
    vykony = sorted(vysledek["vykon_FVE_instalovany_kWp"].unique(), reverse=True)
    baterie = sorted(vysledek["kapacita_baterie_kWh"].unique())

    pivot_naklad = (
        vysledek.pivot_table(
            index="vykon_FVE_instalovany_kWp",
            columns="kapacita_baterie_kWh",
            values="Rocni_naklad_Kc"
        )
        .reindex(index=vykony, columns=baterie)
    )

    pivot_sobe = (
        vysledek.pivot_table(
            index="vykon_FVE_instalovany_kWp",
            columns="kapacita_baterie_kWh",
            values="sobestacnost_pct"
        )
        .reindex(index=vykony, columns=baterie)
    )

    pivot_navratnost = (
        vysledek.pivot_table(
            index="vykon_FVE_instalovany_kWp",
            columns="kapacita_baterie_kWh",
            values="Navratnost_roky"
        )
        .reindex(index=vykony, columns=baterie)
    )

    pivot_uspora = (
        vysledek.pivot_table(
            index="vykon_FVE_instalovany_kWp",
            columns="kapacita_baterie_kWh",
            values="Uspora_Kc"
        )
        .reindex(index=vykony, columns=baterie)
    )

    hover_text = pd.DataFrame(index=pivot_naklad.index, columns=pivot_naklad.columns)

    for i in pivot_naklad.index:
        for j in pivot_naklad.columns:
            naklad = pivot_naklad.loc[i, j]
            sobe = pivot_sobe.loc[i, j]
            navr = pivot_navratnost.loc[i, j]
            uspo = pivot_uspora.loc[i, j]
            if pd.notnull(naklad):
                hover_text.loc[i, j] = (
                f"Výkon FVE: {i} kWp<br>"
                f"Kapacita baterie: {j} kWh<br>"
                f"Roční náklady: {str(format(naklad, ',.0f')).replace(',', ' ')} Kč<br>"
                f"Soběstačnost: {sobe:.1f} %<br>"
                f"Návratnost: {navr:.1f} let<br>"
                f"Roční úspora: {str(format(uspo, ',.0f')).replace(',', ' ')} Kč"
                )
            else:
                hover_text.loc[i, j] = ""

    text_naklad = pivot_naklad.applymap(
        lambda v: "" if pd.isna(v) else f"{v:,.0f}".replace(",", " ")
    )

    fig_heat_naklad = px.imshow(
        pivot_naklad,
        color_continuous_scale=[(0, "#0000FF"), (1, "#FF0000")],
        labels=dict(
            x="Kapacita baterie [kWh]",
            y="Výkon FVE [kWp]",
            color="Roční náklady [Kč]"
        ),
        title="<b>Roční náklady podle výkonu elektrárny a kapacity baterie v Kč</b>",
        aspect="auto"
    )

    fig_heat_naklad.update_xaxes(type="category")
    fig_heat_naklad.update_yaxes(type="category")

    fig_heat_naklad.add_shape(
        type="rect",
        x0=0.5, y0=-0.5, x1=1.5, y1=0.5,
        line=dict(color="Yellow", width=2)
    )

    fig_heat_naklad.update_traces(
        hovertext=hover_text.values,
        hovertemplate="%{hovertext}<extra></extra>",
        text=text_naklad.values,
        texttemplate="%{text}"
    )

    fig_heat_naklad.update_layout(
        title_x=0.1,
        title_font=dict(size=20),
        coloraxis_colorbar=dict(
            title=dict(
                text="Roční náklady [Kč]",
                side="right"
            ),
            thickness=18,
            x=1.02
        ),
        margin=dict(l=60, r=30, t=60, b=60)
    )

    return fig_heat_naklad

def vytvor_graf_leto_vs_zima(soubor_spotreby):
    pvgis_data = nacti_PVGIS(2022)
    spotreby_data = nacti_spotreby_bez_FVE(soubor_spotreby)

    pvgis_data.columns = ["time", "P"]
    pvgis_data["HourEnd"] = pvgis_data["time"] + pd.Timedelta(hours=1)
    pvgis_data = pvgis_data.sort_values("HourEnd").head(8760).reset_index(drop=True)

    hourend_2025 = pd.date_range("2025-01-01 01:00:00", periods=8760, freq="h")
    pvgis_data["HourEnd"] = hourend_2025

    spojene = pd.merge(
        pvgis_data[["HourEnd", "P"]],
        spotreby_data[["HourEnd", "Spotreba_kWh"]],
        on="HourEnd",
        how="inner"
    )

    spojene["datum"] = spojene["HourEnd"].dt.date
    spojene["hodina"] = spojene["HourEnd"].dt.hour
    spojene["vyroba_kWh_kWp"] = spojene["P"] / 1000.0

    leto_mask = (
        (spojene["datum"] >= pd.to_datetime("2025-06-21").date())
        & (spojene["datum"] <= pd.to_datetime("2025-09-22").date())
    )

    zima_mask = (
        (spojene["datum"] <= pd.to_datetime("2025-03-20").date())
        | (spojene["datum"] >= pd.to_datetime("2025-12-21").date())
    )

    prumer_leto = (
        spojene[leto_mask]
        .groupby("hodina", as_index=False)[["vyroba_kWh_kWp", "Spotreba_kWh"]]
        .mean()
    )

    prumer_zima = (
        spojene[zima_mask]
        .groupby("hodina", as_index=False)[["vyroba_kWh_kWp", "Spotreba_kWh"]]
        .mean()
    )

    vse_hodiny = pd.DataFrame({"hodina": range(24)})
    prumer_leto = vse_hodiny.merge(prumer_leto, on="hodina", how="left").fillna(0)
    prumer_zima = vse_hodiny.merge(prumer_zima, on="hodina", how="left").fillna(0)

    hodiny = vse_hodiny["hodina"].astype(str)

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=hodiny,
            y=prumer_leto["vyroba_kWh_kWp"],
            mode="lines+markers",
            name="Léto",
            line=dict(color="#EF553B"),
            xaxis="x",
            yaxis="y",
        )
    )

    fig.add_trace(
        go.Scatter(
            x=hodiny,
            y=prumer_zima["vyroba_kWh_kWp"],
            mode="lines+markers",
            name="Zima",
            line=dict(color="#636efa"),
            xaxis="x",
            yaxis="y",
        )
    )

    fig.add_trace(
        go.Scatter(
            x=hodiny,
            y=prumer_leto["Spotreba_kWh"],
            mode="lines+markers",
            name="Léto – spotřeba",
            line=dict(color="#EF553B", dash="dot"),
            showlegend=False,
            xaxis="x2",
            yaxis="y2",
        )
    )

    fig.add_trace(
        go.Scatter(
            x=hodiny,
            y=prumer_zima["Spotreba_kWh"],
            mode="lines+markers",
            name="Zima – spotřeba",
            line=dict(color="#636efa", dash="dot"),
            showlegend=False,
            xaxis="x2",
            yaxis="y2",
        )
    )

    fig.update_layout(
        title="Léto vs zima: modelovaná solární výroba a spotřeba vaší domácnosti během dne",
        title_x=0.0,
        title_font=dict(size=20),
        xaxis=dict(
            anchor="y",
            domain=[0.0, 1.0],
            showticklabels=False,
            type="category",
        ),
        yaxis=dict(
            anchor="x",
            domain=[0.55, 1.0],
            title_text="Výroba FVE [kWh/kWp]",
        ),
        xaxis2=dict(
            anchor="y2",
            domain=[0.0, 1.0],
            title_text="Hodina dne",
            type="category",
        ),
        yaxis2=dict(
            anchor="x2",
            domain=[0.0, 0.45],
            title_text="Spotřeba domácnosti [kWh]",
        ),
        legend=dict(title="Období"),
        margin=dict(l=60, r=40, t=60, b=60),
    )

    return fig



