##
## Utilities for running scripts on cluster
##
import os
import time
from settings import Settings, load_settings

def write_cluster_preface(file_handle):
    module_preface = \
"""
module add python/2.6.4;
module add numpy;		   
module add scipy;
module add matplotlib;
module add pygsl;
module add simplejson;\n
"""
    file_handle.write(module_preface)

def chunk_list(seq, num):
  avg = len(seq) / float(num)
  out = []
  last = 0.0
  while last < len(seq):
    out.append(seq[int(last):int(last + avg)])
    last += avg
  return out


def make_bash_script(filename, cmd, crate_dir=None):
    """
    Make an executable bash script out of the given command.
    """
#    os.system('ls %s' %(filename))
    if crate_dir == None:
        crate_dir = os.path.dirname(os.path.abspath(os.path.expanduser(__file__)))
    f = open(filename, 'w')
    f.write("#!/bin/bash\n")
    f.write("export PATH=$PATH:%s\n" %(crate_dir))
    f.write("source ~/.bash_profile\n")
    f.write("cd %s\n" %(crate_dir))
    #write_cluster_preface(f)
    f.write(cmd + "\n")
    f.close()
    os.system('chmod +x \"%s\"' %(filename))

    
def valid_qsub_name(name):
    """
    Return valid qsub ID by removing semicolons, converting
    them into underscores.
    """
    name = name.replace(';', '_')
    return name


def run_on_cluster(cmd, job_name, cluster_output_dir, cluster_scripts_dir=None,
                   queue_type=None, cmd_name="qsub", settings=None):
    print "Submitting job: %s" %(job_name)
    queue_name = None

    # Load command name from settings file
    if settings != None:
        load_settings(settings)
        cmd_name = Settings.get_cluster_command()

    if queue_type == "long":
        queue_name = Settings.get_long_queue_name()
    elif queue_type == "short":
        queue_name = Settings.get_short_queue_name()
    else:
        print "Warning: Unknown queue type: %s" %(queue_type)
        queue_name = queue_type
    

    if queue_type == None:
        print "  - queue: unspecified"
    else:
        print "  - queue: %s, using queue name %s" %(queue_type,
                                                     queue_name)

    #print "  - cmd: %s" %(cmd)
    if cluster_scripts_dir == None:
	cluster_scripts_dir = os.path.join(cluster_output_dir, 'cluster_scripts')
	if not os.path.isdir(cluster_scripts_dir):
	    os.mkdir(cluster_scripts_dir)
    scripts_output_dir = os.path.join(cluster_output_dir, 'scripts_output')
    if not os.path.isdir(scripts_output_dir):
	os.mkdir(scripts_output_dir)
    scripts_output_dir = os.path.abspath(scripts_output_dir)
    #qsub_call = 'qsub -V -q \"%s\" -o \"%s\" -e \"%s\"' %(queue_type, scripts_output_dir, scripts_output_dir)
    qsub_call = '%s -o \"%s\" -e \"%s\"' %(cmd_name, scripts_output_dir,
                                           scripts_output_dir)

    # Add queue type if given one
    if queue_name != None:
        qsub_call += ' -q \"%s\"' %(queue_name)
        
    script_name = valid_qsub_name(os.path.join(cluster_scripts_dir,
                                               '%s_time_%s.sh' %(job_name,
                                                                 time.strftime("%m-%d-%y_%H:%M:%S"))))
    make_bash_script(script_name, cmd)
    qsub_cmd = qsub_call + ' \"%s\"' %(script_name)
    os.system(qsub_cmd)
