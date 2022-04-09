# bids-phenotype

A utility repository for BIDS phenotypic data conversion, aggregation, and segregation.

## `python phenotype.py -h`

```shell
usage: phenotype.py [-h] {convert,segregate,aggregate} ...

BIDS phenotype data utility

positional arguments:
  {convert,segregate,aggregate}
                        Modes
    convert             Convert CSV or Excel files to BIDS TSV files
    segregate           Segregate phenotype files from the top of the tree
    aggregate           Aggregate phenotype files to the top of the tree

optional arguments:
  -h, --help            show this help message and exit
```

## UNTESTED `python phenotype.py convert -h` UNTESTED

```shell
usage: phenotype.py convert [-h] -i INDIR -o OUTDIR

optional arguments:
  -h, --help            show this help message and exit
  -i INDIR, --input-dir INDIR
                        Input directory of CSVs and/or Excel files.
  -o OUTDIR, --output-dir OUTDIR
                        Output directory to write converted files which can be the same as the input directory
```

## `python phenotype.py segregate -h`

```shell
usage: phenotype.py segregate [-h] -i INDIR -o OUTDIR {subject,session}

positional arguments:
  {subject,session}     Segregate to either the subject or session level

optional arguments:
  -h, --help            show this help message and exit
  -i INDIR, --input-dir INDIR
                        Input BIDS top-level/root directory containing the phenotype folder
  -o OUTDIR, --output-dir OUTDIR
                        Output directory to write segregated files which can be the same as the input directory
```

## `python phenotype.py aggregate -h`

```shell
usage: phenotype.py aggregate [-h] -i INDIR -o OUTDIR {subject,session}

positional arguments:
  {subject,session}     Aggregate from either the subject or session level

optional arguments:
  -h, --help            show this help message and exit
  -i INDIR, --input-dir INDIR
                        Input BIDS top-level/root directory containing the subject/session segregated phenotype folders
  -o OUTDIR, --output-dir OUTDIR
                        Output directory to write aggregated files which can be the same as the input directory
```
