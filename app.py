import datetime as dt
from datetime import timedelta
import numpy as np

from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

########################################################################
# Database Setup
########################################################################

# Generate the engine to the correct sqlite file
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Use automap_base() and reflect the database schema 
Base = automap_base()
Base.prepare(autoload_with=engine)
print(Base.classes.keys())

# Save references to the tables in the sqlite file (measurement and station) 
Measurement = Base.classes.measurement
Station = Base.classes.station

# create and bind the session between the python app and database  
session = Session(engine)


########################################################################
# Flask Setup
########################################################################
app = Flask(__name__)


########################################################################
# Flask Routes
########################################################################

# Display the available routes on the landing page
@app.route("/")
def welcome ():
	return (
		f"Hello and Wecome to the Hawaii Climate Analysis<br/>"
		f"The available API Routes are:<br/>"
		f"/api/v1.0/precipitation<br/>"
		f"/api/v1.0/stations<br/>"
		f"/api/v1.0/tobs<br/>"
		f"/api/v1.0/temp/start<br/>"
		f"/api/v1.0/temp/start/end<br/>"
		f"<p>'start' and 'end' date should be in the format YYYYMMDD.<p>"
	)

@app.route("/api/v1.0/precipitation")
def precipitation():
	session = Session(engine)
	"""Return all precipitation data for the last year"""
	# Calculate the date 1 year ago from the last date in the database
	previous_year = dt.date(2017, 8, 23) - dt.timedelta(days = 365)

	# A precipitation route that returns jsonified precipitation data for the last year in the database
	precipitation = session.query(Measurement.date, Measurement.prcp).\
		filter(Measurement.date >= previous_year).all()
	
	session.close()

	# Convert the query results to a dictionary with date as the key and prcp as the value
	precip = {date: prcp for date, prcp in precipitation}
	return jsonify(precip)

@app.route("/api/v1.0/stations")
def stations():
	"""Return a list of stations"""
	results = session.query(Station.station, Station.name).all()

	session.close()

	# A stations route that returns jsonified data of all of the stations in the database
	return {id:loc for id,loc in results }

@app.route("/api/v1.0/tobs")
def temp_monthly():
	"""Return the temperature observations (tobs) for the previous year"""
	#Calculate the date 1 year ago from the last date in the database
	previous_year = dt.date(2017, 8, 23) - dt.timedelta(days = 365)

	# Return jsonified data for the most active station (USC00519281) 
	# Only return the jsonified data for the last year of data 
	results = session.query(Measurement.date,Measurement.tobs).\
		filter(Measurement.station == 'USC00519281').\
		filter(Measurement.date >= previous_year).all()

	session.close()

	# Unravel the results and convert to a list
	return { d:t for d,t in results }


# A start route that accepts the start date as a parameter from the URL 
@app.route("/api/v1.0/temp/<start>")

# A start/end route that accepts the start and end dates as parameters from the URL
@app.route("/api/v1.0/temp/<start>/<end>")

# Return the min, max, and average temperatures calculated from the given start date to the end of the dataset 
def stats(start, end = '2017-08-23'):
	"""Return the TMIN, TAVG, TMAX"""

	# Select a statement
	sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

	results = session.query(*sel).\
		filter(Measurement.date >= start).\
		filter(Measurement.date <= end).all() 

	session.close()	

	# Unravel the results and convert to a list
	temps = list(np.ravel(results))
	return jsonify(temps = temps)

if __name__ == '__main__':
	app.run()
