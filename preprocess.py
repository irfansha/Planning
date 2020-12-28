import os

def run_bloqqer(args):
      command = './tools/bloqqer/bloqqer --verbose=1 --timeout=' + str(args.preprocessing_time_limit) + " " +args.encoding_out + ' ' + args.preprocessed_encoding_out
      plan_status = os.popen(command).read()
      stats = plan_status.split("\nc [bloqqer] ")
      if "total time" not in stats[-1]:
          return 0
      for line in stats:
        if ("seconds" in line and 'MB' in line):
          temp_stats = line.split(" ")
          print("Preprocessing time: " + str(temp_stats[0]) + ' seconds')
          print("Preprocessing memory: " + str(temp_stats[2]) + ' MB')
      return 1



def preprocess(args):
    if (args.preprocessing == 1):
        return (run_bloqqer(args))
    else:
        print("Work in progress for other preprocessors.")
        return 0