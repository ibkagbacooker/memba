from flask import Flask
from flask_wtf.csrf import CSRFProtect
from flask_sqlalchemy import SQLAlchemy
app = Flask(__name__, instance_relative_config=True) #making the instance available

#import oo config available
from membapp import config


#initialize extension to protect all POST routes against csrf attack and pass the token when submitting through these routes
csrf = CSRFProtect(app)
csrf.exempt 

#load the config from instance folder file
app.config.from_pyfile("config.py", silent=False)

#how to load from object based config that is within your package

app.config.from_object(config.LiveConfig)

db=SQLAlchemy(app) #an instance of alchemy
#load the routes

from membapp import adminroutes,userroutes