# Main script file.

# Importing
import geoip2.database
import re
import pymysql

# Define ExpresswayE logs location.
# filename = '/var/log/syslog-ng/expresswaye.log'
# Define ExpresswayE logs location.
filename = 'expresswaye.log'
# Define GeoIPdatabase location.
db_city = "./docs/db/GeoIP2-City.mmdb"
# Define MySQL server
MySQLServer = '10.34.228.50'

# Define key phrase for log search (for Expressway E version 12.5.6)
regsearch = 'get_edge_sso?email='
regsearch_oreceive = 'Receive Request'

v_found_lines = []
v_result_lines = []
v_unique_data = []
v_seen_names = set()

## Main search cycle in log file
with open(filename, 'r') as file:
    for line in file:
        v_jabber = ''
        v_user = ''
        v_date = ''
        v_time = ''
        v_timestamp = ''
        v_found_lines = []

        if "get_edge_sso?email=" in line and "Receive Request" in line:
            # Only for troubleshooting
            # print(line)

            v_date = line.split()[5].split('T')[0]
            v_time = line.split()[2].replace('"', "").split(',')[0]
            v_timestamp = v_date + ' ' + v_time
            v_jabber_ip = line.split()[18].split('=')[1].replace('"', "")
            v_username = line.split()[21].split('=')[1].split('@')[0]

            v_found_lines.append(v_timestamp)
            v_found_lines.append(v_username)
            v_found_lines.append(v_jabber_ip)
            v_result_lines.append(v_found_lines)

# Sorting result list by timestamp
v_result_lines = sorted(v_result_lines, key=lambda item: item[0], reverse=True)

# Get only unique items by username
for item in v_result_lines:
    if item[1] not in v_seen_names:
        v_unique_data.append(item)
        v_seen_names.add(item[1])

# Only for troubleshooting
# print(v_unique_data)

# Main cycle with requests to LOCAL GeoIP2-City DB
for item in v_unique_data:
    response = ''

    # Do request
    with geoip2.database.Reader(db_city) as reader:
        response = reader.city(item[2])

    item.append(response.country.name)
    if response.city.name:
        item.append(response.city.name)
    else:
        item.append('None')
    if response.subdivisions.most_specific.name:
        item.append(response.subdivisions.most_specific.name)
    else:
        item.append('None')
    item.append(response.location.latitude)
    item.append(response.location.longitude)
    item.append(response.location.time_zone)
    item.append('None')
    item.append('None')

    # Only for troubleshooting
    print(item)

# Connect to MySQL database and insert data
# Create connection
MySQLDBcon = pymysql.connect(host=MySQLServer,
                             user="mysqltestuser",
                             passwd="Forwarding!239",
                             db='JABBERS_DASHBOARD')
# Creating a cursor
cursor = MySQLDBcon.cursor()
# defining id
id = 0

# Check if v_unique_data isn't null we clear(truncate table) else left old data in the table JABBER
if v_unique_data:
    print("There is some data so we must add it to database")
    # clear old data in JABBER table
    sql = "TRUNCATE TABLE JABBER"
    cursor.execute(sql)
    MySQLDBcon.commit()

    # adding new data
    for v_item in v_unique_data:
        id += 1
        # print(id)
        sql = "INSERT INTO `JABBER` (id, lname, ip_address, conn_time, asn_domain, asn_name, country, region, city, latitude, longitude, timezone) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        # print(sql)

        cursor.execute(sql, (
        id, v_item[1], v_item[2], v_item[0], v_item[10], v_item[9], v_item[3], v_item[5], v_item[4], v_item[6],
        v_item[7], v_item[8]))
        MySQLDBcon.commit()

else:
    print("there isn't new data, leave old and exit")

MySQLDBcon.close()

""" 
"""

