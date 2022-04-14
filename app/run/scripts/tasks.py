import subprocess as sp

from collections import OrderedDict, defaultdict, Counter
import logging
import glob
import os

logger = logging.getLogger(__name__)


def run_pipe(command, id_path, shell_bo=False, start_msg="Starting nextflow pipeline...",
             stop_msg="Pipeline finished successfully!", silent=False, m_env=os.environ.copy()):
    print(start_msg)
    print("PATH: ", m_env["PATH"])
    process = sp.run(command,
                     stdout=sp.PIPE,
                     stderr=sp.PIPE,
                     shell=shell_bo,
                     universal_newlines=True,
                     env=m_env,
                     cwd=id_path
                     )
    if process.returncode == 0:
        if not silent:
            print("print:", process.stdout)
        logger.debug(process.stdout)
        logger.debug(process.stderr)
        print(stop_msg)
        return process.returncode
    else:
        if not silent:
            print("stdout:", process.stdout)
        print("stderr:", process.stderr)
        logger.debug(process.stdout)
        logger.debug(process.stderr)
        logger.error("Pipeline finished with error code:{0}".format(str(process.returncode)))
        return process.returncode


def get_memory():
    with open('/proc/meminfo', 'r') as mem:
        free_memory = 0
        max_memory = 0
        for i in mem:
            sline = i.split()
            if str(sline[0]) in ('MemFree:', 'Buffers:', 'Cached:'):
                free_memory += int(sline[1])
            elif str(sline[0]) == 'MemTotal:':
                max_memory = int(sline[1])
    free_memory = (free_memory / 1e+6) / 2
    max_memory = max_memory / 1e+6
    if free_memory > max_memory / 4:
        free_memory = max_memory / 4
    return int(free_memory)


def get_cpus():
    from multiprocessing import cpu_count
    return int(cpu_count() / cpu_count())


# Create a logger
logging.basicConfig(format='%(name)s - %(asctime)s %(levelname)s: %(message)s')
tx2logger = logging.getLogger(__file__)
tx2logger.setLevel(logging.INFO)


def read_top_transcript(salmon):
    txs = set()
    fn = glob.glob(os.path.join(salmon, "*", "quant.sf"))[0]
    with open(fn) as inh:
        for line in inh:
            if line.startswith("Name"):
                continue
            txs.add(line.split()[0])
            if len(txs) > 100:
                break
    tx2logger.info("Transcripts found in FASTA: %s" % txs)
    return txs


def tx2gene(gtf, salmon, gene_id, extra, out):
    txs = read_top_transcript(salmon)
    votes = Counter()
    gene_dict = defaultdict(list)
    with open(gtf) as inh:
        for line in inh:
            gene_id_value = ''
            if line.startswith("#"):
                continue
            cols = line.split("\t")
            attr_dict = OrderedDict()
            for gff_item in cols[8].split(";"):
                item_pair = gff_item.strip().split(" ")
                if len(item_pair) > 1:
                    value = item_pair[1].strip().replace("\"", "")
                    if value in txs:
                        votes[item_pair[0].strip()] += 1

                    attr_dict[item_pair[0].strip()] = value
                if item_pair[0] == gene_id:
                    gene_id_value = item_pair[1].strip()
            gene_dict[gene_id_value].append(attr_dict)

    if not votes:
        tx2logger.warning("No attribute in GTF matching transcripts")
        return None

    txid = votes.most_common(1)[0][0]
    tx2logger.info("Attributed found to be transcript: %s" % txid)
    seen = set()
    with open(out, 'w') as outh:
        for gene in gene_dict:
            for row in gene_dict[gene]:
                if txid not in row:
                    continue
                if (gene, row[txid]) not in seen:
                    seen.add((gene, row[txid]))
                    if not extra in row:
                        extra_id = gene
                    else:
                        extra_id = row[extra]
                    print("%s,%s,%s" % (row[txid], gene, extra_id), file=outh)

# def del_file(filelist, id_path='.'):
#     for filename in os.listdir('.'):
#         if filename in filelist:
#             if os.path.isdir(filename):
#                 print("removing %s" % (filename,))
#                 shutil.rmtree(filename)
#             else:
#                 print("removing %s" % (filename,))
#                 os.remove(filename)

def del_file(filelist, id_path='.'):
    for filename in os.listdir('.'):
        if filename in filelist:
            if os.path.isdir(filename):
                print("removing %s" % (filename,))
                shutil.rmtree(filename)
            else:
                print("removing %s" % (filename,))
                os.remove(filename)

