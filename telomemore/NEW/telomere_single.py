from typing import Tuple
import pysam
from pathlib import Path
import pandas as pd
from collections import defaultdict
import re

class CountTelomeresSingleFile:
    '''Counts number of telomeres in bam file. User can specify a already defined file of cell barcodes. 
    If not, the program counts all cell barcodes in the bam file from cellranger.'''

    def __init__(self, input_bam: str, pattern: str, barcodes_file: str = False, cutoff: int = 3):
        self.cutoff = cutoff
        self.input_bam = Path(input_bam)
        self.pattern = re.compile(pattern)
        self.barcodes = barcodes_file if barcodes_file else False
            
    def _number_telomers(self, sequence: str) -> int:
        counts = re.findall(self.pattern, sequence)
        return len(counts)

    def _telomere_counts_barcode(self, sam: pysam.AlignmentFile) -> Tuple[dict, dict, int]:
        '''Counts number of telomeres from barcode file and returns the total reads per cells, 
        telomeres per cells and reads with missed barcodes. '''
        
        barcodes = pd.read_csv(self.barcodes, header=None, delimiter='\t', names=['bc'])
        
        telomeres_cells = dict().fromkeys(barcodes['bc'].to_list(), 0)
        total_reads_cells = dict().fromkeys(barcodes['bc'].to_list(), 0)
        missed_barcodes = 0

        for read in sam:
            try:
                cb = read.get_tag('CB')
                seq = read.seq
                assert isinstance(seq, str)
            except Exception:
                missed_barcodes += 1
            else:
                if cb in total_reads_cells:
                    total_reads_cells[cb] += 1
                if cb in telomeres_cells and self._number_telomers(seq) >= self.cutoff:
                    telomeres_cells[cb] += 1

        return telomeres_cells, total_reads_cells, missed_barcodes
    
    def _telomere_counts(self, sam: pysam.AlignmentFile) -> Tuple[dict, dict, int]:
        '''Counts number of telomeres without barcode file and returns the total reads per cells, 
        telomeres per cells and reads with missed barcodes.'''

        telomeres_cells = defaultdict(int)
        total_reads_cells = defaultdict(int)
        missed_barcodes = 0

        for read in sam:
            try:
                cb = read.get_tag('CB')
                seq = read.seq
                assert isinstance(seq, str)               
            except Exception:
                missed_barcodes += 1
            else:
                total_reads_cells[read.get_tag('CB')] += 1 

                if self._number_telomers(read.seq) >= self.cutoff:
                    telomeres_cells[read.get_tag('CB')] += 1

        return telomeres_cells, total_reads_cells, missed_barcodes
        
    def run_program(self) -> None:
        '''Generates teleomere counts for the bam file, with or without barcode file.
        Writes the results as csv files in the same folder of the bam file.'''
        
        telomere_file = self.input_bam.parent / 'telomemore_count_{self.pattern.pattern}.csv'
        totalreads_file = self.input_bam.parent / 'telomemore_total_{self.pattern.pattern}.csv'
        missed_barcods_file = self.input_bam.parent / 'telomemore_missed.txt'

        sam = pysam.AlignmentFile(self.input_bam, 'rb')
        
        if self.barcodes:
            telomeres_dict, total_dict, missed_barcodes = self._telomere_counts_barcode(sam)
        else:
            telomeres_dict, total_dict, missed_barcodes = self._telomere_counts(sam)

        with open(telomere_file, 'a+') as telomere:
            for key, value in telomeres_dict.items():
                print(f'{key},{value}', file=telomere)

        with open(totalreads_file, 'a+') as total:
            for key, value in total_dict.items():
                print(f'{key},{value}', file=total)

        with open(missed_barcods_file, 'w+') as missed:
            print(f'Number of missed barcodes = {missed_barcodes}', file=missed)
            
    
