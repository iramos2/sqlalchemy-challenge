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
measure = Base.classes.measurement
station = Base.classes.station

#################################################
# Flask Setup
#################################################
# Create an app, being sure to pass __name__
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route("/")
def home():
    return (
        f"Welcome to the climate app!<br/>"
        f"Available Routes:<br/>"
        f"Precipitation: /api/v1.0/precipitation<br/>"
        f"Stations: /api/v1.0/stations<br/>"
        f"Temperature of the most active station: /api/v1.0/tobs<br/>"
        f"More temperature from a start date (YYYY-MM-DD): /api/v1.0/<start><br/>"
        f"More temperature from a start-end range (YYYY-MM-DD):/api/v1.0/<start>/<end>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    sesh = Session(engine)
    start_date = '2016-08-23'
    
    recent = sesh.query(measure.date).order_by(measure.date.desc()).first()
    # Calculate the date one year from the last date in data set.
    one_y = dt.date(2017,8,23) - dt.timedelta(days=365)

    # Perform a query to retrieve the data and precipitation scores
    prcp = sesh.query(measure.date, measure.prcp).\
                        filter(measure.date > one_y).all()

    # Save the query results as a Pandas DataFrame. Explicitly set the column names
    prcp_d = pd.DataFrame(prcp, columns=['date', 'precipitation'])

    # Sort the dataframe by date
    prcp_df = prcp_d.sort_values(by='date')
    
    # convert df to dictionary
    prcp_dict = prcp_df.to_dict(orient='records')
        
    sesh.close()
    return jsonify(prcp_dict)

@app.route("/api/v1.0/stations")
def stations():
    sesh = Session(engine)
    stations = sesh.query(station.station).all()
    all_stations = list(np.ravel(stations))
    sesh.close()
    
    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def tobs():
    sesh = Session(engine)
    temp_year = sesh.query(measure.date).filter(measure.station =='USC00519281').order_by(measure.date.desc()).first()

    # Calculate the date one year from the last date in data set.
    one_y_t = dt.date(2017,8,18) - dt.timedelta(days=365)

    # Perform a query to retrieve the date and temperatures
    temp = sesh.query(measure.date, measure.tobs).\
                        filter(measure.date > one_y_t).\
                        filter(measure.station =='USC00519281').all()

    # Save the query results as a Pandas DataFrame. Explicitly set the column names
    temp_d = pd.DataFrame(temp, columns=['date', 'temperature'])

    # Sort the dataframe by date
    temp_df = temp_d.sort_values(by='date')
    
    # convert DF to dictionary
    temp_dict = temp_df.to_dict(orient='records')
    
    sesh.close()
    return jsonify(temp_dict)

@app.route("/api/v1.0/<start>")
def start(start):
    sesh = Session(engine)
    
    # querying the min, max, and average for the most active station
    sel = [func.min(measure.tobs), func.max(measure.tobs), func.avg(measure.tobs)]
    temp = sesh.query(*sel).filter(measure.date >= start).all()
    
    # convert the query results to a dictionary
    temp_dict = {
        "Minimum": temp[0][0],
        "Maximum": temp[0][1],
        "Average": temp[0][2],
    }
    
    sesh.close()
    return jsonify(temp_dict)

@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):
    sesh = Session(engine)
    
    # querying the min, max, and average for the most active station
    sel = [func.min(measure.tobs), func.max(measure.tobs), func.avg(measure.tobs)]
    temp = sesh.query(*sel).filter(measure.date >= start).filter(measure.date <= end).all()
    
    # convert the query results to a dictionary
    temp_dict = {
        "Minimum": temp[0][0],
        "Maximum": temp[0][1],
        "Average": temp[0][2],
    }
    
    return jsonify(temp_dict)

if __name__ == "__main__":
    app.run(debug=True)
