def simulace(df_input, S_kWp, B_kWh,
             ucinnost_nabijeni=0.95,
             ucinnost_vybijeni=0.95,
             max_vykon_baterie_kW=None):
    # připrava vstupních dat: hodiny roku, výroba na 1 kWp a spotřebu
    dfr = df_input[["HourEnd", "E_FVE_1kWp_kWh", "Spotreba_kWh"]].copy()
    # přepočet na výrobu pro zvolený výkon FVE (3–10 kWp)
    dfr["E_FVE_kWh"] = dfr["E_FVE_1kWp_kWh"] * S_kWp

    # počáteční stav nabití baterie
    soc = 0.0
    soc_max = float(B_kWh)
    # případný limit výkonu baterie v kW (za hodinu v kWh)
    limit_kWh = (max_vykon_baterie_kW * 1.0) if max_vykon_baterie_kW is not None else None

    # akumulace ročních výsledků
    vlastni_FVE_spotreba = 0.0
    do_baterie = 0.0
    z_baterie = 0.0
    nakup = 0.0
    prodej = 0.0

    celkova_spotreba = float(dfr["Spotreba_kWh"].sum())

    # hodinový průchod celým rokem (8760 hodin)
    for index_radku, radek in dfr.iterrows():
        spotreba = float(radek["Spotreba_kWh"])
        PV = float(radek["E_FVE_kWh"])

        # 1) přímá spotřeba z FVE
        primy_odber = min(spotreba, PV)
        vlastni_FVE_spotreba += primy_odber
        spotreba -= primy_odber
        PV -= primy_odber

        # 2) nabíjení baterie z přebytků výroby
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

        # 3) vybíjení baterie při nedostatku výroby
        if spotreba > 0 and soc > 0:
            energie_k_dispozici = soc * ucinnost_vybijeni
            vybito = min(spotreba, energie_k_dispozici)
            if limit_kWh is not None:
                vybito = min(vybito, limit_kWh)
            spotreba -= vybito
            z_baterie += vybito
            soc -= vybito / ucinnost_vybijeni

        # 4) přetoky do sítě a nákup ze sítě
        if PV > 0:
            prodej += PV
        if spotreba > 0:
            nakup += spotreba

    # agregované roční výsledky – vstup pro ekonomický model
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
            (1.0 - float(nakup) / max(celkova_spotreba, 1e-9)) * 100.0, 2),
        "podil_pretoku_pct": round(float(prodej) / 
                      max(float(dfr["E_FVE_kWh"].sum()), 1e-9) * 100.0, 2 )}
