import os

def run_bloqqer(args):
      command = './tools/bloqqer/bloqqer --verbose=1 ' + args.encoding_out + ' ' + args.preprocessed_encoding_out
      plan_status = os.popen(command).read()
      stats = plan_status.split("\nc [bloqqer] ")
      for line in stats:
        if ("seconds" in line and 'MB' in line):
          temp_stats = line.split(" ")
          print("Preprocessing time: " + str(temp_stats[0]) + ' seconds')
          print("Preprocessing memory: " + str(temp_stats[2]) + ' MB')



def preprocess(args):
    if (args.preprocessing == 1):
        run_bloqqer(args)
    else:
        print("Work in progress for other preprocessors.")