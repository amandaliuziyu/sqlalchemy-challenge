# Import the dependencies.
import numpy as np
import pandas as pd
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
Base.prepare(autoload_with=engine)


# Save references to each table
station = Base.classes.station
measurement = Base.classes.measurement
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
    return (
        f"Welcome to the Hawaii Weather API<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/stats"
        f"/api/v1.0/<start> (enter as YYYY-MM-DD)<br/>"
        f"/api/v1.0/<start>/<end> (enter as YYYY-MM-DD)<br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)

    # Calculate the date one year ago from the last date
    one_year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    previous_year = dt.date(one_year_ago.year, one_year_ago.month, one_year_ago.day)

    # Query for the precipitation data in the last 12 months
    results = (
        session.query(measurement.date, measurement.prcp)
        .filter(measurement.date >= previous_year)
        .order_by(measurement.date.desc())
        .all()
    )

    # Convert the query results to a dictionary
    precipitation_dict = {date: prcp for date, prcp in results}
    
    print(f"The results for Percipitation: {precipitation_dict}")
    return jsonify(precipitation_dict)


@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    station_results = session.query(station.station, station.name, station.latitude, station.longitude, station.elevation).all()
    session.close()

    stations_list = []
    for station_id,name,latitude,longitude,elevation in station_results:
        station_dict = {}
        station_dict['station_id'] = station_id
        station_dict['Lat'] = latitude
        station_dict['Lon'] = longitude
        station_dict['Elevation'] = elevation
        stations_list.append(station_dict)

    return jsonify(stations_list)

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)

    #most active: USC00519281

    one_year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    previous_year = dt.date(one_year_ago.year, one_year_ago.month, one_year_ago.day)

    # Query for the temperature observations of the most active station in the last 12 months
    results = (
        session.query(measurement.date, measurement.tobs)
        .filter(measurement.station == "USC00519281")
        .filter(measurement.date >= previous_year )
        .all()
    )

    tobs_list = [{"date": result[0], "tobs": result[1]} for result in results]
    return jsonify(tobs_list)

@app.route("/api/v1.0/stats")
def stats():
    session = Session(engine)

    # Calculate temperature statistics
    results = (
        session.query(
            func.min(measurement.tobs),
            func.max(measurement.tobs),
            func.avg(measurement.tobs)
        )
        .filter(measurement.station == "USC00519281")
        .all()
    )
    session.close()

    stats_dict = {
        "Lowest Temperature": results[0][0],
        "Highest Temperature": results[0][1],
        "Average Temperature": results[0][2]
    }
    return jsonify(stats_dict)


@app.route("/api/v1.0/<start>")
def start_date(start):
    session = Session(engine)
    
    # Query temperature statistics from the start date
    results = (
        session.query(
            func.min(measurement.tobs),
            func.max(measurement.tobs),
            func.avg(measurement.tobs)
        )
        .filter(measurement.date >= start)
        .all()
    )
    session.close()

    # Create a dictionary to hold the results
    stats_dict = {
        "Start Date": start,
        "Lowest Temperature": results[0][0],
        "Highest Temperature": results[0][1],
        "Average Temperature": results[0][2]
    }
    return jsonify(stats_dict)

@app.route("/api/v1.0/<start>/<end>")
def start_end_date(start, end):
    session = Session(engine)
    
    # Query temperature statistics from the start date to the end date
    results = (
        session.query(
            func.min(measurement.tobs),
            func.max(measurement.tobs),
            func.avg(measurement.tobs)
        )
        .filter(measurement.date >= start)
        .filter(measurement.date <= end)
        .all()
    )
    session.close()

    # Create a dictionary to hold the results
    stats_dict = {
        "Start Date": start,
        "End Date": end,
        "Lowest Temperature": results[0][0],
        "Highest Temperature": results[0][1],
        "Average Temperature": results[0][2]
    }
    return jsonify(stats_dict)


# Run the Flask app
if __name__ == "__main__":
    app.run(debug=True)