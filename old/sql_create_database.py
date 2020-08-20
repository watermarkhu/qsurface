import mysql.connector
from mysql.connector import Error


def create_connection(host_name=None, user_name=None, user_password=None, database=None):
    connection = None
    try:
        if not host_name:
            host_name = "104.199.14.242"
        if not user_name:
            user_name = "root"
        if not user_password:
            user_password = "Guess20.Located.Oil..."
        config = dict(
            host=host_name,
            user=user_name,
            passwd=user_password
        )
        if database:
            config.update(database=database)
        connection = mysql.connector.connect(**config)

    except Error as e:
        print(f"The error '{e}' occurred")

    return connection


def create_database(connection, db_name):
    cursor = connection.cursor()
    try:
        cursor.execute("CREATE DATABASE {}".format(db_name))
        print("Database created successfully")
    except Error as e:
        print(f"The error '{e}' occurred")



def new_database(host_name, user_name, user_password, database_name):
    connection = create_connection(host_name, user_name, user_password)
    create_database(connection, database_name)
    connection.close()


if __name__ == "__main__":

    import argparse
    from simulator import add_kwargs

    parser = argparse.ArgumentParser(
        prog="mysql creator",
        description="creates a mysql database",
    )

    parser.add_argument("database_name",
        action="store",
        type=str,
        help="name of database",
        metavar="dn",
    )

    key_arguments = [
        ["-ip", "--host_name", "store", "ip address of database", dict(metavar="")],
        ["-u", "--user_name", "store", "login username", dict(metavar="")],
        ["-pw", "--user_password", "store", "login password", dict(metavar="")]
        ]

    add_kwargs(parser, key_arguments)
    args=vars(parser.parse_args())
    new_database(**args)
