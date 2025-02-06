from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.impute import SimpleImputer
import numpy as np

app = FastAPI()

app.mount("/css", StaticFiles(directory="css"), name="css")
templates = Jinja2Templates(directory="./vendor/templates")

csv_path = "PATH_TO_YOUR_FILE"

def load_data():
    try:
        return pd.read_csv(csv_path, encoding='ISO-8859-1')
    except UnicodeDecodeError:
        return pd.read_csv(csv_path, encoding='latin1')

def prepare_data():
    water_data = load_data()
    water_data.replace(' ', np.nan, inplace=True)
    required_columns = [
        "Temp", "D.O. (mg/l)", "PH", "CONDUCTIVITY (µmhos/cm)", "B.O.D. (mg/l)",
        "NITRATENAN N+ NITRITENANN (mg/l)", "FECAL COLIFORM (MPN/100ml)",
        "TOTAL COLIFORM (MPN/100ml)Mean", "year"
    ]
    imputer = SimpleImputer(strategy='mean')
    water_data[required_columns] = imputer.fit_transform(water_data[required_columns])
    pollution_threshold = 500
    ph_value = 8.5
    water_data['Polluted'] = ((water_data['CONDUCTIVITY (µmhos/cm)'] > pollution_threshold) |
                              (water_data['PH'] > ph_value)).astype(int)
    X = water_data[required_columns]
    y = water_data['Polluted']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    model = RandomForestClassifier(random_state=42)
    model.fit(X_train_scaled, y_train)
    return model, scaler, water_data

model, scaler, water_data = prepare_data()

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    states = water_data['STATE'].dropna().unique().tolist()
    locations = water_data['LOCATIONS'].dropna().unique().tolist()
    return templates.TemplateResponse("home.html", {"request": request, "result": None, "states": states, "locations": locations})

@app.post("/predict", response_class=HTMLResponse)
async def predict(request: Request, state: str = Form(...), location: str = Form(...)):
    data_point = water_data[(water_data['STATE'].str.lower() == state.lower()) &
                            (water_data['LOCATIONS'].str.contains(location, case=False, na=False))]

    if data_point.empty:
        result = "No data available for the selected location."
    else:
        features = data_point.drop(columns=['Polluted', 'STATE', 'LOCATIONS', 'STATION CODE'], errors='ignore')
        features_scaled = scaler.transform(features)
        prediction = model.predict(features_scaled)[0]
        result = f"{location} is: {'Polluted' if prediction == 1 else 'Not Polluted'}"

    states = water_data['STATE'].dropna().unique().tolist()
    locations = water_data['LOCATIONS'].dropna().unique().tolist()
    return templates.TemplateResponse("home.html", {"request": request, "result": result, "states": states, "locations": locations})
