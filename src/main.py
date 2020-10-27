import mysql.connector
import os
import git

if os.path.isdir("DiShIn") == False:
    print("Downliading DiShIn")
    git.Git().clone("https://github.com/lasigeBioTM/DiShIn")

import sys
sys.path.insert(1, '/SemanticSimDBCreator/src/DiShIn')
import ssmpy
import multiprocessing as mp
import configargparse
from calculate_simlarities import *
from database import *



pd.set_option('display.max_columns', None)

if __name__ == '__main__':

    p = configargparse.ArgParser(default_config_files=['../config/config.ini'])
    p.add('-mc', '--my-config', is_config_file=True, help='alternative config file path')

    p.add("-ds", "--path_to_dataset", required=False, help="path to dataset", type=str)

    p.add("-host", "--host", required=False, help="db host", type=str)
    p.add("-user", "--user", required=False, help="db user", type=str)
    p.add("-pwd", "--password", required=False, help="db password", type=str)
    p.add("-db_name", "--database", required=False, help="db name", type=str)

    p.add("-owl", "--path_to_owl", required=False, help="path to owl ontology", type=str)
    p.add("-db_onto", "--path_to_ontology_db", required=False, help="path to ontology db", type=str)

    p.add("-n_split", "--n_split_dataset", required=False, help="number to split the list of entities", type=int)


    options = p.parse_args()

    dataset = options.path_to_dataset

    host = options.host
    user = options.user
    password = options.password
    database = options.database
    path_to_owl = options.path_to_owl
    path_to_ontology = options.path_to_ontology_db
    n_split = options.n_split_dataset

    check_database(host, user, password, database)

    df_dataset = pd.read_csv(dataset, names=['user', 'item', 'rating'], sep=',')



    if os.path.isfile(path_to_ontology) == False:
        print("chebi DB does not exit. Creating...")
        ssmpy.create_semantic_base(path_to_owl, path_to_ontology,
                                   "http://purl.obolibrary.org/obo/",
                                   "http://www.w3.org/2000/01/rdf-schema#subClassOf", "")

    else:
        print("chebi.db file already exists")


    # input: csv with user, item, rating
    chebi_ids = get_chebi_ids(df_dataset)
    print("n of ids: ", chebi_ids.shape)

    # calculate_semantic_similarity(chebi_ids, host, user, password, database, path_to_ontology)

    # connection to sqlite database
    conn = create_connection_sqlite(path_to_ontology)

    # connection to MYSQL database
    conn_mysql = create_connection_mysql(user, host, password, database)

    # creation of engine to MYSQL database to insert pandas DataFrame in the database
    engine = create_engine_mysql(host, user, password, database)

    calculate_semantic_similarity_chunks(chebi_ids, conn, conn_mysql, engine, "similarity", n_split)

    conn.close()
    conn_mysql.close()
