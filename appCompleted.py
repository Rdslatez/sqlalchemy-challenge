# Import the dependencies.
from matplotlib import style
style.use('fivethirtyeight')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, Column, Integer, String, Float

#################################################
# Database Setup
#################################################
# create engine to hawaii.sqlite
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)
Base.classes.keys()


# Save references to each table
Measurements = Base.classes.measurement
Stations = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

# Find the most recent date in the data set.
recent_date = session.query(func.max(Measurements.date)).first()
print (recent_date)

#Design a query to retrieve the last 12 months of precipitation data and plot the results. 
# Starting from the most recent data point in the database. 

# Calculate the date one year from the last date in data set.
#2017-08-23 - 1 year = 2016-08-23
conn = engine.connect()
# Perform a query to retrieve the data and precipitation scores
data = session.query(Measurements.date, Measurements.prcp).filter(Measurements.date >= '2016-08-23', Measurements.date <= '2017-08-23').all()
# Save the query results as a Pandas DataFrame. Explicitly set the column names
df = pd.DataFrame(data)

# Sort the dataframe by date
df = df.rename(columns={"prcp": "Percipitation"})
df.sort_values(by='date', inplace = True)
df.set_index('date', inplace=True)
# Use Pandas Plotting with Matplotlib to plot the data
#df.plot()
#plt.xlabel('Date')
#plt.ylabel('Inches')
#plt.title('Precipitation over last year')
#plt.legend(loc = 'upper center')
#plt.tight_layout()
#plt.xticks(rotation = 90)

#plt.show()

# Use Pandas to calculate the summary statistics for the precipitation data
stats = df['Percipitation'].describe()
stat_df = pd.DataFrame(stats)
stat_df

# Design a query to calculate the total number of stations in the dataset
print (session.query(Stations.station).count())

# Design a query to find the most active stations (i.e. which stations have the most rows?)
# List the stations and their counts in descending order.
session.query(Measurements.station, func.count(Measurements.station)).group_by(Measurements.station).all()

# Using the most active station id from the previous query, calculate the lowest, highest, and average temperature.
session.query(func.min(Measurements.tobs), func.max(Measurements.tobs), func.avg(Measurements.tobs)).filter(Measurements.station == 'USC00519281').all()

# Find the most recent date in the data set for that previous specific station.
recent_date = session.query(func.max(Measurements.date)).filter(Measurements.station == 'USC00519281').first()
print (recent_date)

# Using the most active station id
# Query the last 12 months of temperature observation data for this station and plot the results as a histogram
histo = session.query(Measurements.tobs).filter(Measurements.date >= '2016-08-18', Measurements.date <= '2017-08-18', Measurements.station == 'USC00519281').all()
df2 = pd.DataFrame(histo)
#plt.hist(df2['tobs'], bins=12, label='tobs')
#plt.xlabel('Temperature')
#plt.ylabel('Frequency')
#plt.legend(loc = 'upper right')
#plt.tight_layout()
#plt.show()
# Close Session
session.close()

#################################################
# Flask Setup
#################################################
from flask import Flask, jsonify

app = Flask(__name__)


#################################################
# Flask Routes
#################################################
@app.route("/")
def home():
    #Homepage
    print("Welcome to my class homepage!")
    return(f"Welcome!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        #Gives a format for the api
        f"Date format for start and/or end below: yyyy-mm-dd<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end<br/>"
        )


@app.route("/api/v1.0/precipitation")
def precip():
    #Queries the data needed, just as per the earlier
    info = session.query(Measurements.date, Measurements.prcp).filter(Measurements.date >= '2016-08-23', Measurements.date <= '2017-08-23').all()
    #converts to dataframe for easy conversion to dictionary
    data_f = pd.DataFrame(info)
    #convers to dictionary
    dict1 = data_f.to_dict()
    #returns json dictionary
    return jsonify(dict1)

@app.route("/api/v1.0/stations")
def stati():
   #Query to find all stations
   temp = session.query(Stations.station).all()
   tempdf = pd.DataFrame(temp)
   station_list = tempdf.values.tolist()
   return jsonify(station_list)

@app.route("/api/v1.0/tobs")
def tobs():
    #initial query, getting tobs based on the dates aquired earlier in the work
    tobs_sess = session.query(Measurements.date, Measurements.tobs).filter(Measurements.date >= '2016-08-18', Measurements.date <= '2017-08-18', Measurements.station == 'USC00519281').all()
    #converts to dataframe, easy to make into a list
    tobs_df = pd.DataFrame(tobs_sess)
    #converts to list
    tobs_list = tobs_df.values.tolist()
    #returns json
    return jsonify(tobs_list)

@app.route(f"/api/v1.0/<start>")
def starts(start):
    #initial query, getting tobs based on the dates entered into the api
    start_sess = session.query(Measurements.tobs).filter(Measurements.date >= start).group_by(Measurements.date).all()
    #converts to a dataframe for easy calculations
    start_df = pd.DataFrame(start_sess)
    #aggregates for min, mean and max
    start_df = start_df.agg(['min','mean','max'])
    #converts to a list for json
    start_list = start_df.values.tolist()
    #returns json
    return jsonify(start_list)

@app.route(f"/api/v1.0/<start>/<end>")
def full(start, end):
    #initial query, getting tobs based on the dates entered into the api
    entire = session.query(Measurements.tobs).filter(Measurements.date >= start, Measurements.date <= end).group_by(Measurements.date).all()
    #converts to a dataframe for easy calculations
    entire_df = pd.DataFrame(entire)
    #aggregates for min, mean and max
    entire_df = entire_df.agg(['min','mean','max'])
    #converts to a list for json
    entire_list = entire_df.values.tolist()
    #returns json
    return jsonify(entire_list)


if __name__ == "__main__":
    app.run(debug=True)