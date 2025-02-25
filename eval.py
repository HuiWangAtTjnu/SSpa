import json
import sqlite3
import re
import datetime
import argparse

def execute_sql(predicted_sql,ground_truth, db_path):
    conn = sqlite3.connect(db_path)
    #
    conn.enable_load_extension(True)
    conn.execute('SELECT load_extension("mod_spatialite.dll")')

    # Connect to the database
    cursor = conn.cursor()
    cursor.execute(predicted_sql)
    predicted_res = cursor.fetchall()
    #
    res = 0
    for gold in ground_truth:
        cursor.execute(gold)
        ground_truth_res = cursor.fetchall()
        #
        if set(predicted_res) == set(ground_truth_res):
            res = 1
            break
    return res


def execute_model(predicted_sql,ground_truth, db_place, idx):
    info = ''
    try:
        res = execute_sql(predicted_sql, ground_truth, db_place)
    except Exception as e:
        info = f'error {e}'
        # result = [(f'error {e}',)]  # possibly len(query) > 512 or not executable
        res = 0
    result = {'sql_idx': idx, 'res': res, 'info': info}
    # print(result)
    return result

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--data_type", type=int, choices=[1, 2, 3, 4],  required=True)
    parser.add_argument("--algo", type=str, choices=["dail_sql", "sspa", "sspa_tips", "sspa_sdbms", "sspa_geo"], default="sspa",  required=True)
    parser.add_argument("--shot", type=int, choices=[0, 1, 3, 5],  required=True)
    # data_type = 1: dataset 1      train set: tourism&traffic              dev set:ada&edu
    # data_type = 2: dataset 1      train set: ada&edu                      dev set:tourism&traffic
    # data_type = 3: dataset 2      train set: tourism&traffic              dev set:ada&edu
    # data_type = 4: dataset 2      train set: ada&edu                      dev set:tourism&traffic
    args = parser.parse_args()
    
    data_type = args.data_type
    algo = args.algo
    shot = args.shot
    #
    # data_type = 1
    # algo = 'sspa'
    # shot = 5
    
    if data_type == 1:
        db_dir = './experiments/dataset1_ada_edu'
        question_dir = f'./experiments/results/{algo}/dataset1_ada_edu_shot_{shot}'
    elif data_type == 2:
        db_dir = './experiments/dataset1_tourism_traffic'
        question_dir = f'./experiments/results/{algo}/dataset1_tourism_traffic_shot_{shot}'
    elif data_type == 3:
        db_dir = './experiments/dataset2_ada_edu'
        question_dir = f'./experiments/results/{algo}/dataset2_ada_edu_shot_{shot}'
    elif data_type == 4:
        db_dir = './experiments/dataset2_tourism_traffic'
        question_dir = f'./experiments/results/{algo}/dataset2_tourism_traffic_shot_{shot}'
    else:
        assert(data_type == 1 or data_type == 2 or data_type == 3 or data_type == 4)
        
    evaluationf = open(f'{question_dir}/evaluations.txt', 'a', encoding = 'utf-8')

    predicted_sql_path = f'{question_dir}/answers.json'
    predicted_dict = {}
    with open(predicted_sql_path, 'r', encoding = 'utf-8') as f:
        _items = json.load(f)
        for _item in _items:
            predicted_dict[_item['id']] = _item['sql']
    #
    gold_sql_path = f'{db_dir}/dev/dev.json'
    gold_dict = {}
    with open(gold_sql_path, 'r', encoding = 'utf-8') as f:
        _items = json.load(f)
        for _item in _items:
            gold_dict[_item['id']] = _item['Evals']
    #
    ids = [key for key in predicted_dict]
    ids.sort()
    #
    for _id in ids:  
        # if _id != 'edu25':
        #     continue
        matchobj = re.match(r'(?P<db>[a-z]+)\d+', _id)
        db = matchobj.group('db')
        db_path = f'{db_dir}/databases/{db}/{db}.sqlite'
        stime = datetime.datetime.now()
        res = execute_model(predicted_dict[_id], gold_dict[_id], db_path, _id)
        etime = datetime.datetime.now()
        nseconds = (etime - stime).seconds
        evaluationf.write(f'{_id},{nseconds},{res}\n')
        evaluationf.flush()
    #
    evaluationf.close()
    print("Finished~")
    