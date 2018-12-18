import os
import random
import sys
import configparser


# 41526 - Кислород        30
# 41506 - Двуокись азота  1-200       max 200
# 41509 - Двуокись серы   2-250       max 50
# 41504 - Хлороводород    0.2 - 30    max 10
# 41512 - Угарный газ     2 - 200     max 50
# 41505 - Окись азота     3 - 300     max 200


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

    config.add_section("network")
    config.set("network", "internal_server_ip", "192.168.0.250")
    config.set("network", "internal_port", "2003")
    config.set("network", "external_server_ip", "23.20.213.83")
    config.set("network", "external_port", "2003")

    config.add_section("general")
    config.set("general", "doc_path", "xmls")
    config.set("general", "send_internal", "1")
    config.set("general", "send_external", "1")
    config.set("general", "send_filtered_external", "1")
    config.set("general", "prefix", "device_11")

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


config_name="config.cfg"

internal_ip = get_setting(config_name, "network", "internal_server_ip")

sections = ("41526", "41506", "41509", "41504", "41505", "41512")
max_vals={}
for x in sections:
    max_vals[x]=get_setting(config_name,x,"max")

print(max_vals)

for x in range(100):
    print(random.normalvariate(17,1))

def main(argv):
    for x in argv:
        print(x)

if __name__ == "__main__":
    main(sys.argv)