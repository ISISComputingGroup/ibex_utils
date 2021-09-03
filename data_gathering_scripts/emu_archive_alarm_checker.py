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


def get_blocks(connection):
    cursor = connection.cursor()
    query = "SELECT channel_id, name FROM archive.channel WHERE name like '%CS:SB%';"
    cursor.execute(query)
    blocks = [(channel_id, name) for channel_id, name in cursor]
    cursor.close()
    return blocks
    

def main(host, username, password, database):
    with connect_to_mysql(host, username, password, database) as connection:
        print(f"Connected with {connection}")
        blocks = get_blocks(connection)
        print(blocks)



if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument("-dh", "--database-host", action="store", dest="host", default="NDXEMU")
    argparser.add_argument("-u", "--username", action="store", dest="username", default="report")
    argparser.add_argument("-p", "--password", action="store", dest="password")
    argparser.add_argument("-d", "--database", action="store", dest="database", default="archive")
    args = argparser.parse_args()
    main(args.host, args.username, args.password, args.database)
