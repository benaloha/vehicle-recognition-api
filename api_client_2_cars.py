import requests
import os
import json

path = '../../temp/2021-03-01 (copy)'
with os.scandir(path) as entries:
    print("analyse path: " + path)

    try:
        os.mkdir(path + "/cars")
    except:
        pass

    for entry in entries:
        print("analyse image: " + entry.name)
        if entry.is_file():
            if entry.name.endswith('.jpg') or entry.name.endswith('.thumb'):
                file = open(entry, 'rb')
                files={"image": file}
                res=requests.post(url='http://10.152.183.224:32334',
                                  files=files)

                if res.status_code == 200:
                    cars=res.json()['cars']
                    if cars == []:
                        print("no car in file, remove: " + entry.name)
                        os.remove(entry)
                    else:
                        prefix = ''
                        for car in cars:
                            prefix = prefix + "{}-{}-{}--".format(car['make'], car['model'], car['color'])
                        #dubieus stuk, zolang ik m'n motion det. niet goed krijg. Er staat altijd wel 1 gep. auto op
                        if len(cars) > 1:
                            newPath=path + '/cars/' + prefix + entry.name
                            print("move file to: " + newPath)
                            os.rename(entry.path, newPath)
                        else: # ws 1 geparkeerde auto..
                            print("no moving car, remove: " + entry.name)
                            os.remove(entry)

            else:
                print("no picture, remove: " + entry.name)
                os.remove(entry)




