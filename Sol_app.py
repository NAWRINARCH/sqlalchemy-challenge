# Import the dependencies.
from flask import Flask, jsonify
import numpy as np
import pandas as pd
from sqlalchemy import create_engine, func
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
import datetime as dt

# Create Flask app instance
app = Flask(__name__)


#################################################
# Database Setup
engine = create_engine("sqlite:///C:/Users/nawri/OneDrive/Desktop/mod 10 challenge/Starter_Code/Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)
# Save references to the tables
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create session link from Python to the DB
session = Session(engine)

# Define your routes
@app.route("/")
def welcome():
    return (
        f"Welcome to the Climate API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end><br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    last_date = dt.datetime.strptime(last_date, "%Y-%m-%d")
    year_ago = last_date - dt.timedelta(days=365)
    precipitation_data = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= year_ago).all()
    precipitation_dict = {date: prcp for date, prcp in precipitation_data}
    return jsonify(precipitation_dict)

@app.route("/api/v1.0/stations")
def stations():
    results = session.query(Station.station).all()
    stations_list = list(np.ravel(results))
    return jsonify(stations_list)

@app.route("/api/v1.0/tobs")
def tobs():
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    last_date = dt.datetime.strptime(last_date, "%Y-%m-%d")
    year_ago = last_date - dt.timedelta(days=365)
    most_active_station = session.query(Measurement.station).group_by(Measurement.station)\
                               .order_by(func.count(Measurement.station).desc()).first()[0]
    temp_data = session.query(Measurement.date, Measurement.tobs)\
                       .filter(Measurement.station == most_active_station)\
                       .filter(Measurement.date >= year_ago).all()
    temp_list = [{date: tobs} for date, tobs in temp_data]
    return jsonify(temp_list)

@app.route("/api/v1.0/<start>")
def start_date(start):
    start_date = dt.datetime.strptime(start, "%Y-%m-%d")
    temp_data = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs))\
                       .filter(Measurement.date >= start_date).all()
    temp_dict = {"TMIN": temp_data[0][0], "TAVG": temp_data[0][1], "TMAX": temp_data[0][2]}
    return jsonify(temp_dict)

@app.route("/api/v1.0/<start>/<end>")
def start_end_date(start, end):
    start_date = dt.datetime.strptime(start, "%Y-%m-%d")
    end_date = dt.datetime.strptime(end, "%Y-%m-%d")
    temp_data = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs))\
                       .filter(Measurement.date >= start_date)\
                       .filter(Measurement.date <= end_date).all()
    temp_dict = {"TMIN": temp_data[0][0], "TAVG": temp_data[0][1], "TMAX": temp_data[0][2]}
    return jsonify(temp_dict)

#################################################


# Teardown session when done
@app.teardown_appcontext
def shutdown_session(exception=None):
    session.close()

# Run the app
if __name__ == "__main__":
    app.run(debug=True)
