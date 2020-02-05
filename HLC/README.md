# HLC (Habits Learning Component)

## Harokopio University - Informatics and Telematics Department

**Experimental Version **

The script executed every 24h and saves on the db the changes of the states of an entity, the same time for every state of the entity stores the average values for every connected entity using the table of relations  (e.g. entities_relations ) from the db.

Example of a Record on the record_habits table:

| id   |    entity_id  |time_changed|state|context|
| ---- | ---- | ---- |---- |---- |
| 1 | switch.water_heater |2020-02-05 00:00:00|off|[{\"entity_id\": \"sensor.living_room_humidity\", \"state\": 46.0}, {\"entity_id\": \"sensor.living_room_temperature\", \"state\": 20.0}]|

## MySQL

You should manually create a database and the following two tables.

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

You should also insert the entities relations manually on the table.

```mysql
INSERT INTO `recommendations`.`entities_relations` (`key_entity`, `entities`) VALUES ('switch.water_heater', '[{"entity_id":"sensor.living_room_humidity"},{"entity_id":"sensor.living_room_temperature"}]');

```

## Home Assistant API direct access

That addon use the REST API functionality of Home Assistant using a generated API key. 

## Debug

For debugging  set the debug : true and start the component, the script executed immediately and only for one time . 

