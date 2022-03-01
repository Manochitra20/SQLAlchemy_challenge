# Dependencies
import datetime as dt
import numpy as np
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Function to access and query SQLite database file
Base = automap_base()

# Reflect database
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station


#################################################
# Flask Setup
#################################################
app = Flask(__name__)

# Define welcome route
@app.route('/')

def welcome():
   
    """List all Climate Analysis API routes!"""
    return (
    f"Available Routes: <br/>"
    f"/api/v1.0/precipitation <br/>"
    f"/api/v1.0/stations <br/>"
    f"/api/v1.0/tobs <br/>"
    f"/api/v1.0/temp/start/end"
    )

# Define precipitation route
@app.route('/api/v1.0/precipitation')

def precipitation():
     # Create our session (link) from Python to the DB
    session = Session(engine)
     # query to retrieve the last 12 months of precipitation data
    query_date = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    
    year_data=session.query(Measurement.date, Measurement.prcp).\
            filter(Measurement.date >= query_date).all()

    session.close()

    all_precipitation = list(np.ravel(year_data))
    return jsonify(all_precipitation)

# Define stations route
@app.route('/api/v1.0/stations')

def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    results = session.query(Station.station).all()

    session.close()

    all_stations = list(np.ravel(results))
    return jsonify(all_stations)

# Define temperature route
@app.route('/api/v1.0/tobs')

def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    station_total=session.query(Station.name).count()
   
    active_station=session.query(Measurement.station, func.count(Measurement.station)).\
                    group_by(Measurement.station).\
                    order_by(func.count(Measurement.station).desc()).first()

    query_date = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    results = session.query(Measurement.tobs).\
        filter(Measurement.station == 'USC00519281').\
        filter(Measurement.date >= query_date).all()
    
    session.close()
    
    all_temp= list(np.ravel(results))
    
    return jsonify(all_temp)

# Define statistics route
@app.route('/api/v1.0/temp/<start>')
@app.route('/api/v1.0/temp/<start>/<end>')

def stats(start=None, end=None):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    
    #Create an if statement to get the start time 
    if not end:
        start=dt.datetime.strptime(start, '%m-%d-%Y')
        
        results = session.query(*sel).\
            filter(Measurement.date>= start).all()
   
        session.close()

   #Unravel results into an array and convert to a list
        all_start=list(np.ravel(results))
   
        return jsonify(all_start)

    #Define user input start/end dates
    start=dt.datetime.strptime(start, '%m-%d-%Y')
    end=dt.datetime.strptime(end, '%m-%d-%Y')

    results=session.query(*sel).\
        filter(Measurement.date>=start).\
        filter(Measurement.date<=end).all()

    session.close()

    #Unravel results into an array and convert to a list
    all_dates=list(np.ravel(results))

    return jsonify(all_dates)
    

if __name__ == '__main__':
    app.run(debug=True)