# from pymongo import MongoClient
import os, sys
from cmtk import tempfolder, active, run_stage, host, templatedir, cur, comp_orien, ori, orien


def query_orientation(question, default='LPS'):
    """Ask a question via raw_input() and return an orientation string.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
        It must be an valid orientation (the default) or None (meaning
        an answer is required of the user).

    The "answer" return value is a string.
    """
    prompt = 'Shorthand: ' + str(ori) + ' or in full: \n' + str(orien)
    valid = ori + orien
    if not default == None:
      prompt = prompt + ' default=' + str(default)
    while True:
        sys.stdout.write(question + '\n' + prompt + '\n')
        choice = raw_input()
        if default is not None and choice == '':
            if default in valid:
              if len(default) > 3:
                return str(default)
              else:
                return comp_orien[default]
        elif choice in valid:
            if len(choice) > 3:
              return str(choice)
            else:
              return comp_orien[choice]
        else:
            sys.stdout.write("Please respond with a valid oriention (case sensitive) " + "\n" + prompt)

def query_settings(question, default=1):
    """Ask a question via raw_input() and return an int.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
        It must be an int number (the default) or None (meaning
        an answer is required of the user).

    The "answer" return value is an int.
    """
    cur.execute('SELECT id, name FROM system_setting')
    records = cur.fetchall()
    ids = []
    for record in records:
      print str(record[0]) + ' - ' + str(record[1])
      ids.append(int(record[0]))
    valid = ids
    prompt = str(ids)
    if not default == None:
      prompt = prompt + ' default=' + str(default)

    while True:
        sys.stdout.write(question + '\n' + prompt + '\n')
        choice = raw_input()
        if default is not None and choice == '':
            if default in valid:
              return int(default)
        elif choice in valid:
            return int(choice)
        else:
            sys.stdout.write("Please respond with the number of the reqired settings " + str(ids) + "\n")

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

def loadDir(folder, settings_id=1, orientation=comp_orien['LPS'], overwrite=False):
  if os.path.isdir(folder):
    for file in os.listdir(folder):
      if loadFile(file, folder, settings_id, orientation, overwrite):
        print file + " - loaded OK"
      else:
        print file + " - failed to load"

def loadFile(file, folder, settings_id=1, orientation=comp_orien['LPS'], overwrite=False):
  r=0
  if os.path.exists(file) and ('.tif' in file or '.lsm' in file):
    name = str(os.path.splitext(os.path.basename(file))[0])
    cur.execute("SELECT count(*) FROM images_alignment WHERE name like %s", [name])
    r = int(cur.fetchone()[0])
    if r < 1:
      cur.execute("INSERT INTO images_alignment (settings_id, name, max_stage, alignment_stage, last_host, loading_host, original_ext, original_path, orig_orientation) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)", [str(settings_id), name, str(1), str(1), host, host, str(os.path.splitext(os.path.basename(file))[1]), str(folder), orientation])
      cur.connection.commit()
    else:
      cur.execute("SELECT * FROM images_alignment WHERE name like '" + str(os.path.splitext(os.path.basename(file))[0]) + "'")
      print cur.fetchone()
      if overwrite:
        cur.execute("UPDATE images_alignment SET orig_orientation = %s, settings_id = %s, max_stage = 1, alignment_stage = 1, last_host = %s, loading_host = %s, original_ext = %s, original_path = %s WHERE name = %s", [orientation, str(settings_id), host, host, str(os.path.splitext(os.path.basename(file))[1]), str(folder), name])
        cur.connection.commit()
      else:
        if query_yes_no("Image already exists in processing stack do you want to update original file details?"):
          cur.execute("UPDATE images_alignment SET orig_orientation = %s, settings_id = %s, max_stage = 1, alignment_stage = 1, last_host = %s, loading_host = %s, original_ext = %s, original_path = %s WHERE name = %s", [orientation, str(settings_id), host, host, str(os.path.splitext(os.path.basename(file))[1]), str(folder), name])
          cur.connection.commit()
    cur.execute("SELECT count(*) FROM images_alignment WHERE name like %s", [name])
    r = int(cur.fetchone()[0])
  if r > 0:
    return True
  else:
    return False

if __name__ == "__main__":
  if active and '1' in run_stage:
    ans = query_settings('Which settings do you want to use?', default=1)
    O = query_orientation('Which orientation do you want to use?', default='LPS')
    loadDir(os.getcwd(), settings_id=ans, orientation=O)
    print 'done'
  else:
    print 'inactive or stage 1 not selected'
