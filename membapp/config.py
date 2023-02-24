SECRET_KEY ="jkgabulifk=="

#database connection params

SQLALCHEMY_DATABASE_URI ='mysql+mysqlconnector://root@localhost/membadb'

#TO DO activate your virtual environment and install the following:
#1 pip install flask-sqlalchemy
#2 pip install mysql-connector
#update requirement file by typing
#pip freeze > requirements.txt

# more ways of using config 

#before you test, switch to a test environment
class Config:
    ADMIN_EMAIL ="test@memba.com"
    SECRET_KEY = '4P)1D710K'

class LiveConfig(Config):
    ADMIN_EMAIL ="admin@memba.com"
    SERVER_ADDRESS = "https://server.memba.com"

class TestConfig(Config):
    SERVER_ADDRESS="http://127.0.0.1:5000"
