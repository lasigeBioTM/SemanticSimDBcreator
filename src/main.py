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
#  (author: Matilde Pato, matilde.pato@gmail.com)                             #  
#                                                                             #  
#  Note:                                                                      #  
# 1. You must to configure dataset.py for your problem                        #  
#                                                                             #
# 2. If is an HPO then the comp_1 and comp_2 for the similarity semantic DB   #
# is represented in string format, elsewhere is in int type                   #   
#                                                                             #  
###############################################################################
#

import os
import git

if os.path.isdir( "DiShIn" ):
    pass
else:
    print( "Downloading DiShIn" )
    git.Git().clone( "https://github.com/lasigeBioTM/DiShIn" )

import sys

sys.path.insert( 1, '/SemanticSimDBcreator/src/DiShIn' )

from myconfiguration import MyConfiguration as cfg
from calculate_simlarities import *
from database import *
from datetime import datetime
from dataset import upload_dataset

pd.set_option( 'display.max_columns', None )

if __name__ == '__main__':

    start_time = datetime.now()
    # ---------------------------------------------------------------------------------------- #
    # connect db
    check_database()

    # ---------------------------------------------------------------------------------------- #

    # read dataset; select the right columns; select items only from ontology
    # you must 
    
    df_dataset = upload_dataset( cfg.getInstance().dataset,\
                                 cfg.getInstance().item_prefix )
    
    
    # ---------------------------------------------------------------------------------------- #
    # check ontology database
    if os.path.isfile( cfg.getInstance().path_to_ontology ):
        print( "Database ontology file already exists" )

    else:
        print( "Database from owl does not exit. Creating..." )
        ssmpy.create_semantic_base( cfg.getInstance().path_to_owl,
                                    cfg.getInstance().path_to_ontology,
                                    "http://purl.obolibrary.org/obo/",
                                    "http://www.w3.org/2000/01/rdf-schema#subClassOf", "" )

    # ---------------------------------------------------------------------------------------- #
   
    # get item id in the input dataset
    items_ids = get_items_ids( df_dataset, cfg.getInstance().item_prefix )
    print( "n of ids: ", items_ids.shape )
    
    # ---------------------------------------------------------------------------------------- #

    # connection to sqlite database
    conn = create_connection_sqlite( cfg.getInstance().path_to_ontology )

    # ---------------------------------------------------------------------------------------- #

    # creation of engine to MYSQL database to insert pandas DataFrame in the database
    engine = create_engine_mysql()

    # ---------------------------------------------------------------------------------------- #

    calculate_semantic_similarity_chunks( items_ids, conn, engine, "similarity",\
                                          cfg.getInstance().n_split, cfg.getInstance().item_prefix )

    # ---------------------------------------------------------------------------------------- #
    # close connection
    conn.close()

    # ---------------------------------------------------------------------------------------- #
    end_time = datetime.now()
    # save meta-information: date, time, database, dataset and ontology label in the txt file
    with open( '../info_process.txt', 'a' ) as f:
        f.write( f"Date: {datetime.now()} \n\
                Duration: {end_time - start_time}\n"
                 )
        f.write(
            f"Database: {cfg.getInstance().database} \n\
                Dataset: {cfg.getInstance().dataset} \n\
                Ontology: {cfg.getInstance().item_prefix}\n\n"
        )
        f.close()
