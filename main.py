import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import random


def create_mock_data():
    """Generates random data for testing if web scraping fails."""
    print("⚠️ Warning: Could not fetch real data, generating 'Mock Data' for testing...")
    dates = [datetime.today() - timedelta(days=x) for x in range(30)]
    temps = [random.randint(-5, 35) for _ in range(30)]
    cities = ["İstanbul", "Ankara", "İzmir"] * 10  # Repeat cities for mock data
   
    date_strings = [d.strftime("%Y-%m-%d") for d in dates]
    return pd.DataFrame({
        "city": cities,
        "date": date_strings, 
        "temperature": temps
    })

def scrape_weather():
    # Import the updated webscraping function
    from webscraping import scrape_weather as ws_scrape_weather
    
    try:
        df = ws_scrape_weather()
        if df.empty:
            return create_mock_data()
        return df
    except Exception as e:
        print(f"Error in web scraping: {e}")
        return create_mock_data() 


def clean_weather_data(df):
    if df.empty:
        print("No data to clean.")
        return df

    
    df["temperature"] = pd.to_numeric(df["temperature"], errors="coerce")
    
    
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    
    
    original_len = len(df)
    df.dropna(inplace=True)
    
    if len(df) < original_len:
        print(f"{original_len - len(df)} invalid rows removed.")

    
    df.sort_values(by="date", inplace=True)
    
    return df


def statistical_summary(df):
    print("\n--- Statistical Summary ---")
    print(f"Total data points: {len(df)}")
    
    if 'city' in df.columns:
        print(f"Cities covered: {df['city'].nunique()}")
        print(f"Cities: {', '.join(df['city'].unique())}")
        
        # Show statistics by city
        print("\n--- Temperature Statistics by City ---")
        city_stats = df.groupby('city')['temperature'].agg(['mean', 'min', 'max', 'count'])
        print(city_stats.round(2))
    
    print(f"\nOverall Mean Temperature: {df['temperature'].mean():.2f}")
    print(f"Overall Min Temperature: {df['temperature'].min()}")
    print(f"Overall Max Temperature: {df['temperature'].max()}")
    
    print("\nQuartiles:")
    print(df["temperature"].quantile([0.25, 0.5, 0.75]))

def detect_anomalies(df):
    
    df["rolling_avg"] = df["temperature"].rolling(window=3).mean()

    mean = df["temperature"].mean()
    std = df["temperature"].std()

    
    conditions = [
        (df["temperature"] > mean + 2 * std),
        (df["temperature"] < mean - 2 * std)
    ]
    choices = ["High anomaly", "Low anomaly"]
    
    df["anomaly"] = np.select(conditions, choices, default="Normal")

    
    anomaly_count = df[df["anomaly"] != "Normal"].shape[0]
    print(f"\nNumber of anomalies detected: {anomaly_count}")
    
    return df


def classify_weather(df):
    """
    Classifies the day based on temperature ranges.
    """
    conditions = [
        (df["temperature"] < 0),
        (df["temperature"] >= 0) & (df["temperature"] < 10),
        (df["temperature"] >= 10) & (df["temperature"] < 20),
        (df["temperature"] >= 20) & (df["temperature"] < 30),
        (df["temperature"] >= 30)
    ]
    choices = ["Very Cold", "Cold", "Mild", "Hot", "Very Hot"]
    
    df["condition"] = np.select(conditions, choices, default="Unknown")
    return df


def visualize(df):
    sns.set_theme(style="whitegrid") 

    # Temperature trend over time
    plt.figure(figsize=(12, 6))
    if 'city' in df.columns:
        # Plot separate lines for each city
        for city in df['city'].unique()[:10]:  # Limit to first 10 cities for readability
            city_data = df[df['city'] == city]
            plt.plot(pd.to_datetime(city_data["date"]), city_data["temperature"], 
                    marker='o', linestyle='-', label=city)
        plt.legend()
        plt.title("Daily Temperature Change by City")
    else:
        plt.plot(pd.to_datetime(df["date"]), df["temperature"], marker='o', linestyle='-', color='b')
        plt.title("Daily Temperature Change")
    
    plt.xlabel("Date")
    plt.ylabel("Temperature (°C)")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

    # Temperature distribution
    plt.figure(figsize=(8, 5))
    sns.boxplot(y=df["temperature"], color='lightblue')
    plt.title("Temperature Distribution & Outliers")
    plt.show()

    # City comparison if available
    if 'city' in df.columns and df['city'].nunique() > 1:
        plt.figure(figsize=(10, 6))
        sns.boxplot(data=df, x="city", y="temperature")
        plt.title("Temperature Distribution by City")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()

    # Anomalies scatter plot
    if 'anomaly' in df.columns:
        plt.figure(figsize=(10, 6))
        sns.scatterplot(
            data=df,
            x=pd.to_datetime(df["date"]),
            y="temperature",
            hue="anomaly",
            palette={"Normal": "green", "High anomaly": "red", "Low anomaly": "blue"},
            style="anomaly",
            s=100
        )
        plt.title("Temperature Anomalies")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()
    
    # Weather condition distribution
    if 'condition' in df.columns:
        plt.figure(figsize=(8, 5))
        sns.countplot(x="condition", data=df, order=["Very Cold", "Cold", "Mild", "Hot", "Very Hot"])
        plt.title("Weather Condition Distribution")
        plt.xticks(rotation=45)
        plt.show()


def main():
    print("Starting program...")
    
    
    df = scrape_weather()
    if df.empty:
        print("Error: Could not collect data. Exiting.")
        return
    df = clean_weather_data(df)
    statistical_summary(df)
    df = detect_anomalies(df)
    df = classify_weather(df)
    
    print("\nProcessed Data Sample (First 10 rows):")
    print(df.head(10))

    
    print("\nGenerating plots...")
    visualize(df)
    print("Process completed.")

if __name__ == "__main__":
    main()