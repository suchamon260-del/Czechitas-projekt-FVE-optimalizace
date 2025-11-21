import pandas as pd

def nacti_PVGIS(year):
    df = pd.read_csv('PVGIS.csv')

    df = df.iloc[:, :2]

    df['time'] = pd.to_datetime(df['time'], format='%Y%m%d:%H%M')

    df['time'] = df['time'].dt.floor('h')

    start_date = pd.Timestamp(str(year) + "-01-01 00:00:00")
    end_date   = pd.Timestamp(str(year+1) + "-01-01 00:00:00")
                            
    df = df[(df.iloc[:, 0] >= start_date) & (df.iloc[:, 0] < end_date)]
    df = df.head(8760)

    return df
