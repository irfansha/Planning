# Irfansha Shaik, 30.09.2020, Aarhus

class VarDispatcher():


  def get_vars(self, n):
    var_list = list(range(self.next_var, self.next_var+n))
    self.next_var = self.next_var+n
    return var_list

  def set_next_var(self, n):
    self.next_var = n

  def __init__(self):
    self.next_var = 1
