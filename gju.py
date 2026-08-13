# Main script file.

# Importing
import re
import sys
import requests
import pymysql

# Defining variables.
# Define ExpresswayE logs location.
filename = '/var/log/syslog-ng/expresswaye.log'

# Define key phrase for log search (for Expressway E version 12.5.1)
# regsearch = 'clusterUser\?email='
# Define key phrase for log search (for Expressway E version 12.5.6)
regsearch = 'get_edge_sso?email='
regsearch_oreceive = 'Receive Request'
# Define token for requests to IPINFO.IO
ipinfo_token = 'your_token'
ipinfo_uri = 'https://ipinfo.io/'

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
            print(line)
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
print(v_unique_data)

# Main cycle with requests to IPINFO.IO
for item in v_unique_data:
    url = ''
    response = ''
    json_response = ''
    country = ''
    latitude = ''
    longitude = ''
    city = ''
    region = ''
    hostname = ''
    organization = ''
    timezone = ''

    # Create URL for request
    url = ipinfo_uri + item[2] + '?token=' + ipinfo_token

    # Do request
    response = requests.get(url)

    # If response is received do:
    if response.status_code == 200:
        text = (response.json())
        country = text['country']
        latitude = text['loc'].split(',')[0]
        longitude = text['loc'].split(',')[1]
        city = text['city']
        region = text['region']
        timezone = text['timezone']
        asn_name = text['asn']['name']
        asn_domain = text['asn']['domain']

        item.append(country)
        item.append(latitude)
        item.append(longitude)
        item.append(city)
        item.append(region)
        item.append(timezone)
        item.append(asn_name)
        item.append(asn_domain)

# Connect to MySQL database and insert data
MySQLServer = '127.0.0.1'
# Create connection
MySQLDBcon = pymysql.connect(host=MySQLServer,
                             user="MYSQLUSER",
                             passwd="PASSWORD",
                             db='databasename')
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
        id, v_item[1], v_item[2], v_item[0], v_item[10], v_item[9], v_item[3], v_item[7], v_item[6], v_item[4],
        v_item[5], v_item[8]))
        MySQLDBcon.commit()

else:
    print("there isn't new data, leave old and exit")

# Check table
# sql = "SELECT * FROM JABBER;"
# cursor.execute(sql)
# result = cursor.fetchall()  # Fetch all results
# for row in result:
#    print(row)

# Close connection
MySQLDBcon.close()

# Only for troubleshooting
#for item in v_unique_data:
#    print(item)

# Information
#
# Connect to MYSQL from cli
# mysql -uroot -psomepassword

# Choose DB
# USE databasename

# Show all tables in database
# SHOW TABLES;

# Show all data from table JABBER
# SELECT * FROM JABBER;

# Delete table JABBER
# DROP TABLE JABBER;

# Create table JABBER
# CREATE TABLE IF NOT EXISTS JABBER(id INT NOT NULL,lname VARCHAR(128) NOT NULL,ip_address VARCHAR(16) NOT NULL,conn_time VARCHAR(32) NOT NULL,asn_domain VARCHAR(128) NOT NULL,asn_name VARCHAR(128) NOT NULL,country VARCHAR(64) NOT NULL,region VARCHAR(128) NOT NULL,city VARCHAR(128) NOT NULL,latitude DECIMAL(8,6) NOT NULL,longitude DECIMAL(9,6) NOT NULL,timezone VARCHAR(64) NOT NULL,PRIMARY KEY(id));
