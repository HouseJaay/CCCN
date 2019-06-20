from pythonlsf import lsf
import os
import time


def run_job(command):
    """
    Run a job...
    """
    submitreq = lsf.submit()
    submitreq.command = command
    submitreq.options = 0
    submitreq.options2 = 0

    limits = []
    for i in range(0, lsf.LSF_RLIM_NLIMITS):
        limits.append(lsf.DEFAULT_RLIMIT)

    submitreq.rLimits = limits

    submitreq.beginTime = 0
    submitreq.termTime = 0
    submitreq.numProcessors = 1
    submitreq.maxNumProcessors = 1

    submitreply = lsf.submitReply()

    if lsf.lsb_init("test") > 0:
        exit(1)

    job_id = lsf.lsb_submit(submitreq, submitreply)
    return job_id


def do_sub(command, node, folder_lst, n_line):
    """
    submit a job for every folder
    :param command: command to run CCCN, without folder_lst
    :param node: number of nodes
    :param folder_lst: folder_lst of preparation.py
    :param n_line: folder quantity submitted by one job
    :return:
    """
    with open(folder_lst, 'r') as f:
        folders = f.readlines()
    for i in range(0, len(folders), n_line):
        folder = folders[i: i+n_line]
        name = folder[0].strip()
        print("now submitting folder %s" % name)
        sub_lst = os.path.basename(name.split()[0]) + '.lst'
        with open(sub_lst, 'w') as f:
            f.write(''.join(folder))
        run_job(command + ' ' + sub_lst)
        count = lsf.lsb_openjobinfo(0, None, 'goxu', None, None, 0)
        while count > node:
            time.sleep(10)
            count = lsf.lsb_openjobinfo(0, None, 'goxu', None, None, 0)


if __name__ == '__main__':
    # command = "python ~/hao_shijie/program/CCCN/Scripts/bin/preparation.py " +\
    #           "-f0.1/0.2/16/19 -d0.02 -thinet -c1000/80000 -l20"
    with open('run_cccn', 'r') as f:
        command = f.read().strip()
    do_sub(command, 18, 'folder.lst', 2)
