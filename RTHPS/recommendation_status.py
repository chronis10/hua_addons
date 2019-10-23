# Python Module to fetch PIR records for last 'daysback' period, calculate the lookback timers per hour and return a recommendation trigger as "ON" or "OFF".
import mysql.connector
from mysql.connector import Error
import pandas as pd
import datetime
import json
import pdb
import sys, getopt
from codecs import decode


def calculate_hourly_timers(dbHost, dbPort, dbName, dbUser, dbPass, daysback=28, houroffset=3):
    try:
        connection = mysql.connector.connect(host = dbHost,
                                             port = dbPort,
                                             database = dbName,
                                             user = dbUser,
                                             password = dbPass)

        if connection.is_connected():
            db_Info = connection.get_server_info()
            print("Connected to MySQL Server version: ", db_Info)
            cursor = connection.cursor()
            cursor.execute("select database();")
            record = cursor.fetchone()
            print("You are connected to database: ", record)
            cursor = connection.cursor()
            # CALL THE STORED PROCEDURE
            cursor.callproc('get_last_month_pir_per_day_hour', [daysback, houroffset])
            # EXTRACT RESULTS FROM CURSOR
            dfData = pd.DataFrame()
            for result in cursor.stored_results():
                dfData = pd.DataFrame(result.fetchall(), columns=['domainName', 'entity', 'DayOfWeek', 'timeSlot', 'counter'])

    except Error as e:
        print("Error while connecting to MySQL: ", e)
    finally:
        if (connection.is_connected()):
            groupedDF = dfData.groupby(['DayOfWeek'])
            timer = 15  # The HomeAssistant timer
            df = pd.DataFrame()
            # iterate over each group
            for group_name, group_data in groupedDF:
                arraySlots = list(range(0, 24))
                fullSlotsdf = pd.DataFrame(arraySlots, columns=['timeSlot'])

                # left join in python
                temp_df = pd.merge(fullSlotsdf, group_data, on='timeSlot', how='left')
                temp_df = temp_df[['domainName', 'entity', 'DayOfWeek', 'timeSlot', 'counter']]
                temp_df['domainName'].fillna('sensor', inplace=True)
                temp_df['entity'].fillna('sensor.varlamis_office_rf_bridge', inplace=True)
                temp_df['DayOfWeek'].fillna(str(group_name), inplace=True)
                temp_df['counter'].fillna(0, inplace=True)
                df = df.append(temp_df, ignore_index=True)

            # Convert column "DayOfWeek" to int64 dtype
            df = df.astype({"DayOfWeek": int})
            # Convert column "timeSlot" to int64 dtype
            df = df.astype({"timeSlot": int})
            # Convert column "counter" to int64 dtype
            df = df.astype({"counter": int})

            # Declare lists that are to be converted into df columns
            probs = []
            lookback_time = []
            max_counter = df['counter'].max()
            query_args_list = []

            for index, row in df.iterrows():
                cur_dayOfWeek = row['DayOfWeek']
                cur_timeslot = row['timeSlot']
                cur_prob = round((row['counter'] / max_counter), 2)
                lkback_time = int(round(cur_prob * timer) + 2)
                probs.append(cur_prob)
                lookback_time.append(lkback_time)
                query_args_list.append({'dayOfWeek': cur_dayOfWeek, 'timeslot': cur_timeslot,
                                        'lookback_time_mins': lkback_time, 'changed_by': 'ProbCalculator'})
            # Using 'Probability' as the column name and equating it to the 'probs' list
            df['Probability'] = probs
            df['Lookback_Time'] = lookback_time
            # print out the resultset
            print("Printing query results...")
            print(df)

            for arg in query_args_list:
                queryQ = "INSERT INTO lookback_timers (dayOfWeek,timeslot,lookback_time_mins,changed_by) " \
                         "VALUES (" \
                         + str(arg.get('dayOfWeek')) + ", " \
                         + str(arg.get('timeslot')) + ", " \
                         + str(arg.get('lookback_time_mins')) + ", '" \
                         + str(arg.get('changed_by')) + "') " \
                         "ON DUPLICATE KEY UPDATE " \
                         "dayOfWeek = " + str(arg.get('dayOfWeek')) + ", " \
                         "timeslot = " + str(arg.get('timeslot')) + ", " \
                         "lookback_time_mins = " + str(arg.get('lookback_time_mins')) + ", " \
                         "changed_by = '" + str(arg.get('changed_by')) + "';"

                cursor.execute(queryQ)
                connection.commit()
            print("Closing the DB connection...")
            cursor.close()
            connection.close()
            print("MySQL connection is closed!")


def get_action_recommendation_decision(dbHost, dbPort, dbName, dbUser, dbPass, houroffset=3, minDetections=10):
    try:
        # read commandline arguments, first
        fullCmdArguments = sys.argv

        # - further arguments
        argumentList = fullCmdArguments[1:]

        shortArguments = "hi:p:n:u:s:"
        longArguments = ["dbHost=", "dbPort=", "dbName=", "dbUser=", "dbPass="]

        try:
            arguments, values = getopt.getopt(argumentList, shortArguments, longArguments)

        except getopt.error as err:
            # output error, and return with an error code
            print (str(err))
            sys.exit(2)

        if len(argumentList) != 5:  
              print ("usage: get_action_recommendation_decision.py --dbHost=<dbHost> --dbPort=<dbPort> --dbName=<dbName> --dbUser=<dbUser> --dbPass=<dbPass> --houroffset=<houroffset> --minDetections=<minDetections>")
        else:
            for currentArgument, currentValue in arguments:
                if currentArgument == "-h":
                    print("Displaying help:")
                    print("get_action_recommendation_decision.py --dbHost=<dbHost> --dbPort=<dbPort> --dbName=<dbName> --dbUser=<dbUser> --dbPass=<dbPass> --houroffset=<houroffset> --minDetections=<minDetections>")
                elif currentArgument in ("-i", "--dbHost"):
                    dbHost = currentValue
                elif currentArgument in ("-p", "--dbPort"):
                    dbPort = currentValue
                elif currentArgument in ("-n", "--dbName"):
                    dbName = currentValue
                elif currentArgument in ("-u", "--dbUser"):
                    dbUser = currentValue
                elif currentArgument in ("-s", "--dbPass"):
                    dbPass = currentValue

        print("Initializing connection...")
        
        connection = mysql.connector.connect(host = dbHost,
                                             port = dbPort,
                                             database = dbName,
                                             user = dbUser,
                                             password = dbPass)
        
        if connection.is_connected():
            db_Info = connection.get_server_info()
            print("Connected to MySQL Server version ", db_Info)
            cursor = connection.cursor()
            cursor.execute("select database();")
            record = cursor.fetchone()
            print("You are connected to database: ", record)
            cursor = connection.cursor()
            call_function_query = "select " + str(dbName) + ".get_recommendation_trigger_status_for_interval(" + str(houroffset) + ", " + str(minDetections) + ");"
            cursor.execute(call_function_query)
            records = cursor.fetchone()

            for result in records:
                print("This is the JSON response:")
                print(result)

    except Error as e:
        print("Error while connecting to MySQL", e)

    finally:
        if (connection.is_connected()):
            print("Closing the DB connection...")
            cursor.close()
            connection.close()
            print("MySQL connection is closed!")



if __name__ == "__main__":
    # execute only if run as a script
    print("Starting...")
    get_action_recommendation_decision(sys.argv[1:][0], sys.argv[1:][1], sys.argv[1:][2], sys.argv[1:][3], sys.argv[1:][4])
