# Irfansha Shaik, 01.10.2020, Aarhus.

import os

class Quabs():

  def run(self):
    command = self.solver_path + " --partial-assignment " + self.input_file_path + " > " + self.output_file_path
    os.system(command)


  def __init__(self, input_file_path, output_file_path, solver_path):
    self.input_file_path = input_file_path
    self.output_file_path = output_file_path
    self.solver_path = solver_path
