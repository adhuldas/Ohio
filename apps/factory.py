from flask import Flask
import os
from apps.database_handler.sqlite_connection import SqlInitHandler
from config import Config


def create_app(config_type=Config.CONFIGURATION):
    """ 
    Creates and configures a new Flask application instance.
    
    Args:
        config_type (str): The configuration type to load for the Flask application. 
                            Defaults to `Config.CONFIGURATION`.

    Returns:
        Flask: A Flask application instance with the appropriate configuration and routes set up.
    
    This function initializes the application, sets the configuration, checks the 
    existence of the SQLite database, and initializes it if necessary. It also 
    registers the API blueprint for the application.
    """
    # Initialize the Flask application
    app = Flask(__name__)
    
    # Load the configuration for the app from the provided config type
    app.config.from_object(config_type)
    
    # Check if the SQLite database file exists
    if not os.path.exists(Config.SQL_DB_PATH):
        # If the database does not exist, initialize it
        sql_object = SqlInitHandler()
        sql_object.init_sqldb()

    # Import the API blueprint (to avoid circular imports, it's done here)
    from apps.api_module.controller import api_module  # pylint: disable=import-outside-toplevel

    # Register the blueprint with the Flask app
    app.register_blueprint(api_module)

    # Return the initialized Flask app instance
    return app
