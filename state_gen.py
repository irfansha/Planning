# Irfansha Shaik, 30.09.2020, Aarhus

class StateGen():

  def __init__(self, vd, k):
    self.states = []
    for i in range(k):
      self.states.append(vd.get_vars(k))
