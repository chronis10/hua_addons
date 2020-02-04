# HLC (Habits Learning Component)

## Harokopio University - Informatics and Telematics Department

**Experimental Version **

The script every 24h save on db the changes of the states of a component

## Home Assistant API direct access

That addon can control all the Home Assistant entities using a generated API key. 

### MYSQL Support
You can store all the data on your MYSQL Server.

Create a database and a table with the following columns

Table for habits recording

```sql
CREATE TABLE `record_habits` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `entity_id` varchar(45) DEFAULT NULL,
  `time_changed` datetime DEFAULT NULL,
  `state` varchar(45) DEFAULT NULL,
  `context` json DEFAULT NULL,
  PRIMARY KEY (`id`));
```

Table for entities relations

```sql
CREATE TABLE `entities_relations` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `key_entity` varchar(100) NOT NULL,
  `entities` json NOT NULL,
  PRIMARY KEY (`id`));
```