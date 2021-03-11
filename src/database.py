###############################################################################
#                                                                             #
# Licensed under the Apache License, Version 2.0 (the "License"); you may     #
# not use this file except in compliance with the License. You may obtain a   #
# copy of the License at http://www.apache.org/licenses/LICENSE-2.0           #
#                                                                             #
# Unless required by applicable law or agreed to in writing, software         #
# distributed under the License is distributed on an "AS IS" BASIS,           #
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.    #
# See the License for the specific language governing permissions and         #
# limitations under the License.                                              #
#                                                                             #
###############################################################################
#                                                                             #  
# @author: Márcia Barros                                                      #  
# @email: marcia.c.a.barros@gmail.com                                         #
# @date: 28 Jan 2020                                                          #
# @version: 1.0                                                               #  
# Lasige - FCUL                                                               #
#                                                                             #  
# @last update:                                                               #  
#   version 1.1: 12 Feb 2021                                                  #      
#   (author: Matilde Pato, matilde.pato@gmail.com)                            #   
#                                                                             #  
###############################################################################

import sqlite3
from itertools import product
from sqlite3 import Error

import mysql.connector
import numpy as np
import pandas as pd
from sqlalchemy import create_engine

from myconfiguration import MyConfiguration as cfg

# ----------------------------------------------------------------------------------------------------- #

def create_default_connection_mysql():
    """

    Create a default connection to the mysql database specified by host, user 
     and password defined in config.ini
    :param
    :return mydb: connection object
    """
    conf = cfg.getInstance()
    mydb = mysql.connector.connect(
        host=conf.host,
        user=conf.user,
        password=conf.password
    )
    return mydb

# ----------------------------------------------------------------------------------------------------- #

def create_connection_mysql():
    """
   
   Create a connection to the mysql database specified by host, user, password and
    database name defined in config.ini
   :param
   :return mydb: connection object
   """
    mydb = create_default_connection_mysql()
    mydb.database = cfg.getInstance().database

    return mydb

# ----------------------------------------------------------------------------------------------------- #

def create_connection_sqlite(sb_file):
    """ 
    
    Create a database connection to the SQLite database specified by sb_file
    :param sb_file: File name of database where semantic base will be stored
    :type sb_file: string
    :return conn: connection object or none
    """
    try:
        conn = sqlite3.connect( sb_file )
        return conn
    except Error as e:
        print( e )

    return None

# ----------------------------------------------------------------------------------------------------- #

def create_engine_mysql():
    """
    
    Create a pool and dialect together connection to provide a source of database and behavior
    :param
    :return engine: connection engine object
    """
    # in case of connection error, change the host as in the next commented code
    conf = cfg.getInstance()
    host = conf.host
    user = conf.user
    passwd = conf.password
    db_name = conf.database

    engine = create_engine( "mysql+pymysql://{user}:{pw}@{host}/{db}"
                            .format( user=user,
                                     pw=passwd,
                                     host=host,
                                     db=db_name ),
                            pool_pre_ping=True )

    return engine

# ----------------------------------------------------------------------------------------------------- #

def check_database():
    """
    Check the existence of a database with the name defined in config.ini 
     if none, a new is created as well as a table of similarity
    :param 
    :return none
    """

    global mydb
    try:
        check = False
        mydb = create_default_connection_mysql()
        mycursor = mydb.cursor()
        db_name = cfg.getInstance().database

        mycursor.execute( "SHOW DATABASES" )
        for x in mycursor:

            if x[0].decode( "unicode-escape" ) == db_name:
            # or,
            # if x[0].encode().decode( 'utf-8' ) == db_name:
                check = True

        if not check:
            print( "Will create database" )
            mycursor.execute( "CREATE DATABASE " + db_name )
            create_table()

        else:
            print( "Database already exists" )

    except Error as e:
        print( "Error while connecting to MySQL", e )
    finally:
        if mydb.is_connected():
            mycursor.close()
            mydb.close()

# ----------------------------------------------------------------------------------------------------- #

def create_table():
    """
    
    Create a table named similarity with in mysql which columns are
        <id, comp_1, comp_2, sim_resnik, sim_lin, sim_jc> 
    :param: none
    :return:
    """
    global mydb
    try:
        mydb = create_connection_mysql()

        mycursor = mydb.cursor()

        mycursor.execute( "SET FOREIGN_KEY_CHECKS = 0" )
        mycursor.execute( "DROP TABLE IF EXISTS `similarity`" )

        mycursor.execute(
            " CREATE TABLE `similarity` (`id` INT NOT NULL AUTO_INCREMENT,"
            "`comp_1` INT NOT NULL,"  
            "`comp_2` INT NOT NULL, "
            "`sim_resnik` FLOAT NOT NULL, "
            "`sim_lin` FLOAT NOT NULL, "
            "`sim_jc` FLOAT NOT NULL,"
            " PRIMARY KEY (`id`), "
            "INDEX sim (`comp_1`,`comp_2`) ) ENGINE = InnoDB" )

        mycursor.execute( "SET FOREIGN_KEY_CHECKS = 1" )

    except Error as e:
        print( "Error while connecting to MySQL", e )
    finally:
        if mydb.is_connected():
            mycursor.close()
            mydb.close()

