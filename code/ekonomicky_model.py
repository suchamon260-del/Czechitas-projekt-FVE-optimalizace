# výpočet roční úspory včetně amortizace investice
def rocni_uspora(
        rocni_souhrn,
        cena_nakup_Kc_za_kWh=7.0,
        cena_vykup_Kc_za_kWh=1.5,
        fixni_poplatky_FVE_Kc_rok=2000.0,
        investice_po_dotaci=0.0,
        zivotnost_let=30):

        # spotřeba domácnosti a toky energie ze / do sítě
        spotreba = float(rocni_souhrn.get("spotreba_celkova_kWh", 0.0))
        odber = float(rocni_souhrn.get("import_ze_site_kWh", 0.0))
        pretok = float(rocni_souhrn.get("export_do_site_kWh", 0.0))

        # roční amortizace investice (FVE + baterie) přes danou životnost
        rocni_amortizace = investice_po_dotaci / zivotnost_let

        # náklady bez FVE (z distribuční sítě)
        naklad_bez_FVE = spotreba * cena_nakup_Kc_za_kWh

        # náklady s FVE: nákup ze sítě – příjem z přetoků + fixní poplatky + amortizace
        naklad_s_FVE = (
            odber * cena_nakup_Kc_za_kWh
            - pretok * cena_vykup_Kc_za_kWh
            + fixni_poplatky_FVE_Kc_rok
            + rocni_amortizace)

        # roční úspora (kladná = FVE se ekonomicky vyplácí)
        uspora = naklad_bez_FVE - naklad_s_FVE
        return float(round(uspora, 0))

