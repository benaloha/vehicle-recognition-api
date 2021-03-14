import httpx
import os
import json
import time
import asyncio
#from multiprocessing.pool import ThreadPool as Pool
#from multiprocessing import Pool

async def process_file(path, dirEntry):
    print("[{}] Start work.".format(dirEntry.name))
    if dirEntry.is_file():
        if dirEntry.name.endswith('.jpg') or dirEntry.name.endswith('.thumb'):
            limits = httpx.Limits(max_keepalive_connections=8, max_connections=8)
            async with httpx.AsyncClient(limits=limits) as client:
                file = open(dirEntry, 'rb')
                files = {"image": file}
                start = time.time()
                res = await client.post(url='http://localhost', files=files)
                end = time.time()
                print("[{}] Object detection took {:.6f} seconds.".format(dirEntry.name, end - start))

                if res.status_code == 200:
                    cars = res.json()['cars']
                    print("[{}] Response: {}".format(dirEntry.name, cars))
                    if cars == []:
                        print("[{}] No car in file, remove.".format(dirEntry.name))
                        os.remove(dirEntry)
                    else:
                        extra_fn = ''
                        for car in cars:
                            extra_fn = extra_fn + "--{}-{}-{}".format(car['make'], car['model'], car['color'])
                        fn_parts = dirEntry.name.split('.')
                        newPath = path + '/cars/' + fn_parts[0] + extra_fn + '.' + fn_parts[1]
                        print("[{}] Move file to: {}.".format(dirEntry.name, newPath))
                        os.rename(dirEntry.path, newPath)
        else:
            print("[{}] No picture file, remove.".format(dirEntry.name))
            os.remove(dirEntry)

    print("[{}] Finished work.".format(dirEntry.name))


async def main():
    path = '../../temp/2021-03-08 (copy)'
    
    with os.scandir(path) as entries:
        print("Analyse path: " + path)

        try:
            os.mkdir(path + "/cars")
        except:
            pass

        task_list = []
        for entry in entries:
            print("[{}] Append task for entry.".format(entry.name))
            task_list.append(process_file(path, entry))
        await asyncio.gather(*task_list)
        print("Finished main()")

if __name__ == "__main__":
    start_time = time.monotonic()
    asyncio.run(main())
    print(f"Time Taken:{time.monotonic() - start_time}")





