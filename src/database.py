import pandas as pd
import numpy as np
from itertools import product
from sqlalchemy import create_engine
import mysql.connector
import sqlite3
from sqlite3 import Error


def get_sim_where_comp(host, user, password, database, it1, it2):
    mydb = create_connection_mysql(host, user, password, database)

    my_cursor = mydb.cursor()
    sql = "select * from similarity where comp_1=%s and comp_2=%s"
    sql = sql % (it1, it2)
    my_cursor.execute(sql)

    my_cursor = my_cursor.fetchall()

    return len(my_cursor)


def check_if_pair_exist(host, user, password, database, it1, it2):
    print(it1, it2)

    exist = get_sim_where_comp(host, user, password, database, it1, it2)
    exist_reverse = get_sim_where_comp(host, user, password, database, it2, it1)

    if exist == 0 and exist_reverse == 0:
        return False

    else:

        return True


def insert_row(host, user, password, database, chebi_a, chebi_b, sim_res, sim_l, sim_j):
    mydb = create_connection_mysql(host, user, password, database)

    my_cursor = mydb.cursor()

    sql = "INSERT INTO similarity (comp_1, comp_2, sim_resnik, sim_lin, sim_jc) VALUES (%s,%s,%s,%s,%s)"

    val = (chebi_a, chebi_b, sim_res, sim_l, sim_j)
    my_cursor.execute(sql, val)

    mydb.commit()


def get_chebi_ids(dataset):
    chebi_ids = dataset.item.unique()

    return chebi_ids


def check_database(host, user, passwd, db_name):
    check = False

    mydb = mysql.connector.connect(
        host=host,
        user=user,
        passwd=passwd
    )
    mycursor = mydb.cursor()

    mycursor.execute("SHOW DATABASES")

    for x in mycursor:
        # x = x[0].decode("unicode-escape") # decode was giving an error (note: decode is needed when using mysql docker)

        if x[0].decode("unicode-escape") == db_name:
            check = True

    if check == False:

        print("will create db")
        mycursor.execute("CREATE DATABASE " + db_name)
        create_table(host, user, passwd, db_name)

    else:
        print("Database already exists")


def create_table(host, user, passwd, db_name):
    mydb = mysql.connector.connect(
        host=host,
        user=user,
        passwd=passwd,
        database=db_name
    )

    mycursor = mydb.cursor()

    # mycursor.execute("CREATE TABLE customers (name VARCHAR(255), address VARCHAR(255))")

    mycursor.execute("SET FOREIGN_KEY_CHECKS = 0")
    mycursor.execute("DROP TABLE IF EXISTS `similarity`")

    mycursor.execute(
        " CREATE TABLE `similarity` (`id` INT NOT NULL AUTO_INCREMENT, `comp_1` INT NOT NULL,  `comp_2` INT NOT NULL, "
        "`sim_resnik` FLOAT NOT NULL, `sim_lin` FLOAT NOT NULL, `sim_jc` FLOAT NOT NULL, PRIMARY KEY (`id`), "
        "INDEX sim (`comp_1`,`comp_2`) ) ENGINE=InnoDB")

    mycursor.execute("SET FOREIGN_KEY_CHECKS = 1")



def create_connection_mysql(user, host, password, db):

    mydb = mysql.connector.connect(
        host=host,
        user=user,
        passwd=password,
        database=db
    )

    return mydb


def create_connection_sqlite(db_file):
    """ create a database connection to the SQLite database
        specified by db_file
    :param db_file: database file
    :return: Connection object or None
    """
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)

    return None


def create_engine_mysql(host, user, password, database_name):
    #"mysql+pymysql://{user}:{pw}@172.17.0.5/{db}"
    engine = create_engine("mysql+pymysql://{user}:{pw}@"+ host + "/{db}"
                           .format(user=user,
                                   pw=password,
                                   db=database_name))

    return engine




def confirm_all_test_train_similarities(list1, list2, pairs_from_db):
    # check if all item-item pair was found in the database

    lists_combinations = pd.DataFrame(list(product(list1, list2)),
                                      columns=['l1', 'l2'])

    ss = lists_combinations.l1.isin(
        pairs_from_db.comp_1.astype('int64').tolist()) & lists_combinations.l2.isin(
        pairs_from_db.comp_2.astype('int64').tolist())

    ss2 = lists_combinations.l2.isin(
        pairs_from_db.comp_1.astype('int64').tolist()) & lists_combinations.l1.isin(
        pairs_from_db.comp_2.astype('int64').tolist())

    not_found_in_db = lists_combinations[(~ss) & (~ss2)]

    not_found_list_1 = not_found_in_db.l1.unique().tolist()
    not_found_list_2 = not_found_in_db.l2.unique().tolist()

    return not_found_list_1, not_found_list_2


def get_sims(mydb, list1, list2):

    my_cursor = mydb.cursor()
    format_strings1 = ','.join(['%s'] * len(list1))
    format_strings2 = ','.join(['%s'] * len(list2))
    sql = "select id, comp_1, comp_2 from similarity where comp_1 in (%s) and comp_2 in (%s)"
    format_strings1 = format_strings1 % tuple(list1)
    format_strings2 = format_strings2 % tuple(list2)
    # TODO: confirm this is correct
    sql = sql % (format_strings1,format_strings2)

    my_cursor.execute(sql)

    myresult = my_cursor.fetchall()

    if len(myresult) != 0:

        myresult = pd.DataFrame(np.array(myresult),
                                columns=['id', 'comp_1', 'comp_2'])

    else:
        myresult = pd.DataFrame(columns=['id', 'comp_1', 'comp_2'])

    return myresult


def save_to_mysql(df, engine, table_name):

    df.comp_1 = df.comp_1.map(lambda x: x.lstrip('CHEBI_')).astype(int)
    df.comp_2 = df.comp_2.map(lambda x: x.lstrip('CHEBI_')).astype(int)

    df.to_sql(table_name, con=engine, if_exists = 'append',  index=False, method='multi', chunksize=10000)
