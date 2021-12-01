from typing import Tuple
import pysam
from pathlib import Path
import pandas as pd
from collections import defaultdict
import re

class CountTelomeresFolder:
    '''Counts number of telomeres in all bam files in the input folder.
    User can specify pre defined barcodes from barcode file. If not, the program returns the barcodes
    found in the bam file.'''

    def __init__(self, input_folder: str, pattern: str, barcodes: bool = False, cutoff: int = 3):
        self.cutoff = cutoff
        self.pattern = re.compile(pattern)
        self.folder = Path(input_folder)
        self.bam_files = sorted([bam for bam in self.folder.rglob('*.bam') if bam.is_file()])
        self.barcode_files = sorted([bc for bc in self.folder.rglob('filtered_peak_bc_matrix/barcodes.tsv')]) if barcodes else False

    def _number_telomers(self, sequence: str) -> int:
        counts = re.findall(self.pattern, sequence)
        return len(counts)

    def _telomere_counts_barcode(self, sam: pysam.AlignmentFile, barcode_file: Path) -> Tuple[dict, dict, int]:
        '''Counts number of telomeres for barcodes in barcode file and returns the total reads per cells, 
        telomeres per cells and reads with missed barcodes.'''
        
        barcodes = pd.read_csv(barcode_file, header=None, delimiter='\t', names=['bc'])
        
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
        '''Counts number of telomeres and returns the total reads per cells, 
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
        
    def _run_program(self, file: Path, barcode: Path = None) -> None:
        '''Generates teleomere counts for each bam file in the input folder. Writes the results as csv files.
        With out without barcode file.'''
                
        telomere_file = file.parent / 'telomemore_count_{self.pattern.pattern}.csv'
        totalreads_file = file.parent / 'telomemore_total_{self.pattern.pattern}.csv'
        missed_barcods_file = file.parent / 'telomemore_missed.txt'

        sam = pysam.AlignmentFile(file, 'rb')
        
        if barcode:
            telomeres_dict, total_dict, missed_barcodes = self._telomere_counts_barcode(sam, barcode)
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
            
    def run_program(self):
        if self.barcode_files:
            for bamfile, bc in zip(self.bam_files, self.barcode_files):
                self._run_program(bamfile, bc)
        else:
            for bamfile in self.bam_files:
                self._run_program(bamfile)
            
    