# ----------------------------------------------------------------------------------------------------- #

def get_items_ids(dataset, name_prefix):
    """

    Get the ids of each items in the dataset
    :param dataset: cvs dataset
    :param name_prefix: Prefix of the concepts to be extracted from the ontology
    :type name_prefix: string
    :return ids: ids of each row of the dataset
    """
    
    if ( dataset.dtypes['item'] == np.object ):
        dataset.item = dataset.item.map( lambda x: x.lstrip( name_prefix ) ).astype('int64')
    return dataset.item.unique()

# ----------------------------------------------------------------------------------------------------- #

def confirm_all_test_train_similarities(entry_ids_1, entry_ids_2, pairs_from_db):
    """

    Checks if all item-item pair was found in the database
     for each entry_ids_1 and entry_ids_2
    Important: the values must be in string format because of HPO 
    :param entry_ids_1: list of entries 1
    :param entry_ids_2: list of entries 2
    :return: list with results not found combinations pandas Dataframe

    """
    lists_combinations = pd.DataFrame( list( product( entry_ids_1, entry_ids_2 ) ),
                                       columns=['l1', 'l2'] )

    ss = lists_combinations.l1.isin( pairs_from_db.comp_1.astype( 'int64' ).tolist() ) \
        & lists_combinations.l2.isin( pairs_from_db.comp_2.astype( 'int64' ).tolist() ) 

    ss2 = lists_combinations.l2.isin( pairs_from_db.comp_1.astype( 'int64' ).tolist() ) \
        & lists_combinations.l1.isin( pairs_from_db.comp_2.astype( 'int64' ).tolist() )
        
    not_found_in_db = lists_combinations[ (~ss) & (~ss2) ]

    not_found_list_1 = not_found_in_db.l1.unique().tolist()
    not_found_list_2 = not_found_in_db.l2.unique().tolist()

    return not_found_list_1, not_found_list_2

# ----------------------------------------------------------------------------------------------------- #

def get_sims(entry_ids_1, entry_ids_2):
    """

    Get the id, item 1, item 2 of each items in the similarity db
     for each entry_ids_1 and entry_ids_2
    :param entry_ids_1: list of entries 1
    :param entry_ids_2: list of entries 2
    :return myresult: pandas DataFrame
    """
    global mydb, result
    try:
        # Open database connection
        mydb = create_connection_mysql()

        # prepare a cursor object using cursor() method
        mycursor = mydb.cursor()
        
        format_strings1 = ','.join( ['%s'] * len( entry_ids_1 ) )
        format_strings2 = ','.join( ['%s'] * len( entry_ids_2 ) )
        
        # Prepare SQL query to read a record into the database.
        sql = "select id, comp_1, comp_2 from similarity where comp_1 in (%s) and comp_2 in (%s) "

        format_strings1 = format_strings1 % tuple( entry_ids_1 )
        format_strings2 = format_strings2 % tuple( entry_ids_2 )
        
        sql = sql % (format_strings1, format_strings2)

        mycursor.execute( sql )

        result = mycursor.fetchall()

        if len( result ) != 0:

            result = pd.DataFrame( np.array( result ),
                                   columns=['id', 'comp_1', 'comp_2'] )

        else:
            result = pd.DataFrame( columns=['id', 'comp_1', 'comp_2'] )

    except Error as e:
        print( "Error while connecting to MySQL", e )
    finally:
        if mydb.is_connected():
            mycursor.close()
            mydb.close()

    return result

# ----------------------------------------------------------------------------------------------------- #

def save_to_mysql(df, engine, table_name, name_prefix):
    """
    :param df: pandas DataFrame
    :param engine: connection to engine object
    :param table_name: name of the table where the data are saved
    :param name_prefix: Prefix of the concepts to be extracted from the ontology
    :type name_prefix: string
    """
    # save to db with string type instead of int
    df.comp_1 = df.comp_1.map( lambda x: x.lstrip( name_prefix ) ).astype( int )
    df.comp_2 = df.comp_2.map( lambda x: x.lstrip( name_prefix ) ).astype( int )
    """if name_prefix != 'HP_':
        df.comp_1 = df.comp_1.astype( int )
        df.comp_2 = df.comp_2.astype( int )
        """
    df.to_sql( table_name, con=engine, if_exists='append', index=False, \
        method='multi', chunksize=10000 )
