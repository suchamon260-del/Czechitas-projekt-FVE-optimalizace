import pandas as pd

def nacti_spotreby_bez_FVE(file_spotreby):
    df = pd.read_csv(file_spotreby, sep=";", engine="python", encoding="cp1250")
    df_original = df.copy()
    df = df.rename(columns={"+A/3000010347 [kW]": "Spotreba_kW"})
    df["Datum"] = pd.to_datetime(df["Datum"], format="%d.%m.%Y %H:%M:%S", errors="coerce")

    df["HourEnd"] = df["Datum"].dt.floor("h") + pd.Timedelta(hours=1)

    df = df.drop(columns=["Status", "Unnamed: 3"], errors="ignore")
    kW = df["Spotreba_kW"].astype(str)
    df["Spotreba_kW"] = pd.to_numeric(kW, errors="coerce")
    df["Spotreba_kWh_15min"] = df["Spotreba_kW"] * 0.25
    
    hodinova_spotreba = (df.groupby("HourEnd", as_index=False)["Spotreba_kWh_15min"]
          .sum()
          .rename(columns={"Spotreba_kWh_15min": "Spotreba_kWh"})
          .round(3))

    hourend_grid = pd.date_range("2025-01-01 01:00:00", periods=8760, freq="h")
    Spotreby_vystupni_soubor = pd.DataFrame({"HourEnd": hourend_grid})

    hodinova_spotreba_2025 = hodinova_spotreba[hodinova_spotreba["HourEnd"].between(pd.Timestamp("2025-01-01 01:00:00"),
                                                     pd.Timestamp("2026-01-01 00:00:00"))]
    q4_2024 = hodinova_spotreba[hodinova_spotreba["HourEnd"].between(pd.Timestamp("2024-10-01 01:00:00"),
                                                   pd.Timestamp("2025-01-01 00:00:00"))].copy()
    q4_2024["HourEnd"] = q4_2024["HourEnd"] + pd.DateOffset(years=1)

    spotreba_2025_final = (pd.concat([hodinova_spotreba_2025, q4_2024], axis=0)
        .sort_values("HourEnd")
        .drop_duplicates(subset=["HourEnd"], keep="first"))

    Spotreby_vystupni_soubor = Spotreby_vystupni_soubor.merge(spotreba_2025_final, on="HourEnd", how="left")
    Spotreby_vystupni_soubor["Spotreba_kWh"] = Spotreby_vystupni_soubor["Spotreba_kWh"].interpolate(limit_direction="both").round(3)

    return Spotreby_vystupni_soubor[["HourEnd", "Spotreba_kWh"]]

"""vystup = nacti_spotreby_bez_FVE()
vystup.to_csv("Spotreby_bez_FVE_2025.csv", index=False, encoding="utf-8")"""

