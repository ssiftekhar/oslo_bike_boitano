import requests
import pandas as pd
from datetime import datetime
import sqlite3
import os
from pathlib import Path

MAIN_URL = "https://oslo-bike-api-13322556367.europe-west1.run.app"
ENDEPUNKTER = ["station_information", "station_status", "pass_sales"]
DB_FIL = "oslo_bike.db"

try:
    BASE_DIR = Path(__file__).resolve().parent
except NameError:
    BASE_DIR = Path.cwd()
    

def hent_data(endepunkt):
    url = f"{MAIN_URL}/{endepunkt}"
    print(f"Henter data fra: {url}")
    return requests.get(url).json()

def opprette_dataframes(json_dict):
    data = {}

    for navn, innhold in json_dict.items():
        print(f"\n Oppretter dataframe for: {navn}")

        if navn in ["station_status", "station_information"]:
            df = pd.DataFrame(innhold["data"]["stations"])
            last_updated = innhold["last_updated"]
            ts = pd.to_datetime(last_updated, unit="s")

            df["last_updated"] = ts.isoformat()
            print(f" last_updated hentet fra api-et: {ts}")

        elif navn == "pass_sales":
            # Denne har ikke last_updated og er rett ut en liste
            df = pd.DataFrame(innhold["data"])
            df["purchase_timestamp"] = pd.to_datetime(
                df["purchase_timestamp"]).dt.strftime("%Y-%m-%d %H:%M:%S")
            now = datetime.utcnow().isoformat()
            df["last_updated"] = now
            
            print(f" last_updated satt til nåværende tid: {now}")

        else:
            print(f" Uventet struktur for {navn}. Hopper over")
            continue

        print(f" Rader i {navn}: {len(df)}")
        data[navn] = df

    return data



def lag_tabeller(cursor):
    print("\n Oppretter tabeller i MySQL (hvis de ikke finnes)..")

    tabeller = {}

    tabeller["station_information"] = """
    CREATE TABLE IF NOT EXISTS station_information (
        station_id VARCHAR(20) PRIMARY KEY,
        name VARCHAR(200),
        address VARCHAR(200),
        lat DOUBLE,
        lon DOUBLE,
        capacity INT,
        last_updated DATETIME
    );
    """
    
    tabeller["station_status"] = """
    CREATE TABLE IF NOT EXISTS station_status (
        status_id INTEGER PRIMARY KEY AUTOINCREMENT,
        station_id VARCHAR(20),
        is_installed INT,
        can_rent INT,
        can_return INT,
        num_bikes_available INT,
        num_docks_available INT,
        last_updated DATETIME,
        FOREIGN KEY (station_id) REFERENCES station_information(station_id)
    );
    """

    tabeller["pass_sales"] = """
    CREATE TABLE IF NOT EXISTS pass_sales (
        transaction_id VARCHAR(200) PRIMARY KEY,
        user_id VARCHAR(200),
        pass_type VARCHAR(50),
        source VARCHAR(50),
        RelatedBikeStationId VARCHAR(20),
        price_nok DOUBLE,
        purchase_timestamp DATETIME,
        last_updated DATETIME
    );
    """

    for name, ddl in tabeller.items():
        try:
            print(f"Lager tabell: {name}")
            cursor.execute(ddl)
        except Exception as feil:
            print(f"En feil dukket opp: {feil}")

    print("Alle tabeller sjekket/opprettet.")
    

def populer_data(cursor, df, tabell):
    print(f"\n Lagrer data i: {tabell}")

    df = df.where(df.notnull(), None)

    kolonner = list(df.columns)
    placeholders = ", ".join(["?"] * len(kolonner))
    kolonne_string = ", ".join(kolonner)

    if tabell == "station_status":
        sql = f"""
        INSERT INTO {tabell} ({kolonne_string})
        VALUES ({placeholders});
        """
    else:
        oppdater_data = ", ".join(
            f"{col} = excluded.{col}" for col in kolonner[1:]
        )

        sql = f"""
        INSERT INTO {tabell} ({kolonne_string})
        VALUES ({placeholders})
        ON CONFLICT({kolonner[0]}) DO UPDATE SET
        {oppdater_data};
        """

    cursor.executemany(sql, df.values.tolist())
    print(f"{len(df)} rader lagret/oppdatert i {tabell}")
    
    
def beregn_bruk_bevegelse(cursor):
    print("\n Beregner bruk av sykkelstasjoner basert på sykkelbevegelser")

    sql = """
    WITH changes AS (
        SELECT
            station_id,
            last_updated,
            num_bikes_available,
            LAG(num_bikes_available) OVER (
                PARTITION BY station_id
                ORDER BY last_updated
            ) AS prev_bikes
        FROM station_status
    )
    SELECT
        station_id,
        SUM(ABS(num_bikes_available - prev_bikes)) AS totale_bevegelser
    FROM changes
    WHERE prev_bikes IS NOT NULL
    GROUP BY station_id
    ORDER BY totale_bevegelser DESC;
    """

    cursor.execute(sql)
    rows = cursor.fetchall()

    if not rows:
        print(" Ingen bevegelsesdata enda (trenger minst to kjøringer).")
        return

    print("\n Topp 10 stasjoner målt i total bevegelse (inn/ut av sykler):")
    for station_id, total in rows[:10]:
        print(f"  - Stasjon {station_id}: {total} bevegelser")

    return rows

    
def main():
    print("Starter innhenting og lagring av Oslo Bike dataen")
    
    if not os.path.exists(DB_FIL):
        print(f"Oppretter ny databasefil: {DB_FIL}")
    else:
        print(f"Bruker eksisterende databasefil: {DB_FIL}")
        
    conn = sqlite3.connect(DB_FIL)
    cursor = conn.cursor()
    
    lag_tabeller(cursor)
    
    raa_data = {
        "station_information": hent_data("station_information"),
        "station_status": hent_data("station_status"),
        "pass_sales": hent_data("pass_sales")
        }
    
    oslo_bike_dfs = opprette_dataframes(raa_data)
    
    populer_data(cursor, oslo_bike_dfs["station_information"], "station_information")
    populer_data(cursor, oslo_bike_dfs["station_status"], "station_status")
    populer_data(cursor, oslo_bike_dfs["pass_sales"], "pass_sales")
    
    beregn_bruk_bevegelse(cursor)

    conn.commit()
    conn.close()
    print("\n Ferdig med kjøringen! Alle data lagret i SQLite-basen oslo_bike.db.")

if __name__ == "__main__":

    main()
