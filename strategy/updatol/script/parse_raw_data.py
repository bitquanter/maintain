#!/usr/bin/env python
# coding: utf-8
import time
import json
import os
import csv
import zipfile
import gzip
from os.path import join

input_path = '/home/zhangwei/zhangwei/1token_realtime_get/data_save_directory'
output_path = '/home/zhengdalong/outputs'


def parse_kline_data():
    for data in os.walk(input_path):
        in_path = data[0]
        if input_path in in_path and 'kline' in in_path:
            out_path = in_path.replace(input_path, output_path)
            if not os.path.exists(out_path):
                os.makedirs(out_path)
            print(out_path)
            files = data[2]
            for file in files:
                file_p = join(in_path, file)
                csv_p = join(out_path, file.replace('.json.gz','.csv'))
                with open(csv_p, "a", newline='') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(['timestamp','open', 'close', 'high', 'low', 'volume', 'amount'])
                    g_file = gzip.GzipFile(file_p)
                    data = g_file.readline()
                    tmp_dic = {}
                    while data:
                        data = g_file.readline()
                        try:
                            json_str = json.loads(data.decode())
                        except:
                            pass
                        else:
                            date = json_str['time']
                            dateTime = date.replace('T', " ").replace('Z', "")
                            stamp_array = time.strptime(dateTime, '%Y-%m-%d %H:%M:%S')
                            timestamp = int(time.mktime(stamp_array))
                            if timestamp not in tmp_dic:
                                tmp_dic[timestamp] = []
                            open_ = json_str['open']
                            close = json_str['close']
                            high = json_str['high']
                            low = json_str['low']
                            volume = json_str['volume']
                            amount = json_str['amount']
                            item = [timestamp,open_, close,high,low, volume,amount]
                            tmp_dic[timestamp].append(item)
                    for tim in tmp_dic:
                        writer.writerow(tmp_dic[tim][-1])

    pass


if __name__ == '__main__':
    parse_kline_data()
    # from argparse import ArgumentParser
    # parser = ArgumentParser()
    # parser.add_argument('-t', '--task', default='kline')
    # options = parser.parse_args()
    # if options.task == 'kline':
    #     parse_kline_data()
    # else:
    #     print('invalid task')
    pass
