import pandas as pd
import numpy as np
import sys
import os
import multiprocessing as mp

#sys.path.insert(1, '/DiShin')
import ssmpy
from database import *


def calculate_semantic_similarity_chunks(chebi_ids, conn, conn_mysql, engine, table_name, n_split):
    """

    :param chebi_ids: list of ids (int)
    :param conn: connection to sqlite
    :param conn_mysql: connection to mysql
    :param engine: connection to engine
    :param table_name: name of the table where the data are saved
    :return:
    """

    items_splitted = np.array_split(np.array(chebi_ids), n_split)

    aux_array = np.arange(0, n_split, 1)

    for i in aux_array:
        for n in aux_array:
            print(i, n)

            list_1 = items_splitted[i].tolist()
            list_2 = items_splitted[n].tolist()
            print("size of list 1: ", len(list_1), "size of list 2: ", len(list_2))
            list_of_sims_from_db = get_sims(conn_mysql, list_1, list_2)

            list_1, list_2 = confirm_all_test_train_similarities(list_1, list_2, list_of_sims_from_db)

            if len(list_1) | len(list_2) == 0:
                continue

            list_1 = ["CHEBI_" + str(s) for s in list_1]
            list_2 = ["CHEBI_" + str(s) for s in list_2]

            resutls = ssmpy.light_similarity(conn, list_1, list_2, 'all', 20)
            newlist = [item for items in resutls for item in items]
            sim_df = pd.DataFrame(newlist, columns=["comp_1", "comp_2", "sim_resnik", "sim_lin", "sim_jc"])
            save_to_mysql(sim_df, engine, table_name)

        mask = np.where(aux_array == i)
        aux_array = np.delete(aux_array, mask)


def calculate_sim_it1_it2(it1, it2, e1, host, user, password, database):
    if check_if_pair_exist(host, user, password, database, it1, it2) == False:

        it2_ = "CHEBI_" + str(it2)

        # print("   ", it2_)
        try:
            e2 = ssmpy.get_id(it2_)
            items_sim_resnik = ssmpy.ssm_resnik(e1, e2)
            items_sim_lin = ssmpy.ssm_lin(e1, e2)
            items_sim_jc = ssmpy.ssm_jiang_conrath(e1, e2)
            insert_row(host, user, password, database, it1.item(), it2.item(), items_sim_resnik, items_sim_lin,
                       items_sim_jc)

            sys.stdout.flush()
        except TypeError:
            print(it1, " or ", it2, " not found.")


    else:
        print(it1, it2, " pair already exists")


def calculate_semantic_similarity(chebi_ids, host, user, password, database, path_to_ontology):
    ssmpy.semantic_base(path_to_ontology)

    count = 0
    for it1 in chebi_ids:
        it1_ = "CHEBI_" + str(it1)
        print(it1_)
        e1 = ssmpy.get_id(it1_)

        # pool = mp.Pool(mp.cpu_count())
        pool = mp.Pool(20)
        pool.starmap(calculate_sim_it1_it2, [(it1, it2, e1, host, user, password, database) for it2 in chebi_ids])

        pool.close()

        mask = np.where(chebi_ids == it1)
        chebi_ids = np.delete(chebi_ids, mask)
        count += 1
        print(count)


def calculate_semantic_similarity_gpu(chebi_ids, host, user, password, database, path_to_ontology):
    ssmpy.semantic_base(path_to_ontology)

    count = 0
    for it1 in chebi_ids:
        it1_ = "CHEBI_" + str(it1)
        print(it1_)
        e1 = ssmpy.get_id(it1_)

        # pool = mp.Pool(mp.cpu_count())

        calculate_sim_it1_it2_test_gpu(it1, e1, host, user, password, database, chebi_ids)

        mask = np.where(chebi_ids == it1)
        chebi_ids = np.delete(chebi_ids, mask)
        count += 1
        print(count)
