# SemanticSimDBcreator
Semantic Similarity Database Creator 

This tool creates a mySQL database with the semantic similarity between two entities in an ontology, using the framework DiShIn (https://github.com/lasigeBioTM/DiShIn).
The database has a table (similarity) with 6 columns (id, comp_1, comp_2, sim_resnik, sim_lin, sim_jc)

## Requirements:
* Docker
* mySQL

## Data:
CSV with the dataset: https://drive.google.com/open?id=1AbYgGw7V7KgSLudwxBAbH4yZrwHlBuFG (cheRM_20_200.csv)

## Run:

```
docker build -t "chebi_sim" .
docker run -t -d --name chebi_sim_container --net=host -v /path/to/data:/mlData -v /path/to/SemanticSimDBcreator:/SemanticSimDBCreator chebi_sim
docker exec -it chebi_sim_container bash
cd /config 
```
edit config.ini file
```
cd /SemanticSimDBCreator/src
python main.py
```



