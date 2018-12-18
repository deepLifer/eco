import configparser
import datetime
import logging
import os
import shutil
import sys
import time
import xml
from math import ceil
from os import path
from random import random, randrange, normalvariate
from xml.dom import minidom
from xml.etree.ElementTree import Comment, Element, SubElement, tostring
import graphitesend


 
# 41526 - Кислород        30
# 41506 - Двуокись азота  1-200       max 200
# 41509 - Двуокись серы   2-250       max 50
# 41504 - Хлороводород    0.2 - 30    max 10
# 41512 - Угарный газ     2 - 200     max 50
# 41505 - Окись азота     3 - 300     max 200

max_vals = {}
config_name = ""
logger=None  
doc_path = ""
prefix = ""
internal_server_ip = ""
external_server_ip = ""
internal_port = ""
external_port = ""
sections = ("41526", "41506", "41509", "41504", "41505", "41512", "NOx")



def create_config(path):
    """
    Create a config file
    """
    config = configparser.ConfigParser()
    config.add_section("41526")
    config.set("41526","label","кислород")
    config.set("41526","max","100")
    config.set("41526","fake_m","17")
    config.set("41526","fake_d","1")

    config.add_section("41506")
    config.set("41506","label","двуокись азота")
    config.set("41506","max","160")
    config.set("41506","fake_m","17")
    config.set("41506","fake_d","1")

    config.add_section("41509")
    config.set("41509","label","двуокись серы")
    config.set("41509","max","50")
    config.set("41509","fake_m","17")
    config.set("41509","fake_d","1")

    config.add_section("41504")
    config.set("41504","label","хлороводород")
    config.set("41504","max","10")
    config.set("41504","fake_m","17")
    config.set("41504","fake_d","1")    

    config.add_section("41512")
    config.set("41512","label","угарный газ")
    config.set("41512","max","50")
    config.set("41512","fake_m","17")
    config.set("41512","fake_d","1")

    config.add_section("41505")
    config.set("41505","label","окись азота")
    config.set("41505","max","26")
    config.set("41505","fake_m","17")
    config.set("41505","fake_d","1")

    config.add_section("NOx")
    config.set("41505","label","азоты")
    config.set("41505","max","200")

    config.add_section("network")
    config.set("network", "internal_server_ip", "192.168.0.250")
    config.set("network", "internal_port", "2003")
    config.set("network", "external_server_ip", "23.20.213.83")
    config.set("network", "external_port", "2003")

    config.add_section("general")
    config.set("general", "doc_path", "xmls")
    config.set("general", "prefix", "device_11")
    config.set("general", "send_real_internal", "1")
    config.set("general", "send_real_external", "1")
    config.set("general", "send_filtered_external", "1")
    config.set("general", "send_fake_external", "1")


    with open(path, "w") as config_file:
        config.write(config_file)


def get_config(path):
    """
    Returns the config object
    """
    if not os.path.exists(path):
        create_config(path)
    
    config = configparser.ConfigParser()
    config.read(path)
    return config
 
 
def get_setting(path, section, setting):
    """
    Print out a setting
    """
    config = get_config(path)
    value = config.get(section, setting)
    msg = "{section} {setting} is {value}".format(
        section=section, setting=setting, value=value
    )
    
    #print(msg)
    return value


def init():
    global max_vals
    global config_name
    global logger  
    global doc_path
    global prefix
    global internal_server_ip
    global external_server_ip
    global internal_port
    global external_port

    config_name = sys.argv[1]
    doc_path = get_setting(config_name, "general", "doc_path")
    prefix = get_setting(config_name, "general", "prefix")

    internal_server_ip = get_setting(config_name, "network", "internal_server_ip")
    external_server_ip = get_setting(config_name, "network", "external_server_ip")
    internal_port = get_setting(config_name, "network", "internal_port")
    external_port = get_setting(config_name, "network", "external_port")

    max_vals={}
    for x in sections:
        max_vals[x]=get_setting(config_name,x,"max")

    logger=logging.getLogger('processing')
    formatter = logging.Formatter('%(asctime)s-%(filename)s-%(message)s')
    fh = logging.FileHandler('processing.log')
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    

