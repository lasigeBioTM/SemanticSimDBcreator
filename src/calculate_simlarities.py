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
# 
import ssmpy
import numpy as np
from database import *


def calculate_semantic_similarity_chunks(entry_ids, conn, engine, table_name, n_split, name_prefix ):
    """

    :param entry_ids: list of entries ids
    :param conn: connection object to sqlite
    :param engine: connection to engine object
    :param table_name: name of the table where the data are saved
    :param n_split: number to split the list of entities
    :param n_split: int
    :param name_prefix: Prefix of the concepts to be extracted from the ontology
    :type name_prefix: string
    :return:
    """
    
    items_splitted = np.array_split( np.array( entry_ids ), n_split )

    aux_array = np.arange( 0, n_split, 1 )

    for i in aux_array:
        for n in aux_array:
            print( i, n )

            list_1 = items_splitted[i].tolist()
            list_2 = items_splitted[n].tolist()
            # if we consider HPO then we must transform to a string because of the
            # '0000000' format (i.e. 7 digits)
            if name_prefix == 'HP_':
                list_1 = [f'{s:07d}' for s in list_1]
                list_2 = [f'{s:07d}' for s in list_2]

            list_of_sims_from_db = get_sims( list_1, list_2 )
            
            list_1, list_2 = confirm_all_test_train_similarities( list_1, list_2, 
                list_of_sims_from_db )
           
            if len( list_1 ) | len( list_2 ) == 0:
                continue

            list_1 = [name_prefix + str(s) for s in list_1]
            list_2 = [name_prefix + str(s) for s in list_2]    
             
            results = ssmpy.light_similarity( conn, list_1, list_2, "all", 20 )
            newest = [item for items in results for item in items]
            sim_df = pd.DataFrame( newest, columns=["comp_1", "comp_2", "sim_resnik", "sim_lin", "sim_jc"] )
            
            save_to_mysql( sim_df, engine, table_name, name_prefix )

        mask = np.where( aux_array == i )
        aux_array = np.delete( aux_array, mask )
