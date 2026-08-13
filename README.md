![Python](https://img.shields.io/badge/Python-3.6.8-3776AB?logo=python&logoColor=white)
![MySQL](https://img.shields.io/badge/MySQL-4479A1?logo=mysql&logoColor=white)
![Grafana](https://img.shields.io/badge/Grafana-F46800?logo=grafana&logoColor=white)
![Cisco](https://img.shields.io/badge/Cisco-1BA0D7?logo=cisco&logoColor=white)
### GeoIP dashboard в Grafana с выгрузкой данных из лога Cisco Expressway (12.5.6)

![Example output](docs/images/C4JjLpIBp6.png)
***
Краткое описание работы:
1) Python-скрипт (gju.py) выполняет парсинг syslog-файла для получения 3 значений: login-пользователя, IP-адрес с которого он подключался и времени подключения.
2) Используя полученные данные скрипт последовательно выполняет запросы к онлайн-сервису [IPINFO.IO](https://ipinfo.io) для получения значений:
- Страна
- Город
- Регион
- ASN 
- ASN domain
- Широта
- Долгота

3) Затем скрипт вносит полученные данные в локально созданную MySQL БД с таблицей JABBER которую будет использовать Grafana для отображения точек на карте.

***
Создать БД в MySQL:
```
sudo mysql -u root -p
CREATE DATABASE JABBERS_DASHBOARD;
CREATE USER 'MYSQLUSER'@'localhost' IDENTIFIED BY 'PASSWORD';
GRANT ALL PRIVILEGES ON JABBERS_DASHBOARD.* TO 'MYSQLUSER'@'localhost';
FLUSH PRIVILEGES;
CREATE TABLE IF NOT EXISTS JABBER(id INT NOT NULL,lname VARCHAR(128) NOT NULL,ip_address VARCHAR(16) NOT NULL,conn_time VARCHAR(32) NOT NULL,asn_domain VARCHAR(128) NOT NULL,asn_name VARCHAR(128) NOT NULL,country VARCHAR(64) NOT NULL,region VARCHAR(128) NOT NULL,city VARCHAR(128) NOT NULL,latitude DECIMAL(8,6) NOT NULL,longitude DECIMAL(9,6) NOT NULL,timezone VARCHAR(64) NOT NULL,PRIMARY KEY(id));
EXIT;
```
***
Grafana (12.4.4)
1) Создать datasource указывающий на Ваш MySQL. (или использовать уже имеющийся если есть)
![Example output](docs/images/mFPsf9xgyL.png)
![Example output](docs/images/mFPsf9xgyL1.png)
![Example output](docs/images/mFPsf9xgyL2.png)
2) Импортировать dashboard из файла grafana_panel.json или настроить визуализацию в ручную используя datasource (визуализация Geomap)
![Example output](docs/images/p5OybMwsWA.png)
![Example output](docs/images/SOaRWZUZRq.png)
***
