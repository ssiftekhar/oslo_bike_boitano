# oslo_bike_boitano
ETL pipeline for Oslo Bike data om stasjoner og salg av pass

Denne applikasjonen henter data fra et mock-API for Oslo Bysykkel, transformerer datasettene til rene pandas‐dataframes og lagrer dem i en SQLite-relasjonsdatabase.
Løsningen er laget bruk av datanalytikere til å bygge innsikt for interessenter

**Prosjektet består av en enkel ETL-prosess:**

1. Extract – Data hentes fra tre API-endepunkter:

    - station_information
    - station_status
    - pass_sales

2. Transform

    - JSON konverteres til pandas-dataframes
    - last_updated fra API konverteres til datetime
    - For pass_sales genereres en egen last_updated med nåtid

3. Load

    - Tabeller opprettes i SQLite hvis de ikke finnes
    -Data skrives inn til db-filen
    - Dermed oppdateres eksisterende rader, og nye rader legges til

\
**Her er en enkel datamodell som viser Oslo Bike-dataen, og dens relasjoner:**

<img width="615" height="686" alt="datamodell oslo bike" src="https://github.com/user-attachments/assets/9406f267-a3e4-487e-ba2a-4b6bc5ff37f7" />


\
**Slik kjører du koden:**

1. Klon prosjektet

`git clone (https://github.com/ssiftekhar/oslo_bike_boitano)
cd oslo-bike-pipeline`

2. Installer pakker og reqs

`pip install -r requirements.txt`

3. Kjør scriptet case_pipeline

`python case_pipeline.py`


\
**Designvalg**

- sqlite:
- pandas:
- +++

**\Videre forbedringer**

- må legge inn hvor mye stasjonene er brukt
- kanskje gjøre noe mer om jeg rekker
