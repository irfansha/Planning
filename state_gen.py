# Irfansha Shaik, 30.09.2020, Aarhus

class StateGen():

  def __init__(self, vd, num_state_vars, k):
    self.states = []
    for i in range(k+1):
      self.states.append(vd.get_vars(num_state_vars))
