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
sessions = []

# Open the log file and select entries from 'edgeconfigprovisioning'
with open(filename, "r", encoding="utf-8") as file:
    for line in file:
        if "edgeconfigprovisioning" in line and ("Authenticating user failed" in line or "Authenticated user successfully" in line):
            # Remove the first part containing syslog-specific data.
            parts = line.split(' ', 6)
            # Store the remaining part of the line in a variable.
            rest = parts[6]
            # Convert the remaining part into a dictionary of parameters.
            params = dict(re.findall(r'([\w-]+)="([^"]*)"', rest))
            # Check that the Code parameter is exist and set None if not.
            params["Code"] = params.get("Code", None)
            # Check keyword 'failed' in Detail and set success or failed to the new parameter 'status'.
            params["Status"] = ("failed" if params["Detail"] == "Authenticating user failed" else "success")
            # Cut last part of date\time variable.
            params["UTCTime"] = params.get("UTCTime").split(",")[0]
            sessions.append(params)

# # Perform GeoIP2 lookups using the local City database.
with geoip2.database.Reader(db_city) as reader:
    for session in sessions:

        # Use the client's public IP address as the lookup parameter.
        ip = session["ClientId"]

        # Look up the IP address in the local GeoIP2 city database.
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
    for session in sessions:
        # Use the client's public IP address as the lookup parameter.
        ip = session["ClientId"]

        # Look up the IP address in the local GeoIP2Lite ASN database.
        response = reader.asn(ip)

        # Set the ASN name.
        session["ASN"] = response.autonomous_system_organization or "Not found"
        # Set the ASN number.
        session["asn_number"] = response.autonomous_system_number or "Not found"

for session in sessions:
    print(session)

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
if sessions:
    print("Data found. Truncating the table and inserting all current data.")
    # Clear old data from the JABBER table.
    sql = "TRUNCATE TABLE JABBER"
    cursor.execute(sql)
    MySQLDBcon.commit()

    # Insert new data.
    for session in sessions:
        # print("Just for test")
        record_id += 1
        sql = "INSERT INTO `JABBER` (id, lname, ip_address, conn_time, asn_number, asn_name, country, region, city, latitude, longitude, timezone, response_code, status) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        cursor.execute(sql, (
        record_id, session["Username"], session["ClientId"], session["UTCTime"], session["asn_number"], session["ASN"], session["country"], session["region"], session["city"], session["latitude"],
        session["longitude"], session["time_zone"], session["Code"], session["Status"]))

    MySQLDBcon.commit()

    # Show the new inserted in table data if exist.
    sql = "SELECT * FROM JABBER"
    cursor.execute(sql)

    rows = cursor.fetchall()

    for row in rows:
        print(row)

else:
    print("No new data found. Keeping the existing data and exiting.")

MySQLDBcon.close()

