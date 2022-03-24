#  TEAM CANGURU: IMPROVING BIKE BOOKING PROCESS AT SBB

## STEPS

### 1) Data Preprocessing

* For each reservation, define sections (between train stations).
* For each section, define the last bike spot reservation.
* The last bike spot reservation will be the target variable.
* https://github.com/davhofer/start_hack/blob/master/block_splitter.py

### 2) Data Enrichment

* Features given from the reservation data are: train line, time, cities.
* Features such as weekday, holiday and weather are added.
* https://github.com/davhofer/start_hack/blob/master/data_enrichment.ipynb

### 3) Model training

* Train a regression model (XGBoost).
* https://github.com/davhofer/start_hack/tree/master/model.

### 4) Develop a user interface

* Simple web interface where to user inputs journey details: start point, destination and travel date+time.
* Requests to SBB API to get train connection for the requested journey.
