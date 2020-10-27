# SemanticSimDBcreator
Semantic Similarity Database Creator 

This tool creates a mySQL database with the semantic similarity between two entities in an ontology, using the framework DiShIn (https://github.com/lasigeBioTM/DiShIn).
The database has a table (similarity) with 6 columns (id, comp_1, comp_2, sim_resnik, sim_lin, sim_jc)

## Requirements:
* python => 3.5
* Check requirements file

## Data:
* CSV with the dataset: https://drive.google.com/open?id=1AbYgGw7V7KgSLudwxBAbH4yZrwHlBuFG (cheRM_20_200.csv for tests)
* Chebi OWL file (https://www.ebi.ac.uk/chebi/downloadsForward.do)


## Run info
* In /config/config.ini alter for your configurations
* Copy the owl file to the /data folder
* In /src run: 

```
python main.py
```


## Run in Docker
If you wish to run this code in a docker container, I'm providing a Dockerfile and the instructions on how to use Docker


### Docker with mySQL in localhost:

```
docker build -t "chebi_sim" .
docker run -t -d --name chebi_sim_container --net=host -v /path/to/SemanticSimDBcreator:/SemanticSimDBCreator chebi_sim
docker exec -it chebi_sim_container bash
cd /config 
```
edit config.ini file
```
cd /SemanticSimDBCreator/src
python main.py
```

## Run defining mySQL storage:

```
docker run \
--detach \
--name=chebi-mysql \
--env="MYSQL_ROOT_PASSWORD=1234" \
--publish 6603:3306 \
--volume=/path/to/mysql/folder:/var/lib/mysql \
mysql

docker build -t "chebi_simmysql" .
docker run -t -d --name chebi_simmysql_container --link chebi-mysql:mysql  -v /path/to/SemanticSimDBcreator:/SemanticSimDBcreator chebi_simmysql
docker exec -it chebi_simmysql_container bash

```
edit config.ini file
```
cd /SemanticSimDBCreator/src
python main.py
```


## Output
The output of this tool is a mySQL database with table (similarity) containing 6 columns (id, comp_1, comp_2, sim_resnik, sim_lin, sim_jc)

- comp_1 and comp_2 are the IDs for chebi compounds
