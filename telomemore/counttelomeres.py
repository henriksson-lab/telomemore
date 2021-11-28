from telomemore.utils import BaseKmerFinder
from typing import Tuple
from collections import Counter, defaultdict
import pysam
from pathlib import Path
import pandas as pd

class CountTelomeres(BaseKmerFinder):
    '''Counts number of telomeres in all bam files in the input folder'''

    def __init__(self, input_folder: str, pattern: str, output_folder: str, cutoff: int, threads: int = 1):
        super().__init__(input_folder, pattern, output_folder, threads)
        self.cutoff = cutoff
        

    def _telomere_counts(self, sam: pysam.AlignmentFile) -> Tuple[dict, dict, int]:
        '''Counts number of telomeres and returns the total reads per cells, telomeres per cells and reads with missed barcodes.'''
        telomeres_cells = defaultdict(int)
        total_reads_cells = defaultdict(int)
        missed_barcodes = 0
    
        for read in sam:
            try:
                total_reads_cells[read.get_tag('CB')] += 1 
                # adds the key to the dict and initializes it to 0 
                telomeres_cells[read.get_tag('CB')]
                if self._number_telomers(read.seq) >= self.cutoff:
                    telomeres_cells[read.get_tag('CB')] += 1
            except Exception:
                missed_barcodes += 1

        return telomeres_cells, total_reads_cells, missed_barcodes
        
    
    def _run_program(self, file: Path) -> None:
        '''Generates teleomere counts for each bam file in the input folder. Writes the results as csv files.'''
        
        # part[-3] is the name of the folder which contains the out folder and the possorted.bam file 
        telomere_file = self.out_folder / f'{file.parts[-3]}_telomeres_{self.pattern.pattern}.csv'
        totalreads_file = self.out_folder / f'{file.parts[-3]}_total_reads.csv'
        missed_barcods_file = self.out_folder / f'{file.parts[-3]}_missed_barcodes.txt'

        sam = pysam.AlignmentFile(file, 'rb')

        telomeres_dict, total_dict, missed_barcodes = self._telomere_counts(sam)

        with open(telomere_file, 'a+') as telomere:
            for key, value in telomeres_dict.items():
                print(f'{key},{value}', file=telomere)

        with open(totalreads_file, 'a+') as total:
            for key, value in total_dict.items():
                print(f'{key},{value}', file=total)

        with open(missed_barcods_file, 'w+') as missed:
            print(f'Number of missed barcodes = {missed_barcodes}', file=missed)
            




