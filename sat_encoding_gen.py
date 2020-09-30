# Irfansha Shaik, 30.09.2020, Aarhus

from variable_dispatcher import VarDispatcher as vd
from state_gen import StateGen as sg

class SatEncoding():

  def __init__(self, constraints_extract, tfun, k):
    var_dis = vd()
    # generating k states:
    states_gen = sg(var_dis, k)
