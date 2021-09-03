import mysql.connector
from mysql.connector import errorcode
import argparse
import contextlib


@contextlib.contextmanager
def connect_to_mysql(host, username, password, database):
    try:
        connection = mysql.connector.connect(user=username, password=password, host=host, database=database)
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)
    else:
        
        yield connection
        print("Closing connection")
        connection.close()
        print("Connection closed")


def get_alarm_history_of_blocks(connection):
    cursor = connection.cursor()
    query = "SELECT archive.sample.channel_id, blocks.name, smpl_time, severity_id, status_id, nanosecs FROM (archive.sample INNER JOIN (SELECT channel_id, name FROM archive.channel WHERE name like '%CS:SB%') AS blocks ON archive.sample.channel_id = blocks.channel_id) WHERE severity_id != 1 AND severity_id != 5;"
    cursor.execute(query)
    alarm_history_of_blocks = [(channel_id, name, smpl_time, severity_id, status_id, nanosecs) for channel_id, name, smpl_time, severity_id, status_id, nanosecs in cursor]
    cursor.close()
    return alarm_history_of_blocks
    

def main(host, username, password, database):
    with connect_to_mysql(host, username, password, database) as connection:
        print(f"Connected with {connection}")
        alarm_history_of_blocks = get_alarm_history_of_blocks(connection)
        print(alarm_history_of_blocks)



if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument("-dh", "--database-host", action="store", dest="host", default="NDXEMU")
    argparser.add_argument("-u", "--username", action="store", dest="username", default="report")
    argparser.add_argument("-p", "--password", action="store", dest="password")
    argparser.add_argument("-d", "--database", action="store", dest="database", default="archive")
    args = argparser.parse_args()
    main(args.host, args.username, args.password, args.database)
