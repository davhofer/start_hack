# Import packages
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.pylab import rcParams
import seaborn as sns
import scipy
from scipy.spatial.distance import cdist
import dateutil
import math
import meteomatics.api as api
import datetime as dt
% matplotlib
inline
rcParams['figure.figsize'] = 10, 8


# 1) Load data
# read the reservation data
df = pd.read_csv('data_raw/reservation_data_2019-2021_incl_capacity.csv',
                 parse_dates=["date"], date_parser=lambda x: pd.to_datetime(x, format="%Y-%m-%d %H:%M:%S"))

# read holiday data
df_schulferien = pd.read_csv('data_preprocessed/Schulferien.csv', dtype={"canton": "string", "population": "int32"})
df_schulferien['start'] = pd.to_datetime(df_schulferien['holidays_start'])
df_schulferien['end'] = pd.to_datetime(df_schulferien['holidays_end'])
df_schulferien = df_schulferien.drop(columns=["holidays_start", "holidays_end"])

# train station coordinates data
df_coordinates = pd.read_csv('data_preprocessed/dienststellen.csv')
df_coordinates = df_coordinates[["abk_bahnhof", "lat", "lon"]]
df_coordinates = df_coordinates[df_coordinates['abk_bahnhof'].notna()]

# weather data
def parse_date(row):
    date=datetime.datetime.fromisoformat('2019-11-11T00:52:43+00:00')
    return date

df_weather = pd.read_csv("data_preprocessed/weather.csv")
df_weather['date']= df_weather.apply(lambda row: parse_date(row), axis=1)

# df_weather['date'] = df_weather['validdate'].apply(dateutil.parser.parse)

# jahresformation
df_jahresformation = pd.read_csv("data_preprocessed/jahresformation.csv", dtype={"Block Bezeichnung": "string"})
display(df_jahresformation.tail(1))
df_jahresformation.dtypes

# kapazität
df_kapazität = pd.read_csv("data_preprocessed/rollmaterial-matching.csv")
display(df_kapazität.tail(1))

# %% md

#### 2) Week day <a name="stat"></a>

- Add
a
feature
for weekday: 'weekday' and 'month'

# %%

df['weekday'] = df['date'].dt.dayofweek
df['month'] = df['date'].dt.month

# %% md

#### 3) Holidays <a name="stat"></a>
- Add
a
feature
for number of people in holiday canton: n_holiday


# %%

# for each date, get the number of people in Switzerland who
# are either on school holiday or national holiday..
def get_holiday_people(date):
    filtered_holidays = df_schulferien[(df_schulferien['start'] <= date) & (df_schulferien['end'] >= date)]
    is_national_holiday = (filtered_holidays["canton"] == "national").sum()
    if is_national_holiday:
        people = 7917100
    elif not (filtered_holidays.empty):
        filtered_holidays = filtered_holidays[filtered_holidays["canton"] != "national"]
        people = sum(filtered_holidays["population"])
    else:
        people = 0
    return people


# %%

# filter df, only 2021 data
# df=df[df['date']>='2021-01-01']
df['holiday_people'] = df.apply(lambda row: get_holiday_people(row['date']), axis=1)

# %% md

#### 4) Coordinates <a name="hr"></a>

# %%

# full join for start train station
df = pd.merge(df, df_coordinates, left_on='bp_from', right_on='abk_bahnhof')
df = df.drop(columns=['abk_bahnhof']).rename(columns={"lat": "lat_from", "lon": "lon_from"})

# full join for destination
df = pd.merge(df, df_coordinates, left_on='bp_to', right_on='abk_bahnhof')
df = df.drop(columns=['abk_bahnhof']).rename(columns={"lat": "lat_to", "lon": "lon_to"})
display(df.head(2))

# %% md

#### 5) Weather <a name="corr"></a>

# %%

# weather data
df_weather = pd.read_csv("data_preprocessed/weather.csv")
parse_dates = ["validdate"], date_parser = lambda x: pd.to_datetime(x, format="%Y-%m-%d%T%H:%M:%S%Z"))

# df_weather['date'] = df_weather['validdate'].apply(dateutil.parser.parse)
display(df_weather.tail(1))

# %%

##import meteo data
username = 'can-guru_otth'
password = 'eyk47W6ATq'
coordinates = [(47.378177, 8.540212)]
# model =     'mix'

startdate = dt.datetime(year=2022, month=4, day=9, hour=0, minute=0, second=0)
enddate = startdate

parameters = ['t_2m:C', 'precip_24h:mm', 'leisure_biking:idx']
format = 'csv'

df = api.query_time_series(coordinates, startdate, enddate, interval, parameters, username, password, model=model)

print(df)

# %% md

#### 6) Capacity <a name="corr"></a>

# %% md

- Für
jede
Reservation: Zugnummer
im
Jahresformation - Datensatz
abrufen
- Beachte: richtiges
Jahr
wählen, häufigste
Formation
- entsprechende
Kapazität
auslesen

# %%

# combine data from capacity table and annual formation
list_kapazitäten = df_kapazität["Block Bezeichnung in Jahresformation Fpl-2022"].tolist()
df_jahresformation = df_jahresformation[df_jahresformation["Block Bezeichnung"].isin(list_kapazitäten)]
df_jahresformation = df_jahresformation[["Block Bezeichnung", "Zug", "Beginn Fahrplanperiode"]]
df_jahresformation = pd.merge(df_jahresformation, df_kapazität, left_on='Block Bezeichnung',
                              right_on='Block Bezeichnung in Jahresformation Fpl-2022').drop(
    columns=["Block Bezeichnung in Jahresformation Fpl-2022"])
df_jahresformation.tail(2)

# %%

median_df = df[df["capacity"].notnull()]
median = np.median(median_df['capacity'])
print('Median Kapazität', median)

# %%


def fill_capacity(row):
    train = row.train_nr
    formation = df_jahresformation[df_jahresformation["Zug"] == train]
    display(formation)
    capacity = formation["No. of hooks"].mean()
    return capacity


# %%

# for the rows where there is no capacity included
# first try to check with the jahresformation lookup table
mask = df.capacity.isnull()
df['capacity'] = df[mask].apply(fill_capacity, axis=1)

# secondly, fill the median capacity
df = df.fillna(value={"capacity": median})

# %%

df.head(10)
