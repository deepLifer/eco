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

logger=logging.getLogger('processing')
formatter = logging.Formatter('%(asctime)s-%(filename)s-%(message)s')
fh = logging.FileHandler('processing.log')
fh.setFormatter(formatter)
logger.addHandler(fh)

doc_path = '/home/sergey/devel/eco_monitoring/xmls'
internal_server_ip = '192.168.0.23'
internal_port = '2003'
prefix = 'device__1'

def process_file(filename):
    #print (filename)
    _data = {}
    _processed = False
    _sended = False

    #try to read data from file
    try:
        tree = xml.etree.ElementTree.parse(filename)
        root = tree.getroot()
   
        _data['factory'] = root.find('HEADER').find('ID_FACTORY').text
        _data['source'] = root.find('BODY').find('SOURCE').find('ID_SOURCE').text
        _data['dt_avg'] = root.find('BODY').find('SOURCE').find('DT_AVG').text
        _data['alarm'] = root.find('BODY').find('SOURCE').find('CHEMNEY').find('ID_ALARM').text
        
        _timestamp = time.mktime(datetime.datetime.strptime(_data['dt_avg'],"%d-%m-%Y %H-%M").timetuple())
        #print(_timestamp)
        measure_ids = []
        measure_vals = []
        measure_times=[]

        for measure in root.iter('MEASURE'):
            _id = measure.find('ID_PARAM').text
            _val = measure.find('VAL_AVG').text    
            if _val.find('t')>0:
                _val=_val[3:]
            _dim = measure.find('DIMENSION').text
            

            measure_ids.append(_id)
            measure_vals.append(_val)
            measure_times.append(_timestamp)
    
        _data['measure']=list(zip(measure_ids, measure_vals,measure_times))
        _processed = True
    except Exception as ex:
        logger.error('error with {}, details: {}'.format(filename,ex))
        try:
            shutil.move(filename,doc_path+"/error")
            logger.error('file {} moved to ERROR'.format(filename))
        except Exception as ex_mv:
            logger.error('problem with moving {}, details: {}'.format(filename, ex_mv))

    #try send data to ... 
    try:
        send_data(_data, internal_server_ip, internal_port)
    except Exception as ex:
        logger.error('error with sending data {}, details: {}'.format(filename,ex))
        try:
            shutil.move(filename,doc_path+"/error")
            logger.error('file {} moved to ERROR'.format(filename))
        except Exception as ex_mv:
            logger.error('problem with moving {}, details: {}'.format(filename, ex_mv))
    
    _sended=True
    try:
        shutil.move(filename, doc_path+"/done")
        pass
    except Exception as ex_mv:
        logger.error('problem with moving {}, details: {}'.format(filename, ex_mv))
        
def send_data(data, server_ip, port):
    g = graphitesend.init(graphite_server=server_ip, graphite_port=2003, prefix=prefix, )
    g.send_list(data['measure'])
    pass
 
 
def main_loop():
    for filename in os.listdir(doc_path):
        if filename.endswith(".xml"):
            filename = os.path.join(doc_path, filename)
            process_file(filename)
  
main_loop()