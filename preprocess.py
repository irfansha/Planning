import subprocess

def preprocess(args):
      command = './tools/qbfrelay/qbfrelay.sh -t=' + str(args.preprocessing_time_limit) + " -c -o " + args.preprocess_order + " -p " + args.preprocessed_encoding_out + " " + args.encoding_out
      try:
        plan_status = subprocess.run(command,check =True, shell=True)
      except subprocess.CalledProcessError as e:
        return 0
      return 1