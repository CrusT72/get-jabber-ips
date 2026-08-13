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
Структура таблицы в MySQL
```bash
mysql> DESCRIBE JABBER;
+------------+--------------+------+-----+---------+-------+
| Field      | Type         | Null | Key | Default | Extra |
+------------+--------------+------+-----+---------+-------+
| id         | int          | NO   | PRI | NULL    |       |
| lname      | varchar(128) | NO   |     | NULL    |       |
| ip_address | varchar(16)  | NO   |     | NULL    |       |
| conn_time  | varchar(32)  | NO   |     | NULL    |       |
| asn_domain | varchar(128) | NO   |     | NULL    |       |
| asn_name   | varchar(128) | NO   |     | NULL    |       |
| country    | varchar(64)  | NO   |     | NULL    |       |
| region     | varchar(128) | NO   |     | NULL    |       |
| city       | varchar(128) | NO   |     | NULL    |       |
| latitude   | decimal(8,6) | NO   |     | NULL    |       |
| longitude  | decimal(9,6) | NO   |     | NULL    |       |
| timezone   | varchar(64)  | NO   |     | NULL    |       |
+------------+--------------+------+-----+---------+-------+
12 rows in set (0.52 sec)
```
создать таблицу в MySQL:
```bash
CREATE TABLE IF NOT EXISTS JABBER(id INT NOT NULL,lname VARCHAR(128) NOT NULL,ip_address VARCHAR(16) NOT NULL,conn_time VARCHAR(32) NOT NULL,asn_domain VARCHAR(128) NOT NULL,asn_name VARCHAR(128) NOT NULL,country VARCHAR(64) NOT NULL,region VARCHAR(128) NOT NULL,city VARCHAR(128) NOT NULL,latitude DECIMAL(8,6) NOT NULL,longitude DECIMAL(9,6) NOT NULL,timezone VARCHAR(64) NOT NULL,PRIMARY KEY(id));
```
***
В Grafana (тестировалось с версией 12.4.4) использовался стандартный плагин Geomap.
(попробуйте импортировать файл grafana_panel.json или настроить визуализацию в ручную.)



