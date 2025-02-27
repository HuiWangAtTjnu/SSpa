# SSpa
Overview
=

The data and code were created for the review of the paper titled "GPT-Based Text-to-SQL for Spatial Databases". 

Datasets
=

The folder `sdbdatasets` contains the datasets we created specifically for spatial databases, including `dataset1` and `dataset2`.<br>

In `dataset1`, there are four databases (folders): `ada`, `edu`, `tourism`, and `traffic`. Taking the folder `ada` as an example:
* The file `ada.sqlite` is an SQLite database file (We can use [spatialite-gui](https://www.gaia-gis.it/fossil/spatialite_gui/index), an open-source graphical user interface tool, to manage SQLite database files). <br>
* The file `ada.table.csv` contains geographic region descriptions for each database table, supporting both Chinese and English. <br>
* The file `QA-ada-56.txt` stores questions and answers based on the `ada` database. <br>

Below is two examples from the file `QA-ada-56.txt`: <br>

     label:G S
     questionCHI:请问太湖的面积是多少？
     evidenceCHI:太湖是由多个名称相同的湖泊区域组成。只需给出面积。
     nameCHI:太湖以'太湖'为名称表示。
     question:What is the area of Lake Tai?
     evidence:Lake Tai is composed of multiple sections of water with the same name. Only provide the area.
     name:Lake Tai is represented by the name '太湖'.
     SQL: Select Sum(Area)  from lakes where name = '太湖'  %%% Select Sum(Area(Shape, 1))   from lakes where name = '太湖'
     Eval: Select Sum(Area)  from lakes where name = '太湖'  %%% Select Sum(Area(Shape, 1))   from lakes where name = '太湖'
     id: ada01
     


     
     label:Intersection S
     questionCHI:每个省内1级河流的总长度是多少？
     evidenceCHI:一条河流由多个同名河段组成，应计算其在各省境内的交汇部分长度。
     nameCHI:
     question:What is the total length of all Level 1 rivers within each province?
     evidence:A river is composed of multiple sections with the same name, and its intersecting lengths within each province should be calculated.
     name:
     SQL:Select provinces.name, Sum(GLength(Intersection(provinces.Shape, rivers.Shape), 1))  from provinces inner join rivers On Intersects(provinces.Shape, rivers.Shape) = 1 where level_river = 1 group by provinces.name %%% Select cities.province, Sum(GLength(Intersection(cities.Shape, rivers.Shape), 1))  from cities inner join rivers On Intersects(cities.Shape, rivers.Shape) = 1 where level_river = 1 group by cities.province
     Eval:Select provinces.name, Sum(GLength(Intersection(provinces.Shape, rivers.Shape), 1))  from provinces inner join rivers On Intersects(provinces.Shape, rivers.Shape) = 1 where level_river = 1 group by provinces.name %%% Select cities.province, Sum(GLength(Intersection(cities.Shape, rivers.Shape), 1))  from cities inner join rivers On Intersects(cities.Shape, rivers.Shape) = 1 where level_river = 1 group by cities.province %%% Select provinces.name, Sum(GLength(Intersection(rivers.Shape, provinces.Shape), 1))  from provinces inner join rivers On Intersects(provinces.Shape, rivers.Shape) = 1 where level_river = 1 group by provinces.name %%% Select cities.province, Sum(GLength(Intersection(rivers.Shape, cities.Shape), 1))  from cities inner join rivers On Intersects(cities.Shape, rivers.Shape) = 1 where level_river = 1 group by cities.province
     id: ada34
 




The meaning of each field is as follows:  


     |Field       | Description  
     |------------|-------
     |label       | For the SQL queries related to the question, 'G' denotes a general query, and 'S' represents a spatial query.
     |question    | The question in natural language. 
     |evidence    | Supporting knowledge.
     |name        | Real values of some phrases from the 'question' field in the database. 
     |questionCHI | The Chinese translation of the 'question' field.
     |evidenceCHI | The Chinese translation of the 'evidence' field.
     |nameCHI     | The Chinese translation of the 'name' field.
     |SQL         | The SQL query corresponding to the 'question' field. Due to derived columns, there may be multiple SQL queries, separated by '%%%'. 
     |Eval        | SQL queries corresponding to all results. When evaluating the predicted SQL queries with execution accuracy, results like 'GLength(Intersection(rivers.Shape, cities.Shape), 1)' and 'GLength(Intersection(cities.Shape, rivers.Shape), 1)' may differ. 
     |id          | The unique ID for the question.  


In `dataset2`, there are also four databases: `ada`, `edu`, `tourism`, and `traffic`.  
* The `tourism` database in `dataset2` is the same as the `tourism` database in `dataset1`.  
* The `ada`, `edu`, and `traffic` databases in `dataset2`  are derived from the corresponding databases in `dataset1`  by removing the derived columns.  
* The questions in both `dataset1`  and `dataset2`  are identical for each database.




Environment Setup
=
    

   To set up the environment, you should download the [Stanford CoreNLP](http://nlp.stanford.edu/software/stanford-corenlp-full-2018-10-05.zip), unzip it to the folder `./third_party/`, and rename `stanford-corenlp-full-2018-10-05` to `stanfordnlp`. Next, you need to launch the coreNLP server:



    install default-jre
    install default-jdk
    cd third_party/stanfordnlp
    java -mx4g -cp "*" edu.stanford.nlp.pipeline.StanfordCoreNLPServer -port 9000 -timeout 15000


   
   In addition,
   
   

    python -m pip install --upgrade pip
    pip install -r requirements.txt
    python nltk_downloader.py



   You can also refer to the installation steps in [DAIL-SQL](https://github.com/BeachWang/DAIL-SQL).

Run
======

Data Preprocess
------
This step includes copying databases from `sdbdatasets` to the corresponding folders (`experiments/dataset1_ada_edu`, `experiments/dataset1_tourism_traffic`,  `experiments/dataset2_ada_edu`, and `experiments/dataset2_tourism_traffic`) and applying required processing operations.<br>


* The folder `dataset1_ada_edu` indicates that the training set is built using data from the `tourism` and `traffic` databases in `dataset1`, and predictions are made for questions related to the `ada` and `edu` databases.
* The folder `dataset1_tourism_traffic` indicates that the training set is built using data from the `ada` and `edu` databases in `dataset1`, and predictions are made for questions related to the `tourism` and `traffic` databases.
* The folder `dataset2_ada_edu` indicates that the training set is built using data from the `tourism` and `traffic` databases in `dataset2`, and predictions are made for questions related to the ada and edu databases.
* The folder `dataset2_tourism_traffic` indicates that the training set is built using data from the `ada` and `edu` databases in `dataset2`, and predictions are made for questions related to the `tourism` and `traffic` databases.

<br>

    
    python data_preprocess.py


    

 
Prompt Generation
------
This step will generate corresponding questions (prompts) for each method (`dail_sql`, `sspa`, `sspa_geo`, `sspa_sdbms`, `sspa_tips`) across different datasets (`dataset1_ada_edu`, `dataset1_tourism_traffic`, `dataset2_ada_edu`, `dataset2_tourism_traffic`) and scenarios (shot-0, shot-1, shot-3, shot-5), and store the generated questions (prompts) in the folder `experiments/results`.

    
    python generate_question.py



This step will create 80 folders (5 methods, with 16 folders created for each method). Taking the `sspa` method as an example, as shown in the figure below.<br>
![image](https://github.com/HuiWangAtTjnu/SSpa/blob/main/pics/pic1.png)<br>


* `dataset1_ada_edu_shot_5` refers to the case where the `tourism` and `traffic` data from `dataset1_ada_edu` are used as the training set (i.e., `5` examples similar to the target question are selected from `tourism` and `traffic`), and questions (prompts) are generated for each origianl question in the `Ada` and `Edu` databases. <br>

* `dataset1_tourism_traffic_shot_5` refers to the case where the `Ada` and `Edu` data from `dataset1_ada_edu` are used as the training set (i.e., `5` examples similar to the target question are selected from `Ada` and `Edu`), and questions (prompts) are generated for each original question in the `Tourism` and `Traffic` databases.
<br>



The following figure shows the files within the folder `dataset1_ada_edu_shot_5`, where `questions.json` is used to store the generated questions (prompts).<br>


![image](https://github.com/HuiWangAtTjnu/SSpa/blob/main/pics/pic2.png)<br>

Calling the LLM
------

   
This step involves sending the questions (prompts) generated in the previous step to the LLM in order to generate the corresponding SQL queries. Since there are 80 folders in total, processing them all at once can be time-consuming. Therefore, the questions (prompts) from each folder can be sent to the LLM individually, and the results will be stored in the respective `answers.json` file within each folder (as shown in the figure above).
<br>

    
    python ask_llm.py --dataset dataset1 --databases ada_edu --algo sspa --shot 5 --model gpt-4-turbo-2024-04-09


    

 
The parameter `dataset` can only be `dataset1` or `dataset2`, the parameter `databases` can only be `ada_edu` or `tourism_traffic`, the parameter `algo` can only be one of the following: `sspa`, `sspa_geo`, `ssap_tips`, `sspa_sdbms`, or `dail_sql`, the parameter `shot` can only be one of the values: `0`, `1`, `3`, or `5`, and the `model` parameter refers to the LLM being used, which in this case is `gpt-4-turbo-2024-04-09`. Additionally, you need to modify the `api_key` and `base_url` parameters in the file `llm/chatgpt.py`.

Evaluation
------
This step involves evaluating the predicted SQL queries using execution accuracy.<br>

    
    python ask_llm.py --dataset dataset1 --databases ada_edu --algo sspa --shot 5


    

 
The parameter `dataset` can only be `dataset1` or `dataset2`, the parameter `databases` can only be `ada_edu` or `tourism_traffic`, the parameter `algo` can only be one of the following: `sspa`, `sspa_geo`, `ssap_tips`, `sspa_sdbms`, or `dail_sql`, the parameter `shot` can only be one of the values: `0`, `1`, `3`, or `5`.

Statistics
------
This step involves aggregating all the experimental results. The file `experiments/results/statistics.txt` records all the data for the figures and tables presented in the paper.<br>
 
    
    python calculate.py



Acknowledgement
------

The code is inspired by [DAIL-SQL](https://github.com/BeachWang/DAIL-SQL).


References
------
Gao, D., et al. 2024. Text-to-SQL empowered by large language models: A benchmark evaluation. Proceedings of the VLDB Endowment, 17(5), 1132–1145.
    