def measure_filter(id, val, max_array):
    if float(val)>float(max_array[id]):
        res = 0.9*float(max_array[id])-random()*0.05*float(max_array[id])
        if res<0:
            res=0
        return res
    else:
        return val
 
def process_file(filename):
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
        
        measure_ids = []
        measure_vals = []
        measure_vals_filtered=[]
        measure_vals_fake=[]
        measure_times=[]
 
        for measure in root.iter('MEASURE'):
            _id = measure.find('ID_PARAM').text
            _val = measure.find('VAL_AVG').text    
            if _val.find('t')>0:
                _val=_val[3:]
            _dim = measure.find('DIMENSION').text
            fake_m = float(get_setting(config_name,_id,"fake_m"))
            fake_d = float(get_setting(config_name,_id,"fake_d"))
            _fake_val = round(normalvariate(fake_m, fake_d),2)
 
            measure_ids.append(_id)
            measure_vals.append(_val)
            measure_vals_filtered.append(measure_filter(_id, _val, max_vals))
            measure_vals_fake.append(_fake_val)
            measure_times.append(_timestamp)
 
# суммирование 41505 и 41506

        _id = "NOx"
        _val = str(float(measure_vals[measure_ids.index('41505')])+float(measure_vals[measure_ids.index('41506')]))
        _fake_val = str(round(float(measure_vals_fake[measure_ids.index('41505')])+float(measure_vals_fake[measure_ids.index('41506')]),2))

        measure_ids.append(_id)
        measure_vals.append(_val)
        measure_vals_filtered.append(measure_filter(_id, _val, max_vals))
        measure_vals_fake.append(_fake_val)
        measure_times.append(_timestamp)



        _data['measure']=list(zip(measure_ids, measure_vals,measure_times))
        _data['measure_filtered']= list(zip(measure_ids, measure_vals_filtered,measure_times))
        _data['measure_fake']= list(zip(measure_ids, measure_vals_fake,measure_times))
    
    except Exception as ex:
        logger.error('error with {}, details: {}'.format(filename,ex))
        try:
            shutil.move(filename,doc_path+"/error")
            logger.error('file {} moved to ERROR'.format(filename))
        except Exception as ex_mv:
            logger.error('problem with moving {}, details: {}'.format(filename, ex_mv))
 
#try send data to internal server
    if get_setting(config_name, "general", "send_real_internal")=="1":        
        try:
            send_data(_data, internal_server_ip, internal_port)
        except Exception as ex:
            logger.error('error with sending data internal server {}, details: {}'.format(filename,ex))

 
#try send realdata to external server
    if get_setting(config_name, "general", "send_real_external")=="1":        
        try:
            send_data(_data, external_server_ip, external_port)
        except Exception as ex:
            logger.error('error with sending real data external server {}, details: {}'.format(filename,ex))


#try send filtered_data to external server
    if get_setting(config_name, "general", "send_filtered_external")=="1":
        try:
            send_data(_data, external_server_ip, external_port, suffix='_f', array_name="measure_filtered")
        except Exception as ex:
            logger.error('error with sending filtered data external server {}, details: {}'.format(filename,ex))

#try send filtered_data to external server
    if get_setting(config_name, "general", "send_fake_external")=="1":
        try:
            send_data(_data, external_server_ip, external_port, suffix='_ff', array_name="measure_fake")
        except Exception as ex:
            logger.error('error with sending filtered data external server {}, details: {}'.format(filename,ex))


 #try move to done
    try:
        shutil.move(filename, doc_path+"/done")
        pass
    except Exception as ex_mv:
        logger.error('problem with moving {}, details: {}'.format(filename, ex_mv))
       
def send_data(data, server_ip, port, suffix='', array_name="measure"):
    g = graphitesend.init(graphite_server=server_ip, graphite_port=2003, prefix=prefix+suffix, timeout_in_seconds=10, )
    g.send_list(data[array_name])
    if data['alarm']!='':
        g.send('alarm', data['alarm'], data[array_name][0][2])
 
 
def main(argv):
    init()

    for filename in os.listdir(doc_path):
        if filename.endswith(".xml"):
            filename = os.path.join(doc_path, filename)
            process_file(filename)
 
if __name__ == "__main__":
    main(sys.argv)
