# Main script file.

# Import required modules.
import geoip2.database
import re
import pymysql
import os

# Define the location of the Expressway-E log file.
# filename = '/var/log/syslog-ng/expresswaye.log'
filename = 'expresswaye.log'
# Define the GeoIP database location.
db_city = "./docs/db/GeoIP2-City.mmdb"
db_asn = "./docs/db/GeoLite2-ASN.mmdb"

# Store all sessions from the syslog file.
sessions = {}
# Store sessions containing both request and response entries.
filtered_sessions = {}
# Store complete session details (syslog data + GeoIP2 lookup results).
result_session = {}

# Open the log file and select request entries containing a login and all response entries.
with open(filename, "r", encoding="utf-8") as file:
    for line in file:
        if ("get_edge_sso?email=" in line and "Receive Request" in line) or ("Sending Response" in line):
            # Remove the first part containing syslog-specific data.
            parts = line.split(' ', 11)
            # Store the remaining part of the line in a variable.
            rest = parts[11]
            # Convert the remaining part into a dictionary of parameters.
            params = dict(re.findall(r'([\w-]+)="([^"]*)"', rest))
            txn_id = params.get("Txn-id")
            if txn_id:
                sessions.setdefault(txn_id, []).append(params)

# Check all sessions and keep only those containing both Receive Request and Sending Response entries.
for txn_id, events in sessions.items():
    has_receive = any("Receive Request" in event.get("Detail", "") for event in events)
    has_response = any("Sending Response" in event.get("Detail", "") for event in events)

    # If both entries exist, add the session to filtered_sessions, grouped by Txn-id.
    if has_receive and has_response:
        filtered_sessions[txn_id] = events

# Process filtered sessions and create result_session, grouped by Txn-id.
for txn_id, events in filtered_sessions.items():
    result_session[txn_id] = {}

    for event in events:

        # For Receive Request events, extract the request time, client public IP address,
        # and user login from the email address.
        if "Receive Request" in event.get("Detail", ""):
            result_session[txn_id]["request_time"] = event.get("UTCTime").split(",")[0]
            result_session[txn_id]["userip"] = event.get("Src-ip")
            result_session[txn_id]["userlogin"] = re.findall(r'email=([^&\s]+)', event.get("Msg", ""))[0].split("@")[0]

        # For Sending Response events, store the Msg parameter.
        if "Sending Response" in event.get("Detail", ""):
            result_session[txn_id]["Msg"] = event.get("Msg")

# Free memory used by intermediate session dictionaries.
del sessions
del filtered_sessions

# Perform GeoIP2 lookups using the local City database.
with geoip2.database.Reader(db_city) as reader:

    for txn_id, session in result_session.items():

        # Use the client's public IP address as the lookup parameter.
        ip = session["userip"]

        # Look up the IP address in the local GeoIP2 database.
        response = reader.city(ip)

        # Get the country name, or set it to 'Not found' if unavailable.
        session["country"] = response.country.name or "Not found"
        # Get the city name, or set it to 'Not found' if unavailable.
        session["city"] = response.city.name or "Not found"
        # Get the region name, or set it to 'Not found' if unavailable.
        session["region"] = response.subdivisions.most_specific.name or "Not found"
        # Get the latitude.
        session["latitude"] = response.location.latitude
        # Get the longitude.
        session["longitude"] = response.location.longitude
        # Get the time zone.
        session["time_zone"] = response.location.time_zone

with geoip2.database.Reader(db_asn) as reader:
    for txn_id, session in result_session.items():
        response = reader.asn(ip)

        # Set the ASN name.
        session["ASN"] = response.autonomous_system_organization or "Not found"
        # Set the ASN number.
        session["asn_number"] = response.autonomous_system_number or "Not found"

# Print results for troubleshooting.
# for txn_id, session in result_session.items():
##    print(f"\nTXN-ID: {txn_id}")

##    for key, value in session.items():
##        print(f"  {key}: {value}")

# Connect to the MySQL database and insert the results.
# Create a database connection.

# Set the following environment variables before running the script.
# There are for Powershell because my test environment is Windows\Powershell.
# $env:MYSQL_SERVER="xxxxxxxxxxxxx"
# $env:MYSQL_DB="xxxxxxxxxxxxx"
# $env:MYSQL_USER="xxxxxxxxxxxxx"
# $env:MYSQL_PASSWORD="xxxxxxxxxxxxx"

MYSQL_SERVER = os.environ["MYSQL_SERVER"]
MYSQL_USER = os.environ["MYSQL_USER"]
MYSQL_PASSWORD = os.environ["MYSQL_PASSWORD"]
MYSQL_DB = os.environ["MYSQL_DB"]

MySQLDBcon = pymysql.connect(host=MYSQL_SERVER,
                             user=MYSQL_USER,
                             passwd=MYSQL_PASSWORD,
                             db=MYSQL_DB)
# Create a database cursor.
cursor = MySQLDBcon.cursor()
# Initialize the record ID.
record_id = 0

# If result_session contains data, truncate the JABBER table and insert the new data.
# Otherwise, keep the existing data.
if result_session:
    print("Data found. Truncating the table and inserting all current data.")
    # Clear old data from the JABBER table.
    sql = "TRUNCATE TABLE JABBER"
    cursor.execute(sql)
    MySQLDBcon.commit()

    # Insert new data.
    for txn_id, session in result_session.items():
        # print("Just for test")
        record_id += 1
        sql = "INSERT INTO `JABBER` (id, lname, ip_address, conn_time, asn_number, asn_name, country, region, city, latitude, longitude, timezone, txn_id, response_code) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"

        cursor.execute(sql, (
        record_id, session["userlogin"], session["userip"], session["request_time"], session["asn_number"], session["ASN"], session["country"], session["region"], session["city"], session["latitude"],
        session["longitude"], session["time_zone"], txn_id, session["Msg"]))

    MySQLDBcon.commit()

    sql = "SELECT * FROM JABBER"
    cursor.execute(sql)

    rows = cursor.fetchall()

    for row in rows:
        print(row)

else:
    print("No new data found. Keeping the existing data and exiting.")

MySQLDBcon.close()

