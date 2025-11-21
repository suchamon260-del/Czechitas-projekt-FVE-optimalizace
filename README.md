# Optimization of PV System Size and Battery Storage Capacity

This project simulates the operation of a residential photovoltaic (PV) system combined with battery storage and evaluates the most cost-effective configuration for a Czech household.

The model uses real smart-meter electricity consumption data and modeled solar production from PVGIS. It calculates hourly energy flows – PV generation, direct consumption, battery charging/discharging and grid imports – and then derives annual costs, savings, self-sufficiency and payback period for 40 different system configurations.

## Technologies

- Python (Pandas, Plotly)
- Streamlit (interactive app)
- PVGIS (modeled solar production)
- Smart-meter data (Portal of measured data)

## Repository structure

- `main_FVE.py` – main simulation script  
- `Spotreby_bez_FVE.py` – preprocessing of consumption data  
- `PVGIS.py` – preprocessing of PVGIS data  
- `streamlit.py`, `streamlit_grafy.py`, `streamlit_shrnuti.py` – Streamlit app and charts  
- `PVGIS.csv` – modeled PV production (1 kWp)  
- `vysledky_optimalizace.csv` – results for all configurations
