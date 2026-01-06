import pandas as pd
def clean_weather_data(df):
    if df.empty:
        print("No data to clean.")
        return df

    df["temperature"] = pd.to_numeric(df["temperature"], errors="coerce")
    df.dropna(inplace=True)

    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df.dropna(inplace=True)

    return df
