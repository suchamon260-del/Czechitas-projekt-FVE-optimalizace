import pandas as pd
from PVGIS import nacti_PVGIS
from Spotreby_bez_FVE import nacti_spotreby_bez_FVE

def spocitej_vysledky(file_spotreby):
    pvgis_data = nacti_PVGIS(2022)
    spotreby_data = nacti_spotreby_bez_FVE(file_spotreby)

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

    print(spojene.head(5))

    df = spojene[["HourEnd", "P", "Spotreba_kWh"]].copy()
    df["E_FVE_1kWp_kWh"] = ((df["P"] / 1000.0) * 1.0).round(3)
    df = df[["HourEnd", "E_FVE_1kWp_kWh", "Spotreba_kWh"]]
    df.to_csv("sloucena_data.csv", index=False, encoding="utf-8")

    def simulace(df_input, S_kWp, B_kWh,
                ucinnost_nabijeni=0.95,
                ucinnost_vybijeni=0.95,
                max_vykon_baterie_kW=None):
        dfr = df_input[["HourEnd", "E_FVE_1kWp_kWh", "Spotreba_kWh"]].copy()
        dfr["E_FVE_kWh"] = dfr["E_FVE_1kWp_kWh"] * S_kWp

        soc = 0.0
        soc_max = float(B_kWh)
        limit_kWh = (max_vykon_baterie_kW * 1.0) if max_vykon_baterie_kW is not None else None

        vlastni_FVE_spotreba = 0.0
        do_baterie = 0.0
        z_baterie = 0.0
        nakup = 0.0
        prodej = 0.0

        celkova_spotreba = float(dfr["Spotreba_kWh"].sum())

        for index_radku, radek in dfr.iterrows():
            spotreba = float(radek["Spotreba_kWh"])
            PV = float(radek["E_FVE_kWh"])

            primy_odber = min(spotreba, PV)
            vlastni_FVE_spotreba += primy_odber
            spotreba -= primy_odber
            PV -= primy_odber

            if PV > 0 and soc_max > 0:
                volno = soc_max - soc
                if volno > 0:
                    nabiti_teoreticke = PV * ucinnost_nabijeni
                    nabiti_realne = min(nabiti_teoreticke, volno)
                    if limit_kWh is not None:
                        nabiti_realne = min(nabiti_realne, limit_kWh)
                    soc += nabiti_realne
                    do_baterie += nabiti_realne
                    PV -= nabiti_realne / ucinnost_nabijeni

            if spotreba > 0 and soc > 0:
                energie_k_dispozici = soc * ucinnost_vybijeni
                vybito = min(spotreba, energie_k_dispozici)
                if limit_kWh is not None:
                    vybito = min(vybito, limit_kWh)
                spotreba -= vybito
                z_baterie += vybito
                soc -= vybito / ucinnost_vybijeni

            if PV > 0:
                prodej += PV

            if spotreba > 0:
                nakup += spotreba

        return {
            "vykon_FVE_instalovany_kWp": float(S_kWp),
            "kapacita_baterie_kWh": float(B_kWh),
            "spotreba_celkova_kWh": round(celkova_spotreba, 3),
            "vyroba_FVE_celkova_kWh": round(float(dfr["E_FVE_kWh"].sum()), 3),
            "vlastni_spotreba_z_FVE_kWh": round(float(vlastni_FVE_spotreba), 3),
            "E_do_baterie_kWh": round(float(do_baterie), 3),
            "E_z_baterie_kWh": round(float(z_baterie), 3),
            "import_ze_site_kWh": round(float(nakup), 3),
            "export_do_site_kWh": round(float(prodej), 3),
            "sobestacnost_pct": round(
                (1.0 - float(nakup) / max(celkova_spotreba, 1e-9)) * 100.0, 2
            ),
            "podil_pretoku_pct": round(
                float(prodej) / max(float(dfr["E_FVE_kWh"].sum()), 1e-9) * 100.0, 2
            ),
        }

    def rocni_uspora(
        rocni_souhrn,
        cena_nakup_Kc_za_kWh=7.0,
        cena_vykup_Kc_za_kWh=1.5,
        fixni_poplatky_FVE_Kc_rok=2000.0,
        investice_po_dotaci=0.0,
        zivotnost_let=30
    ):
        spotreba = float(rocni_souhrn.get("spotreba_celkova_kWh", 0.0))
        odber = float(rocni_souhrn.get("import_ze_site_kWh", 0.0))
        pretok = float(rocni_souhrn.get("export_do_site_kWh", 0.0))

        rocni_amortizace = investice_po_dotaci / zivotnost_let

        naklad_bez_FVE = spotreba * cena_nakup_Kc_za_kWh

        naklad_s_FVE = (
            odber * cena_nakup_Kc_za_kWh
            - pretok * cena_vykup_Kc_za_kWh
            + fixni_poplatky_FVE_Kc_rok
            + rocni_amortizace
        )

        uspora = naklad_bez_FVE - naklad_s_FVE
        return float(round(uspora, 0))

    def vypocitej_dotaci_NZU(S_kWp, B_kWh):
        if B_kWh is None or B_kWh <= 0:
            return 0.0
        cena_dotace_FVE = S_kWp * 10_000
        cena_dotace_baterie = B_kWh * 10_000
        celkova_dotace = cena_dotace_FVE + cena_dotace_baterie
        if celkova_dotace > 140_000:
            celkova_dotace = 140_000
        return celkova_dotace

    def optimalizace(
        df_input,
        mrizka_vykonu_kWp,
        mrizka_baterie_kWh,
        cena_nakup_Kc_za_kWh=7.0,
        cena_vykup_Kc_za_kWh=1.5,
        fixni_poplatky_FVE_Kc_rok=2000.0,
        ucinnost_nabijeni=0.95,
        ucinnost_vybijeni=0.95,
        max_vykon_baterie_kW=None,
        zivotnost_let=30
    ):
        vysledky_radky = []
        kombinace = len(mrizka_vykonu_kWp) * len(mrizka_baterie_kWh)
        print(f"Počet kombinací: {kombinace}")

        for S_kWp in mrizka_vykonu_kWp:
            for B_kWh in mrizka_baterie_kWh:
                lokalni_max_vykon = max_vykon_baterie_kW
                if lokalni_max_vykon is None and B_kWh > 0:
                    lokalni_max_vykon = 0.5 * float(B_kWh)

                metriky = simulace(
                    df_input=df_input,
                    S_kWp=S_kWp,
                    B_kWh=B_kWh,
                    ucinnost_nabijeni=ucinnost_nabijeni,
                    ucinnost_vybijeni=ucinnost_vybijeni,
                    max_vykon_baterie_kW=lokalni_max_vykon
                )

                if S_kWp <= 4:
                    cena_za_kWp = 35_000.0
                elif S_kWp <= 8:
                    cena_za_kWp = 32_000.0
                else:
                    cena_za_kWp = 30_000.0

                cena_FVE = float(S_kWp) * float(cena_za_kWp)

                if B_kWh is None or B_kWh <= 0:
                    cena_baterie_1ks = 0.0
                else:
                    if B_kWh <= 7:
                        cena_za_kWh = 14_000.0
                    elif B_kWh <= 12:
                        cena_za_kWh = 12_000.0
                    elif B_kWh <= 20:
                        cena_za_kWh = 10_000.0
                    else:
                        cena_za_kWh = 9_000.0
                    cena_baterie_1ks = float(B_kWh) * float(cena_za_kWh)

                celkova_investice = cena_FVE + cena_baterie_1ks
                dotace = vypocitej_dotaci_NZU(S_kWp, B_kWh)

                if celkova_investice > 0:
                    podil_FVE = cena_FVE / celkova_investice
                    podil_baterie = cena_baterie_1ks / celkova_investice
                else:
                    podil_FVE = 0.0
                    podil_baterie = 0.0

                dotace_FVE = dotace * podil_FVE
                dotace_baterie = dotace * podil_baterie

                investice_FVE_po_dotaci = max(cena_FVE - dotace_FVE, 0.0)
                investice_baterie_po_dotaci = max(cena_baterie_1ks - dotace_baterie, 0.0)

                investice_po_dotaci = investice_FVE_po_dotaci + investice_baterie_po_dotaci

                zivotnost_FVE_let = 30.0
                zivotnost_baterie_let = 12.0

                rocni_amortizace_FVE = (
                    investice_FVE_po_dotaci / zivotnost_FVE_let
                    if investice_FVE_po_dotaci > 0 else 0.0
                )
                rocni_amortizace_baterie = (
                    investice_baterie_po_dotaci / zivotnost_baterie_let
                    if investice_baterie_po_dotaci > 0 else 0.0
                )
                rocni_amortizace_celkova = rocni_amortizace_FVE + rocni_amortizace_baterie

                if investice_po_dotaci > 0 and rocni_amortizace_celkova > 0:
                    zivotnost_efektivni = investice_po_dotaci / rocni_amortizace_celkova
                else:
                    zivotnost_efektivni = zivotnost_let

                # uspora po amortizaci (doplnkova info)
                uspora_po_amortizaci = rocni_uspora(
                    metriky,
                    cena_nakup_Kc_za_kWh=cena_nakup_Kc_za_kWh,
                    cena_vykup_Kc_za_kWh=cena_vykup_Kc_za_kWh,
                    fixni_poplatky_FVE_Kc_rok=fixni_poplatky_FVE_Kc_rok,
                    investice_po_dotaci=investice_po_dotaci,
                    zivotnost_let=zivotnost_efektivni
                )

                spotreba = float(metriky.get("spotreba_celkova_kWh", 0.0))
                odber = float(metriky.get("import_ze_site_kWh", 0.0))
                pretok = float(metriky.get("export_do_site_kWh", 0.0))

                naklad_bez_FVE = spotreba * cena_nakup_Kc_za_kWh
                naklad_s_FVE_bez_amortizace = (
                    odber * cena_nakup_Kc_za_kWh
                    - pretok * cena_vykup_Kc_za_kWh
                    + fixni_poplatky_FVE_Kc_rok
                )
                uspora_bez_amortizace = naklad_bez_FVE - naklad_s_FVE_bez_amortizace
                uspora_bez_amortizace = float(round(uspora_bez_amortizace, 0))

                Rocni_naklad = rocni_amortizace_celkova + naklad_s_FVE_bez_amortizace

                metriky["Rocni_naklad_Kc"] = int(round(Rocni_naklad))
                # hlavni ekonomicka uspora = bez amortizace
                metriky["Uspora_Kc"] = float(round(uspora_bez_amortizace, 0))
                # doplnkove uspora po amortizaci
                metriky["Rocni_uspora_po_amortizaci_Kc"] = float(round(uspora_po_amortizaci, 0))
                metriky["Investice_Kc"] = int(round(celkova_investice))
                metriky["Dotace_NZU_Kc"] = int(round(dotace))
                metriky["Investice_po_dotaci_Kc"] = int(round(investice_po_dotaci))

                if metriky["Uspora_Kc"] > 0:
                    metriky["Navratnost_roky"] = round(
                        investice_po_dotaci / metriky["Uspora_Kc"], 1)
                else:
                    metriky["Navratnost_roky"] = None

                vysledky_radky.append(metriky)

        vysledky_optimalizace = (
            pd.DataFrame(vysledky_radky)
            .sort_values("Uspora_Kc", ascending=False)
            .reset_index(drop=True)
        )

        vysledky_optimalizace.to_csv(
            "vysledky_optimalizace.csv",
            index=False,
            encoding="utf-8", sep=","
        )

        return vysledky_optimalizace

    mrizka_vykonu_FVE_kWp = [3, 4, 5, 6, 7, 8, 9, 10]
    mrizka_kapacity_baterie_kWh = [0, 5, 10, 15, 20]

    vysledek = optimalizace(
        df,
        mrizka_vykonu_FVE_kWp,
        mrizka_kapacity_baterie_kWh,
        cena_nakup_Kc_za_kWh=7.0,
        cena_vykup_Kc_za_kWh=1.5,
        fixni_poplatky_FVE_Kc_rok=2000.0,
        ucinnost_nabijeni=0.95,
        ucinnost_vybijeni=0.95,
        max_vykon_baterie_kW=None,
        zivotnost_let=30
    )
    return vysledek
