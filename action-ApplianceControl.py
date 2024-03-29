#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import configparser
from hermes_python.hermes import Hermes
from hermes_python.ffi.utils import MqttOptions
from hermes_python.ontology import *
import io

CONFIGURATION_ENCODING_FORMAT = "utf-8"
CONFIG_INI = "config.ini"

class SnipsConfigParser(configparser.SafeConfigParser):
    def to_dict(self):
        return {section : {option_name : option for option_name, option in self.items(section)} for section in self.sections()}


def read_configuration_file(configuration_file):
    try:
        with io.open(configuration_file, encoding=CONFIGURATION_ENCODING_FORMAT) as f:
            conf_parser = SnipsConfigParser()
            conf_parser.readfp(f)
            return conf_parser.to_dict()
    except (IOError, configparser.Error) as e:
        return dict()

def subscribe_intent_callback(hermes, intentMessage):
    conf = read_configuration_file(CONFIG_INI)
    action_wrapper(hermes, intentMessage, conf)


def action_wrapper(hermes, intentMessage, conf):
    if len(intentMessage.slots.Appliance) > 0:
        appliance = intentMessage.slots.Appliance.first().value
        if len(intentMessage.slots.SwitchState) > 0:
            switchStat = intentMessage.slots.SwitchState.first().value
            result_sentence = "Ok, turning {} {}.".format(str(switchStat),str(appliance))  # The response that will be said out loud by the TTS engine.
            hermes.publish_end_session( intentMessage.session_id, result_sentence)
        else:
            result_sentence = "Sorry, I could not follow."
            hermes.publish_end_session( intentMessage.session_id, result_sentence)
    else:
        hermes.publish_end_session(intentMessage.session_id, "Something is wrong! Please speak again.")
        
        
if __name__ == "__main__":
    #mqtt_opts = MqttOptions()
    with Hermes("localhost:1883") as h:
        h.subscribe_intent("TamojitSaha:ApplianceControl", subscribe_intent_callback) \
         .start()
