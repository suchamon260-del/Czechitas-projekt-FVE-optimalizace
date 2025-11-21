# Optimalizace výkonu fotovoltaické elektrárny a kapacity bateriového úložiště  
*Optimization of PV System Size and Battery Storage Capacity*

Tento projekt simuluje provoz domácí fotovoltaické elektrárny v kombinaci s bateriovým úložištěm a hodnotí, která konfigurace je ekonomicky nejvýhodnější pro českou domácnost.  
*This project simulates the operation of a residential photovoltaic system combined with battery storage and evaluates the most cost-effective configuration for a Czech household.*

Model využívá reálná data spotřeby elektřiny z chytrého elektroměru a modelovanou solární výrobu z PVGIS (Photovoltaic Geographical Information System). Po hodinách počítá výrobu, přímou spotřebu, nabíjení a vybíjení baterie a dovozy ze sítě. Z těchto hodnot určuje roční náklady, úsporu, soběstačnost a návratnost investice pro 40 různých konfigurací.  
*The model uses real smart-meter electricity consumption data and solar production modeled via PVGIS (Photovoltaic Geographical Information System). It computes hourly PV generation, direct consumption, battery charging/discharging and grid imports, and derives annual costs, savings, self-sufficiency and payback period for 40 different configurations.*

---

## Interaktivní demo aplikace  
*Interactive demo application*

Aplikaci (demo verzi s ukázkovými daty) lze spustit zde:  
*The application (demo version with sample data) is available here:*  
https://czechitas-projekt-fve-optimalizace-dtygtgwlnd5jeaoof4nzg3.streamlit.app/
Demo verze se spustí automaticky s ukázkovým datasetem. Uživatel může volitelně nahrát vlastní CSV.  
*The demo version runs automatically with sample data. Users may optionally upload their own CSV file.*

---

## Technologie  
*Technologies*

- **Python** (Pandas, Plotly)  

- **Streamlit** (interaktivní datová aplikace / *interactive data application*) 

- **PVGIS** – modelovaná solární výroba / *modeled solar production*  

- **data z chytrého elektroměru** – reálná spotřeba domácnosti (Portál naměřených dat)  
  *Smart-meter data – real household electricity consumption (15-minute interval)*

---

## Struktura repozitáře  
*Repository structure*

- `main_FVE.py` – hlavní simulační skript  
  *main simulation script*

- `Spotreby_bez_FVE.py` – zpracování spotřebních dat  
  *preprocessing of smart-meter data*

- `PVGIS.py` – zpracování dat PVGIS  
  *preprocessing of PVGIS dataset*

- `PVGIS.csv` – hodinová výroba pro 1 kWp  
  *hourly PV production for 1 kWp*
  
- `Spotreby_bez_FVE.csv` – vstupní dataset reálné spotřeby  
  *input dataset of real household electricity consumption*

- `vysledky_optimalizace.csv` – výsledky simulace pro 40 variant  
  *simulation results for all 40 PV–battery configurations*
  
- `streamlit.py`, `streamlit_grafy.py`, `streamlit_shrnuti.py` – projektová Streamlit aplikace  
  *project Streamlit application (full input required)*

- `streamlit_demo.py` – demo aplikace s automatickými daty  
  *demo Streamlit app with auto-loaded sample data*

---

## Popis projektu  
*Project description*

Cílem projektu je zjistit, jaká kombinace výkonu fotovoltaické elektrárny a kapacity baterie je pro konkrétní domácnost ekonomicky nejvýhodnější. 
*The goal of the project is to determine which combination of a photovoltaic system size and battery capacity is the most cost-effective for a given household.*

Projekt simuluje energetické chování fotovoltaické elektrárny (FVE) a baterie pomocí hodinového modelu, který počítá výrobu FVE, přímou spotřebu domácnosti, nabíjení a vybíjení baterie a spotřebu elektřiny ze sítě, když výroba nestačí. Na základě těchto výpočtů model vyhodnocuje roční náklady, úsporu, míru soběstačnosti a ekonomickou návratnost jednotlivých konfigurací. Výsledky jsou dostupné v interaktivní aplikaci ve Streamlitu.
*The project simulates the energy behavior of a photovoltaic system and battery using an hourly model that calculates PV generation, the household’s direct consumption, battery charging and discharging, and electricity drawn from the grid when PV production is insufficient. Based on these calculations, the model evaluates annual costs, savings, self-sufficiency and the economic payback of each configuration. The results are available in an interactive Streamlit application.*

---

## Spuštění aplikace lokálně  
*Running the application locally*

