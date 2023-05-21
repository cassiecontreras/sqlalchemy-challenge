# Import the dependencies.
import numpy as np 
import datetime as dt 
import sqlalchemy 
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
measurement = Base.classes.measurement
station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)



#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    """List all available api routes."""
    return(
        f"Welcome! Surf's up! <br/>"
        f"Available Routes: <br/>"
        f"Precipitation: /api/v1.0/precipitation<br/>"
        f"List of Stations: /api/v1.0/stations<br/>"
        f"Temperature for one year: /api/v1.0.tobs<br/>"
        f"Temperature Data from start date (yyyy-mm-dd): /api/v1.0/yyyy-mm-dd<br/>"
        f"Temperature Data from end date (yyyy-mm-dd): /api/v1.0/yyyy-mm-dd<br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    queryresult = session.query(measurement.date, measurement.prcp).all()
    session.close()

    precipitation = []
    for date, prcp in queryresult: 
        precip_dict = {}
        precip_dict["Date"] = date
        precip_dict["Precipitation"] = prcp
        precipitation.append(precip_dict)

    return jsonify(precipitation)

@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    queryresult = session.query(station.station, station.name, station.latitude, station.longitude, station.elevation).all()
    session.close()

    stations = []
    for station, name, lat, lng, elv in queryresult:
        station_dict = {}
        station_dict["Station"] = station
        station_dict["Name"] = name
        station_dict["Lat"] = lat
        station_dict["Lng"] = lng
        station_dict["Elv"] = elv
        stations.append(station_dict)

    return jsonify(stations)

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    latest = session.query(measurement.date).order_by(measurement.date.desc()).first()[0]
    lastdate = dt.datetime.strptime(latest, '%Y-%m-%d')
    querydt = dt.date(lastdate.year - 1, lastdate.month, lastdate.day)
    
    queryresult = session.query(measurement.date, measurement.tobs).filter(measurement.date >= querydt).all()
    session.close()

    tobsall = []
    for date, tobs in queryresult:
        tobs_dict = {}
        tobs_dict["Date"] = date
        tobs_dict["Tobs"] = tobs
        tobsall.append(tobs_dict)

    return jsonify(tobsall)

@app.route("/api/v1.0/<start>")
def get_start(start):
    session = Session(engine)
    
    startdt = dt.datetime.strptime(start, '%Y-%m-%d')

    queryresult = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).filter(measurement.date >= startdt).all()
    session.close()

    result_list = []
    for result in queryresult:
        tobs_dict = {}
        tobs_dict['Min'] = result[0]
        tobs_dict['Avg'] = result[1]
        tobs_dict['Max'] = result[2]
        result_list.append(tobs_dict)

    return jsonify(result_list)

@app.route('/api/v1.0/<start>/<stop>')
def start_stop(start,stop):
    session = Session(engine)
    queryresult = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).filter(measurement.date >= start).filter(measurement.date <= stop).all()
    session.close()

    tobsall = []
    for min, avg, max in queryresult:
        tobs_dict = {}
        tobs_dict['Min'] = min
        tobs_dict['Avg'] = avg
        tobs_dict['Max'] = max
        tobsall.append(tobs_dict)

    return jsonify(tobsall)

if __name__ == '__main__':
    app.run(debug = True) 