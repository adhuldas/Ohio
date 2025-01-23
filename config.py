class Config(object):
    """ 
    Configuration class for the Flask application.
    
    This class holds the configuration settings for the Flask application, including 
    the path to the SQLite database and the configuration to be used for setting up the app.
    
    Attributes:
        CONFIGURATION (str): The configuration object to be loaded into the app.
        SQL_DB_PATH (str): The file path to the SQLite database used by the application.
    """
    # The configuration object that is used to configure the app
    CONFIGURATION = "config.Config"
    
    # Path to the SQLite database file
    SQL_DB_PATH = "apps/database.db"
