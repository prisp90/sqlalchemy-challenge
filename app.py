from flask import Flask, jsonify
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from sqlalchemy import Column, Integer, String, Float
import numpy as np
import datetime as dt


engine = create_engine("sqlite:///../Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect = True)
Station = Base.classes.station


Measurement = Base.classes.measurement
session = Session(engine)

app = Flask(__name__)

@app.route("/")
def home():
    return(
    f"Available routes: <br>"
    f"/api/v1.0/precipitation<br>"
    f"/api/v1.0/stations<br>"
    f"/api/v1.0/tobs<br>"
    f"/api/v1.0/<start>/<end>"
    f"<br>")

@app.route("/api/v1.0/precipitation")
def precipitation():

    precipitation_results = session.query(Measurement.date, Measurement.prcp).all()

    session.close()

    precipitation_list = []
    for date, prcp in precipitation_results:
        precipitation_dict = {}
        precipitation_dict["date"] = date
        precipitation_dict["prcp"] = prcp
        precipitation_list.append(precipitation_dict)

    return jsonify(precipitation_list)


@app.route("/api/v1.0/stations")
def station_name():
       
    station_results = session.query(Station.name).all()

    session.close()

    station_list = []
    for station_nm in station_results:
        station_list.append(list(station_nm))

    return jsonify(station_list)

@app.route("/api/v1.0/tobs")
def tobs_def():

    station_count = func.count(Measurement.station)
    tobs_results = session.query(Measurement.station, station_count).group_by(Measurement.station).\
        order_by(station_count.desc()).first()

    session.close()

    most_active_station_id = tobs_results[0]

    next_results = session.query(Measurement.station, Measurement.date, Measurement.tobs).\
        filter_by(station = most_active_station_id).order_by(Measurement.date.desc()).first()    
    
    session.close()

    most_recent_date = next_results[1]

    recent_date = dt.datetime.strptime(f"{most_recent_date}", "%Y-%m-%d")

    last_date = recent_date - dt.timedelta(days = 365)

    most_active_station_table = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.date >= last_date).\
        filter(Measurement.date <= recent_date).filter(Measurement.station == 'USC00519281').\
        order_by(Measurement.date).all()
    
    session.close()

    most_active_station_list = list(np.ravel(most_active_station_table))

    return jsonify(most_active_station_list)

@app.route("/api/v1.0/<start>/<end>")
def search_range(start, end):
    station_avg = func.avg(Measurement.tobs)
    station_min = func.min(Measurement.tobs)
    station_max = func.max(Measurement.tobs)

    startDate = dt.datetime.strptime(f"{start}", "%Y-%m-%d")
    endDate = dt.datetime.strptime(f"{end}", "%Y-%m-%d")

    results = session.query(station_avg, station_min, station_max).filter(Measurement.date >= startDate).\
    filter(Measurement.date <= endDate).all()

    session.close()

    show_this = list(np.ravel(results))

    return jsonify(show_this)

if __name__ == "__main__":
    app.run(debug=True)
