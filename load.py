from pymongo import MongoClient
import os, sys
from cmtk import collection, tempfolder, active, run_stage


def query_yes_no(question, default="yes"):
    """Ask a yes/no question via raw_input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
        It must be "yes" (the default), "no" or None (meaning
        an answer is required of the user).

    The "answer" return value is one of "yes" or "no".
    """
    valid = {"yes":True,   "y":True,  "ye":True,
             "no":False,     "n":False}
    if default == None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = raw_input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' "\
                             "(or 'y' or 'n').\n")

def loadDir(dir, overwrite=False):
  if os.path.isdir(dir):
    for file in os.listdir(dir):
      loadFile(file, overwrite)

def loadFile(file, overwrite=False):
  if os.path.exists(file) and ('.tif' in file or '.lsm' in file):
    if collection.find({'name': os.path.splitext(os.path.basename(file))[0]}).count() < 1 or overwrite:
      collection.insert({'name': os.path.splitext(os.path.basename(file))[0], 'original_ext': os.path.splitext(os.path.basename(file))[1], 'original_path': dir})
    else:
      print collection.find_one({'name': os.path.splitext(os.path.basename(file))[0]})
      if query_yes_no("Image already exists in processing stack do you want to update original file details?"):
        collection.update({'name': os.path.splitext(os.path.basename(file))[0]},{'name': os.path.splitext(os.path.basename(file))[0], 'alignment_stage': 1, 'original_ext': os.path.splitext(os.path.basename(file))[1], 'original_path': dir})

if __name__ == "__main__":
  if active and '1' in run_stage:
    loadDir(os.getcwd())
    print 'done'
  else:
    print 'inactive or stage 1 not selected'
