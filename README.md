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

3. Kjør scriptet oslo_bike_etl

`python oslo_bike_etl.py`


\
**Designvalg**

SQLite: Vurderte først mySQL, men kom på hvor herk det kan være å finne gratis hosting. Også egner SQLite veldig til liknende cas-oppgaver som ikke krever noe store mengder lagring, og kan kjøres av alle med python installert.\
ETL-struktur: Pørvde å ha en tydelig ETL struktur gjennom koden. Letter å teste og debugge\
Historikk: La til en ekstra nøkkel på station_status for å få en historikk som gjøre det lettere å bygge en god measure\
last_updated: valgt å legge til denne som en kolonne og merker hver rad med når den ble oppdatert\

\
**Videre forbedringer**

- Kunne brukt en annen metric som ikke trenger historisk data. Teoretisk sett ville den nok fungert på en fullstendig kilde 
- Rydde opp i spaghetti kode
- Lagt til docstring/beskrivelse på kodesnutter eller viktige transformasjoner
