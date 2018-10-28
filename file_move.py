import shutil
import xml
import os
import logging
import time
import datetime
from math import ceil
from os import path
from random import random, randrange
from xml.etree.ElementTree import Element, SubElement, Comment, tostring
from xml.dom import minidom
import graphitesend

max_vals = {'41526':25, '41506':200,'41509':250, '41504':30, '41512':200, '41505':300}

# 41526 - Кислород        20
# 41506 - Двуокись азота  1-200
# 41509 - Двуокись серы   2-250
# 41504 - Хлороводород    0.2 - 30 
# 41512 - Угарный газ     2 - 200 
# 41505 - Окись азота     3 - 300

logger=logging.getLogger('processing')
formatter = logging.Formatter('%(asctime)s-%(filename)s-%(message)s')
fh = logging.FileHandler('processing.log')
fh.setFormatter(formatter)
logger.addHandler(fh)

doc_path = '/home/sergey/devel/eco_monitoring/xmls'
internal_server_ip = '192.168.0.23'
internal_port = '2003'
prefix = 'device__1'


external_server_ip = '192.168.0.23'
external_port = '2003'

def measure_filter(id, val, max_array):
    if float(val)>max_array[id]:
        return max_array['id']-0.02
    else:
        return val

def process_file(filename):
    #print (filename)
    _data = {}
    _processed = False
    _sended = False

    #try to read data from file
    try:
        tree = xml.etree.ElementTree.parse(filename)
        root = tree.getroot()
        _data['alarm'] = ''
        _data['factory'] = root.find('HEADER').find('ID_FACTORY').text
        _data['source'] = root.find('BODY').find('SOURCE').find('ID_SOURCE').text
        _data['dt_avg'] = root.find('BODY').find('SOURCE').find('DT_AVG').text
        try:
            _data['alarm'] = root.find('BODY').find('SOURCE').find('CHEMNEY').find('ID_ALARM').text
        except Exception:
            pass
            
        _timestamp = time.mktime(datetime.datetime.strptime(_data['dt_avg'],"%d-%m-%Y %H-%M").timetuple())
        #print(_timestamp)
        measure_ids = []
        measure_vals = []
        measure_vals_filtered=[]
        measure_times=[]

        for measure in root.iter('MEASURE'):
            _id = measure.find('ID_PARAM').text
            _val = measure.find('VAL_AVG').text    
            if _val.find('t')>0:
                _val=_val[3:]
            _dim = measure.find('DIMENSION').text
            

            measure_ids.append(_id)
            measure_vals.append(_val)
            measure_vals_filtered.append(measure_filter(_id, _val, max_vals))
         
            measure_times.append(_timestamp)

        _data['measure']=list(zip(measure_ids, measure_vals,measure_times))
        _data['measure_filtered']= list(zip(measure_ids, measure_vals_filtered,measure_times))
        _processed = True
    except Exception as ex:
        logger.error('error with {}, details: {}'.format(filename,ex))
        try:
            shutil.move(filename,doc_path+"/error")
            logger.error('file {} moved to ERROR'.format(filename))
        except Exception as ex_mv:
            logger.error('problem with moving {}, details: {}'.format(filename, ex_mv))

    #try send data to internal server 
    try:
        send_data(_data, internal_server_ip, internal_port)
    except Exception as ex:
        logger.error('error with sending data internal server {}, details: {}'.format(filename,ex))
        try:
            #shutil.move(filename,doc_path+"/error")
            logger.error('file {} moved to ERROR'.format(filename))
        except Exception as ex_mv:
            logger.error('problem with moving {}, details: {}'.format(filename, ex_mv))
    
    _sended=True

#try send data to external server 
    try:
        send_data(_data, external_server_ip, external_port)
    except Exception as ex:
        logger.error('error with sending data external server {}, details: {}'.format(filename,ex))
        try:
            #shutil.move(filename,doc_path+"/error")
            logger.error('file {} moved to ERROR'.format(filename))
        except Exception as ex_mv:
            logger.error('problem with moving {}, details: {}'.format(filename, ex_mv))


    try:
        shutil.move(filename, doc_path+"/done")
        pass
    except Exception as ex_mv:
        logger.error('problem with moving {}, details: {}'.format(filename, ex_mv))
        
def send_data(data, server_ip, port):
    g = graphitesend.init(graphite_server=server_ip, graphite_port=2003, prefix=prefix, )
    g.send_list(data['measure'])
    if data['alarm']!='':
        g.send('alarm', data['alarm'], data['measure'][0][2])
    pass
 
 
def main_loop():
    for filename in os.listdir(doc_path):
        if filename.endswith(".xml"):
            filename = os.path.join(doc_path, filename)
            process_file(filename)
  
main_loop()