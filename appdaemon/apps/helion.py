'''
Listens to the state changes of three buttons on Home Assistant dashboard and calls corresponding scripts.
You need to change the absolute paths to where helion scripts is located on your machine in apps.yaml (param1).

'''

import hassapi as hass
import os

class RunHelion(hass.Hass):

  def initialize(self):
     self.set_state("input_boolean.run_helion", state="off")
     self.set_state("input_boolean.change_states", state="off")
     self.set_state("input_boolean.text_file", state="off")
     self.listen_state(self.helion, "input_boolean.run_helion", new = "on")
     self.listen_state(self.states, "input_boolean.change_states", new="on")
     self.listen_state(self.text, "input_boolean.text_file", new="on")
     self.log("Hello from AppDaemon")
     self.log("You are now ready to run Apps!")

  def helion(self, entity, attribute, old, new, kwargs):
     self.set_state("input_boolean.run_helion", state="off")
     os.chdir(self.args["param1"])
     os.system("python3 helion_predictions.py ../data/generated_data/validation/scenarios_from_evaluators/ha-scenarios.txt  ../data/generated_data/training/training_model/helion.train -o 3 -v ../data/generated_data/training/training_model/helion.vocab")

  def states(self, entity, attribute, old, new, kwargs):
     self.set_state("input_boolean.change_states", state="off")
     os.chdir(self.args["param1"])
     os.system("python3 change_state.py")

  def text(self, entity, attribute, old, new, kwargs):
     self.set_state("input_boolean.text_file", state="off")
     os.chdir(self.args["param1"])
     os.system("python3 write_to_text_file.py \<null,time,night\> \<Door_Lock,lock,unlocked\> \<Motion_Sensor,motion,detected\> \<Water_Heater,switch,on\>")
