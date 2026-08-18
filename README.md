![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white)
![MySQL](https://img.shields.io/badge/MySQL-4479A1?logo=mysql\&logoColor=white)
![Grafana](https://img.shields.io/badge/Grafana-F46800?logo=grafana\&logoColor=white)
![Cisco](https://img.shields.io/badge/Cisco-1BA0D7?logo=cisco\&logoColor=white)

### GeoIP Dashboard in Grafana using Cisco Expressway logs (12.5.6)
Python 3.6.8 — tested version.

![Example output](docs/images/C4JjLpIBp6.png)

---

## How it works
1. The Python script (`gju-local.py`) parses the Cisco Expressway syslog file and extracts the following information:

   * User login
   * Client IP address
   * Connection time

2. The script uses the extracted IP address to perform a lookup in the local GeoIP2 database and retrieves:

   * Country
   * City
   * Region
   * ASN number
   * ASN name
   * Latitude
   * Longitude
   * Time zone

3. The script stores the collected data in a local MySQL database. The `JABBER` table is then used as a data source by Grafana to display the client locations on a map.

[![](https://mermaid.ink/img/pako:eNpdj09rg0AQxb_KMicLKv5do4dCo0kopNDSnhpzmMbVWFZXdpXEhnz3bmyTQuc0j_d7b5gT7ETBIIGSi8Nuj7Inb1ku85boedhUn4PFxQ653Y1bYln3ZG4sjp1kSh1wtFKiRsVFRcqas7trbD6BqbG-BMmKicdnUmCPH6jYRKp_aGYoXViL9s9If4yrzCa5NJ7G15c1yX7LbvRysheblcQSW9yCCZWsC0hK5IqZ0DDZ4EXD6RLIod-zhuWQ6LVgJQ68zyFvzzrXYfsuRANJLwedlGKo9lcxdPoNltVYSWxu5ZK1BZOpGNoeEjd2vKkEkhMcIQlmM9vxo9Cn1HOdWG8mjBrzPDuisRNTPwpC1428swlf013HpoE_C2kY0YA6YRDT8zdQQn3j?type=png)](https://mermaid.live/edit?utm_source=chatgpt.com#pako:eNpdj0Frg0AQhf_KMicLKmvUNXooNJqEQgot7akxh2lcjUVd2VUSG_Lfu9omhc5pHu97b5gz7EXGIYK8Esf9AWVH3pJUpg3R87AtPnurEnus7HbYEcu6JwtjeWolV-qIgxUTNahKFCQvK353jS0mMDY2Y5CsuXh8Jhl2-IGKT6T6hyaG0oWlaP6M-Me4ymSSK-NpeH3ZkOS37EavJnu5XUvMscEdmFDIMoMox0pxE2ouaxw1nMdACt2B1zyFSK8Zz7GvuhTS5qJzLTbvQtQQdbLXSSn64nAVfavf4EmJhcT6Vi55k3EZi77pIHLmjE4lEJ3hBJFH5zZ1A99lbObQUG8mDBqbBXbAQhoyN_B8xwlmFxO-prvUZp4795kfMI9R3wvZ5RtP-H3j)
---

## MySQL Database Setup

Create the database and user:

```sql
sudo mysql -u my_sql_admin_user -p

CREATE DATABASE JABBERS_DASHBOARD;

CREATE USER 'MYSQLUSER'@'localhost' IDENTIFIED BY 'PASSWORD';

GRANT ALL PRIVILEGES ON JABBERS_DASHBOARD.* TO 'MYSQLUSER'@'localhost';

FLUSH PRIVILEGES;

CREATE TABLE IF NOT EXISTS JABBER (
    id INT NOT NULL,
    lname VARCHAR(128) NOT NULL,
    ip_address VARCHAR(16) NOT NULL,
    conn_time VARCHAR(32) NOT NULL,
    asn_number VARCHAR(128) NOT NULL,
    asn_name VARCHAR(128) NOT NULL,
    country VARCHAR(64) NOT NULL,
    region VARCHAR(128) NOT NULL,
    city VARCHAR(128) NOT NULL,
    latitude DECIMAL(8,6) NOT NULL,
    longitude DECIMAL(9,6) NOT NULL,
    timezone VARCHAR(64) NOT NULL,
    response_code VARCHAR(64),
	status VARCHAR(64) NOT NULL,
    PRIMARY KEY(id)
);

EXIT;
```

---

## Grafana (12.4.4)

1. Create a Grafana datasource pointing to your MySQL database, or use an existing MySQL datasource.

![Example output](docs/images/mFPsf9xgyL.png)

![Example output](docs/images/mFPsf9xgyL1.png)

![Example output](docs/images/mFPsf9xgyL2.png)

2. Import the dashboard from `grafana_panel.json`, or configure the visualization manually using the MySQL datasource and the **Geomap** visualization.

![Example output](docs/images/p5OybMwsWA.png)

![Example output](docs/images/SOaRWZUZRq.png)

---
