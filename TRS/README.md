# TRS (Telegram Recommendation Service)

## Harokopio University - Informatics and Telematics Department

**Experimental Version **

The script accepts json paylod and sends telegram notifications.

Syntax of payload:

For switch category entities e.g.: switch.ac_plug

```json
{"msg":"new","userid":"telegram_id","title":"Do you want to turn off the the AC plug?","entity_id":"switch.ac_plug","domain":"switch","service":"turn_off","state":""}
```
For state category entities e.g.: light.office_light , sensor

```json
{"msg":"new","userid":"telegram_id","title":"Do you want to turn off the Office light?","entity_id":"light.office_light","domain":"state","service":"","state":"off"}
```

The messges on telegram have the form Accept/Reject. If the user ignore the message for 20 seconds, the system consider the message as Rejected.

On every action the system sends a message to the user.

The system can handle multiple users.

You can use the internal or an external mqtt broker.

## Home Assistant API direct access

That addon can control all the Home Assistant entities using a generated API key. The service command executed if the user accept the recommendation.

### MYSQL Support
You can store all the recommendations logs and results on your MYSQL Server.

Create a database and a table with the following columns

```sql
CREATE TABLE `data` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` varchar(45) DEFAULT NULL,
  `notify_time` datetime DEFAULT NULL,
  `response_time` datetime DEFAULT NULL,
  `question` mediumtext,
  `response` varchar(45) DEFAULT NULL,
  `response_log` varchar(45) DEFAULT NULL,
  `entity` varchar(45) DEFAULT NULL,
  `state` varchar(45) DEFAULT NULL,
  `domain` varchar(45) DEFAULT NULL,
  `service` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`));
```

