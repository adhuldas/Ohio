from flask import Blueprint, jsonify, request
from apps.database_handler.sqlite_connection import SqlInitHandler

# Setting up blueprint for the API module
api_module = Blueprint(
    "api_module", __name__, url_prefix="/"
)

@api_module.route('/data', methods=['GET'])
def get_data():
    """
    API endpoint to fetch the annual production data by well number.

    This endpoint retrieves the total amount of oil, gas, and brine produced by 
    a specific well identified by its 'well' query parameter. If no well number 
    is provided, it returns an error message. If the well number is not found in 
    the database, it also returns an error.

    Returns:
        JSON: A response with the total oil, gas, and brine production data, or 
              an error message if the well number is missing or not found.
    """
    # Fetch the 'well' query parameter from the request
    well_number = request.args.get('well')
    
    # If no well number is provided, return an error message
    if not well_number:
        return jsonify({"error": "Well number is required"}), 400
    
    # Initialize the database handler to connect to the database
    sql_obj = SqlInitHandler()
    conn = sql_obj.get_db_connection()
    cursor = conn.cursor()

    # SQL query to fetch the total oil, gas, and brine production for the specified well
    cursor.execute('''
    SELECT SUM(oil), SUM(gas), SUM(brine) FROM annual_production WHERE api_well_number = ?
    ''', (well_number,))
    
    # Fetch the query result (a tuple containing the sums of oil, gas, and brine)
    result = cursor.fetchone()

    # Close the database connection
    conn.close()

    # If data is found for the well, return the production totals
    if result:
        total_oil, total_gas, total_brine = result
        return jsonify({
            "oil": total_oil,
            "gas": total_gas,
            "brine": total_brine
        })
    else:
        # If no data is found for the given well number, return an error message
        return jsonify({"error": "Well number not found"}), 404
