# TRS (Telegram Recommendation Service)

## Harokopio University - Informatics and Telematics Department

**Experimental Version **

The script accepts json paylod and sends telegram notifications. 

Syntax of payload:

```json
{"msg":"new","userid":"telegram_id","title":"Do you want to turn off the PC?"} 
```



The messges on telegram have the form Accept/Reject. If the user ignore the message for 20 seconds, the system consider the message as Rejected.

On every action the system sends a message to the user.

The system can handle multiple users.

You can use the internal or an external mqtt broker.



















