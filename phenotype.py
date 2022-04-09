import argparse
from glob import glob
import os
from posixpath import basename
import pandas
import re

def existent(path):
    if not os.path.exists(path):
        raise argparse.ArgumentTypeError(f"{path} does not exist")
    return path

def readable(path):
    if not os.access(path, os.R_OK):
        raise argparse.ArgumentTypeError(f"{path} is not readable")
    return path

def writeable(path):
    if not os.access(path, os.W_OK):
        raise argparse.ArgumentTypeError(f"{path} is not writeable")
    return path

def executable(path):
    if not os.access(path, os.X_OK):
        raise argparse.ArgumentTypeError(f"{path} is not executable")
    return path

def available(path):
    parent = os.path.dirname(os.path.abspath(path))
    if not (os.path.exists(parent) and os.access(parent, os.W_OK)):
        raise argparse.ArgumentTypeError(f"""{path} is either not writeable or 
                                          the parent directory does not exist""")

    if os.path.exists(path):
        path = writeable(path)

    return path

# convert words and strings to exclusively alphanumerics for BIDS' sake
def bidsify(input_name):
    return re.sub(r'[\W_]+', '', input_name)

def csv2tsv(in_csv_file, out_tsv_file):
    dataframe = pandas.read_csv(in_csv_file, sep=',')
    dataframe.to_csv(out_tsv_file, sep='\t')

def excel2tsv(in_excel_file, out_tsv_file):
    dataframe = pandas.read_excel(in_excel_file)
    dataframe.to_csv(out_tsv_file, sep='\t')

def convert2tsv(args):
    convertables = []
    all_files = glob(os.path.join(os.path.abspath(args.input), '*.*'))
    for file in all_files:
        if file.lower().endswith(['.csv',
                                  '.xls',
                                  '.xlsx',
                                  '.xlsm',
                                  '.xlsb',
                                  '.odf',
                                  '.ods',
                                  '.odt']):
            convertables.append(file)

    output = os.path.abspath(args.output)

    for file in convertables:
        old_basename = os.path.basename(file)
        extension = os.path.splitext(old_basename)[1]
        new_basename = bidsify(old_basename.rstrip(extension) + '.tsv')
        out_tsv = available(os.path.join(output, new_basename))

        if file.lower().endswith('.csv'):
            csv2tsv(file, out_tsv)
        else:
            excel2tsv(file, out_tsv)

    # check for single column header
    # check for participant_id column

def segregate(args):
    top_files = glob(os.path.join(os.path.abspath(args.input), 'phenotype', '*.tsv'))
    output = os.path.abspath(args.output)

    for file in top_files:
        basename = os.path.basename(file)
        df = pandas.read_csv(file, sep='\t')
        participants = df['participant_id'].unique()

        # check whether segregation level is subject or session
        if args.level == 'subject':
            # phenotype file crawl
            for participant in participants:
                participant_df = df[df['participant_id'] == participant]

                output_subdir = os.path.join(output, participant, 'phenotype')
                if not os.path.exists(output_subdir):
                    os.makedirs(output_subdir, exist_ok=True)

                participant_file = os.path.join(output_subdir, basename)
                if not os.path.exists(participant_file):
                    participant_df.to_csv(participant_file, sep='\t', index=False)
                else:
                    print(f"{participant_file} already exists")

        elif args.level == 'session':
            # warning about session_id column
            if 'session_id' not in df.columns:
                print(f"session_id not in {file} columns. Skipping.")
                continue

            for participant in participants:
                participant_df = df[df['participant_id'] == participant]
                sessions = participant_df['session_id'].unique()

                for session in sessions:
                    session_df = participant_df[participant_df['session_id'] == session]
                    output_subdir = os.path.join(output, participant, session, 'phenotype')
                    if not os.path.exists(output_subdir):
                        os.makedirs(output_subdir, exist_ok=True)

                    session_file = os.path.join(output_subdir, basename)
                    if not os.path.exists(session_file):
                        session_df.to_csv(session_file, sep='\t', index=False)
                    else:
                        print(f"{session_file} already exists")


def aggregate(args):
    phenotypes = {}
    input  = os.path.abspath(args.input)
    output = os.path.abspath(args.output)
    participant_files = glob(os.path.join(input, 'sub-*', 'phenotype', '*.tsv'))
    session_files = glob(os.path.join(input, 'sub-*', 'ses-*', 'phenotype', '*.tsv'))

    # check whether segregation level is subject or session
    if args.level == 'subject':
        files = participant_files
    elif args.level == 'session':
        files = session_files

    for file in files:
        basename = os.path.basename(file)
        target = os.path.join(output, 'phenotype', basename)

        if target not in phenotypes:
            phenotypes[target] = [file]
        else:
            phenotypes[target].append(file)

    for target, files in phenotypes.items():
        if len(files) == 1:
            shutil.copy(files[0], target)
        else:
            dfs = [pandas.read_csv(file, sep='\t') for file in files]
            df = pandas.concat(dfs, ignore_index=True)
            df.to_csv(target, sep='\t', index=False)

def cli():
    description = """
                  BIDS phenotype data utility
                  """

    parser = argparse.ArgumentParser(description=description)
    subparsers = parser.add_subparsers(help='Modes')

    parser_convert = subparsers.add_parser(
        'convert', help='Convert CSV or Excel files to BIDS TSV files'
        )
    parser_convert.add_argument('-i', '--input-dir', metavar='INDIR',
        type=readable, dest='input', required=True,
        help="""
            Input directory of CSVs and/or Excel files.
            """)
    parser_convert.add_argument('-o', '--output-dir', metavar='OUTDIR',
        type=available, dest='output', required=True,
        help="""
            Output directory to write converted files which
            can be the same as the input directory
            """)
    parser_convert.set_defaults(func=convert2tsv)

    parser_segregate = subparsers.add_parser(
        'segregate', help='Segregate phenotype files from the top of the tree'
        )
    parser_segregate.add_argument('-i', '--input-dir', metavar='INDIR',
        type=readable, dest='input', required=True,
        help="""
            Input BIDS top-level/root directory containing the phenotype folder
            """)
    parser_segregate.add_argument('-o', '--output-dir', metavar='OUTDIR',
        type=available, dest='output', required=True,
        help="""
            Output directory to write segregated files which
            can be the same as the input directory
            """)
    parser_segregate.add_argument(choices=['subject', 'session'],
        type=str, dest='level', 
        help="""
            Segregate to either the subject or session level
            """)
    parser_segregate.set_defaults(func=segregate)

    parser_aggregate = subparsers.add_parser(
        'aggregate', help='Aggregate phenotype files to the top of the tree'
        )
    parser_aggregate.add_argument('-i', '--input-dir', metavar='INDIR',
        type=readable, dest='input', required=True,
        help="""
            Input BIDS top-level/root directory containing the subject/session
            segregated phenotype folders
            """)
    parser_aggregate.add_argument('-o', '--output-dir', metavar='OUTDIR',
        type=available, dest='output', required=True,
        help="""
            Output directory to write aggregated files which
            can be the same as the input directory
            """)
    parser_aggregate.add_argument(choices=['subject', 'session'],
        type=str, dest='level',
        help="""
            Aggregate from either the subject or session level
            """)
    parser_aggregate.set_defaults(func=aggregate)

    args = parser.parse_args()
    args.func(args)

cli()
