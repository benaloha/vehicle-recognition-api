import requests
import os
import json
import time
#from multiprocessing.pool import ThreadPool as Pool
#from multiprocessing import Pool
from concurrent.futures import ThreadPoolExecutor

def process_file(path, dirEntry):
    print("[{}] Start work.".format(dirEntry.name))
    if dirEntry.is_file():
        if dirEntry.name.endswith('.jpg') or dirEntry.name.endswith('.thumb'):
            file = open(dirEntry, 'rb')
            files = {"image": file}
            start = time.time()
            res = requests.post(url='http://rpi4gb', files=files)
            end = time.time()
            print("[{}] Object detection took {:.6f} seconds.".format(dirEntry.name, end - start))

            if res.status_code == 200:
                cars = res.json()['cars']
                if cars == []:
                    print("[{}] No car in file, remove.".format(dirEntry.name))
                    os.remove(dirEntry)
                else:
                    extra_fn = ''
                    for car in cars:
                        extra_fn = extra_fn + "--{}-{}-{}".format(car['make'], car['model'], car['color'])
                    fn_parts = dirEntry.name.split('.')
                    newPath = path + '/cars/' + \
                    fn_parts[0] + extra_fn + '.' + fn_parts[1]
                    print("[{}] Move file to: {}.".format(dirEntry.name, newPath))
                    os.rename(dirEntry.path, newPath)
        else:
            print("[{}] No picture file, remove.".format(dirEntry.name))
            os.remove(dirEntry)

    print("[{}] Finished work.".format(dirEntry.name))


path = '../../temp/2021-03-08 (copy)'
with os.scandir(path) as entries:
    print("Analyse path: " + path)

    try:
        os.mkdir(path + "/cars")
    except:
        pass

    with ThreadPoolExecutor(max_workers = 2) as executor:
        {executor.submit(process_file, path, dirEntry): dirEntry for dirEntry in entries}

    print("Finished analysing path: " + path)





