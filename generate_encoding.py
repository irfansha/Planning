# Irfansha Shaik, 30.10.2020, Aarhus.

from transition_gen import TransitionFunction as tfl
from transition_gen_withoutamoalo import TransitionFunction as tfb
from ungrounded_transition_gen import UngroundedTransitionFunction as utf
from ungrounded_transition_gen_plus import UngroundedTransitionFunctionPlus as utfp
from sat_encoding_gen import SatEncoding as se
from qr_encoding_gen import QREncoding as qr
from qbf_intermediate_encoding import QIEncoding as qi
from ctencoding import CTEncoding as cte
from flat_encoding import FlatEncoding as fe
from ungrounded_encoding import UngroundedEncoding as ue
from ungrounded_encoding_plus import UngroundedEncodingPlus as uep
import os


class EncodingGen():

  def __init__(self, constraints_extract, args):
    if (args.e == 'M-seq'):
      os.system('./tools/M -P 0 -O -F ' + str(args.k) + ' -T ' + str(args.k) + " -b " + args.encoding_out + " " + args.d + " " + args.p)
      # renaming the encoding file, due to madagascar encoding naming scheme:
      padded_k = str(args.k).zfill(3)
      os.rename(args.encoding_out + "." + padded_k + ".cnf", args.encoding_out)
      return
    # Generating transition function:
    if (args.e == 'UE'):
      tfun = utf(constraints_extract, args.splitvars)
    elif (args.e == 'UE+'):
      tfun = utfp(constraints_extract, args.splitvars)
    else:
      if (args.t == 'l'):
        tfun = tfl(constraints_extract)
      elif (args.t == 'b'):
        tfun = tfb(constraints_extract)


    if (args.e == 'SAT'):
      self.encoding = se(constraints_extract, tfun, args.k)
    elif (args.e == 'RE2'):
      self.encoding = qr(constraints_extract, tfun, args.k)
    elif (args.e == 'RE1'):
      self.encoding = qi(constraints_extract, tfun, args.k, args.forall_pruning)
    elif (args.e == 'UE'):
      self.encoding = ue(constraints_extract, tfun, args.k, args.splitvars, args.parameters_overlap)
    elif (args.e == 'UE+'):
      self.encoding = uep(constraints_extract, tfun, args.k, args.splitvars, args.parameters_overlap, args.parameters_fold, args.fold_num)
    elif (args.e == 'CTE'):
      if (args.run == 2):
        self.encoding = cte(constraints_extract, tfun, args.k, 1)
      else:
        self.encoding = cte(constraints_extract, tfun, args.k, 0)
    elif (args.e == 'FE'):
      if (args.run == 2):
        self.encoding = fe(constraints_extract, tfun, args.k, 1)
      else:
        self.encoding = fe(constraints_extract, tfun, args.k, 0)
    else:
      print('no encoding generated')
      exit()

    if (args.encoding_type == 1):
      self.encoding.print_encoding_tofile(args.encoding_out)
      if (args.verbosity_level != 0):
        print("QCIR Encoding generated")

    if (args.encoding_type == 2):
      temp_file_path = args.encoding_intermediate_out
      self.encoding.print_encoding_tofile(temp_file_path)
      if (args.verbosity_level != 0):
        print("Intermediate QCIR Encoding generated")
      os.system('./tools/qcir2qdimacs ' + temp_file_path + ' > ' + args.encoding_out)
      if (args.verbosity_level != 0):
        print("QDIMACS Encoding generated")