# výpočet dotace z programu Nová zelená úsporám (zjednodušený model)
def vypocitej_dotaci_NZU(S_kWp, B_kWh):
        # bez baterie není v modelu uvažována dotace
        if B_kWh is None or B_kWh <= 0:
            return 0.0

        # dotace za FVE a za baterii (na kWp a kWh)
        cena_dotace_FVE = S_kWp * 10_000
        cena_dotace_baterie = B_kWh * 10_000
        celkova_dotace = cena_dotace_FVE + cena_dotace_baterie

        # maximální výše dotace podle pravidel NZÚ
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
        zivotnost_let=30):

        vysledky_radky = []
        kombinace = len(mrizka_vykonu_kWp) * len(mrizka_baterie_kWh)
        print(f"Počet kombinací: {kombinace}")

        # projdeme všechny kombinace výkonu FVE a kapacity baterie
        for S_kWp in mrizka_vykonu_kWp:
            for B_kWh in mrizka_baterie_kWh:
                # volitelný limit výkonu baterie (kW ~ kWh/hod)
                lokalni_max_vykon = max_vykon_baterie_kW
                if lokalni_max_vykon is None and B_kWh > 0:
                    lokalni_max_vykon = 0.5 * float(B_kWh)

                # hodinová simulace pro danou kombinaci
                metriky = simulace(
                    df_input=df_input,
                    S_kWp=S_kWp,
                    B_kWh=B_kWh,
                    ucinnost_nabijeni=ucinnost_nabijeni,
                    ucinnost_vybijeni=ucinnost_vybijeni,
                    max_vykon_baterie_kW=lokalni_max_vykon)

                # odstupňované jednotkové ceny FVE podle instalovaného výkonu
                if S_kWp <= 4:
                    cena_za_kWp = 35_000.0
                elif S_kWp <= 8:
                    cena_za_kWp = 32_000.0
                else:
                    cena_za_kWp = 30_000.0

                cena_FVE = float(S_kWp) * float(cena_za_kWp)

                # odstupňovaná cena baterie podle kapacity
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

                # celková investice před dotací a dotace z NZÚ
                celkova_investice = cena_FVE + cena_baterie_1ks
                dotace = vypocitej_dotaci_NZU(S_kWp, B_kWh)

                # rozdělení dotace mezi FVE a baterii podle podílu na investici
                if celkova_investice > 0:
                    podil_FVE = cena_FVE / celkova_investice
                    podil_baterie = cena_baterie_1ks / celkova_investice
                else:
                    podil_FVE = 0.0
                    podil_baterie = 0.0

                dotace_FVE = dotace * podil_FVE
                dotace_baterie = dotace * podil_baterie

                # investice po odečtení dotace
                investice_FVE_po_dotaci = max(cena_FVE - dotace_FVE, 0.0)
                investice_baterie_po_dotaci = max(cena_baterie_1ks - dotace_baterie, 0.0)
                investice_po_dotaci = investice_FVE_po_dotaci + investice_baterie_po_dotaci

                # životnost FVE a baterie v letech (odlišná amortizace)
                zivotnost_FVE_let = 30.0
                zivotnost_baterie_let = 12.0

                # roční amortizace FVE a baterie
                rocni_amortizace_FVE = (
                    investice_FVE_po_dotaci / zivotnost_FVE_let
                    if investice_FVE_po_dotaci > 0 else 0.0
                )
                rocni_amortizace_baterie = (
                    investice_baterie_po_dotaci / zivotnost_baterie_let
                    if investice_baterie_po_dotaci > 0 else 0.0
                )
                rocni_amortizace_celkova = rocni_amortizace_FVE + rocni_amortizace_baterie

                # efektivní životnost z amortizace (pro výpočet roční úspory)
                if investice_po_dotaci > 0 and rocni_amortizace_celkova > 0:
                    zivotnost_efektivni = investice_po_dotaci / rocni_amortizace_celkova
                else:
                    zivotnost_efektivni = zivotnost_let

                # doplňková úspora: včetně amortizace (informativně)
                uspora_po_amortizaci = rocni_uspora(
                    metriky,
                    cena_nakup_Kc_za_kWh=cena_nakup_Kc_za_kWh,
                    cena_vykup_Kc_za_kWh=cena_vykup_Kc_za_kWh,
                    fixni_poplatky_FVE_Kc_rok=fixni_poplatky_FVE_Kc_rok,
                    investice_po_dotaci=investice_po_dotaci,
                    zivotnost_let=zivotnost_efektivni)

                # přepočet na roční náklady s / bez FVE
                spotreba = float(metriky.get("spotreba_celkova_kWh", 0.0))
                odber = float(metriky.get("import_ze_site_kWh", 0.0))
                pretok = float(metriky.get("export_do_site_kWh", 0.0))

                naklad_bez_FVE = spotreba * cena_nakup_Kc_za_kWh
                naklad_s_FVE_bez_amortizace = (
                    odber * cena_nakup_Kc_za_kWh
                    - pretok * cena_vykup_Kc_za_kWh
                    + fixni_poplatky_FVE_Kc_rok)

                # hlavní úspora – čistě provozní (bez amortizace)
                uspora_bez_amortizace = naklad_bez_FVE - naklad_s_FVE_bez_amortizace
                uspora_bez_amortizace = float(round(uspora_bez_amortizace, 0))

                # roční náklad včetně amortizace
                Rocni_naklad = rocni_amortizace_celkova + naklad_s_FVE_bez_amortizace

                # uložení ekonomických metrik
                metriky["Rocni_naklad_Kc"] = int(round(Rocni_naklad))
                metriky["Uspora_Kc"] = float(round(uspora_bez_amortizace, 0))  # hlavní úspora
                metriky["Rocni_uspora_po_amortizaci_Kc"] = float(round(uspora_po_amortizaci, 0))
                metriky["Investice_Kc"] = int(round(celkova_investice))
                metriky["Dotace_NZU_Kc"] = int(round(dotace))
                metriky["Investice_po_dotaci_Kc"] = int(round(investice_po_dotaci))

                # ekonomická návratnost v letech (jen pokud úspora > 0)
                if metriky["Uspora_Kc"] > 0:
                    metriky["Navratnost_roky"] = round(
                        investice_po_dotaci / metriky["Uspora_Kc"], 1)
                else:
                    metriky["Navratnost_roky"] = None

                vysledky_radky.append(metriky)

        # finální tabulka všech kombinací 
        vysledky_optimalizace = (
            pd.DataFrame(vysledky_radky)
            .sort_values("Uspora_Kc", ascending=False)
            .reset_index(drop=True))

        # uložení výsledků pro další analýzu a vizualizace
        vysledky_optimalizace.to_csv(
            "vysledky_optimalizace.csv",
            index=False,
            encoding="utf-8", sep=",")

        return vysledky_optimalizace
