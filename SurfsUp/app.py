# Now that you’ve completed your initial analysis, you’ll design a Flask API based on the queries that you just developed. To do so, use Flask to create your routes as follows:
from flask import Flask, jsonify
import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy import func
import datetime as dt
#Database setup
#######################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

#reflect an existing database into a new model
#######################################################
Base = automap_base()
#reflect the tables
Base.prepare(autoload_with=engine)

#save reference to the table
measurement = Base.classes.measurement
Station = Base.classes.station

#Flask Setup
app = Flask(__name__)

#Flask routes
@app.route("/")
def welcome():
    """list all available api routes"""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs"
    )

# A precipitation route that:
# Returns json with the date as the key and the value as the precipitation (3 points)
# Only returns the jsonified precipitation data for the last year in the database (3 points)
@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    recent_date = session.query(measurement.date).order_by(measurement.date.desc()).first()[0]
    recent_date = dt.datetime.strptime(recent_date, '%Y-%m-%d')
    query_date_12_months = recent_date - dt.timedelta(days=365)
    precipitation = session.query(measurement.date, measurement.prcp).filter(measurement.date>=query_date_12_months).order_by(measurement.date).all()
    session.close()

    #Convert into normal list
    
    all_prcp = []
    for date, prcp in precipitation:
        prcp_dic = {}
        prcp_dic["Date"] = date
        prcp_dic["Precipitation"] = prcp
        all_prcp.append(prcp_dic)
        
    return jsonify(all_prcp)


# A stations route that:
# Returns jsonified data of all of the stations in the database (3 points)
@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)

    results = session.query(Station.station, Station.name, Station.latitude, Station.longitude).all()
    session.close()

    all_stations = []
    for station, name, latitude, longitude in results:
        station_dict = {}
        station_dict["station"] = station
        station_dict["name"] = name
        station_dict["latitude"] = latitude
        station_dict["longitude"] = longitude
        all_stations.append(station_dict)

    return jsonify(all_stations)



# A tobs route that:
# Returns jsonified data for the most active station (USC00519281) (3 points)
# Only returns the jsonified data for the last year of data (3 points)
@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    recent_date = session.query(measurement.date).order_by(measurement.date.desc()).first()[0]
    recent_date = dt.datetime.strptime(recent_date, '%Y-%m-%d')
    query_date_12_months = recent_date - dt.timedelta(days=365)
    

    most_active_station = session.query(measurement.station, func.count(measurement.station)).group_by(measurement.station).order_by(func.count(measurement.station).desc()).first()[0]
    
    temps = session.query(measurement.date, measurement.tobs).filter(measurement.station == most_active_station).\
        filter(measurement.date > query_date_12_months).\
        order_by(measurement.date).all()
    
    session.close()

    temps_list = []
    for date, tobs in temps:
        temps_dict = {}
        temps_dict["Date"] = date
        temps_dict["Tobs"] = tobs
        temps_list.append(temps_dict)

    return jsonify(temps_list)


if __name__ == '__main__':
    app.run(debug=True)
    

