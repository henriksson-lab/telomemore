import re
from typing import Tuple, List
from abc import ABC, abstractmethod
import pysam
import pandas as pd
from pathlib import Path

class ProgramTelomemore(ABC):
        
    @abstractmethod
    def telomere_count(self) -> Tuple[dict, dict, int]:
        pass
        
    @abstractmethod
    def run_program(self) -> None:
        pass
    
    def number_telomere(self, pattern: str, sequence: str) -> int:
        pattern = re.compile(pattern)
        counts = re.findall(pattern, sequence)
        return len(counts)
    
class NobarcodeProgramTelomemore(ProgramTelomemore):
    
    def telomere_count(self, sam: Path, cutoff: int, pattern: str) -> Tuple[dict, dict, int]:
        
        sam = pysam.AlignmentFile(sam, 'rb')
    
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
                if self.number_telomere(pattern, seq) >= cutoff:
                    telomeres_cells[read.get_tag('CB')] += 1

        return telomeres_cells, total_reads_cells, missed_barcodes
    
    def run_program(self, bam_file: Path, cutoff: int, pattern: str, telomere_file: Path, total_file: Path, missed_file: Path) -> None:
        
        telomeres_cells, total_reads_cells, missed_barcodes = self.telomere_count(bam_file, cutoff, pattern)
        
        with open(telomere_file, 'a+') as telomere:
            for key, value in telomeres_cells.items():
                print(f'{key},{value}', file=telomere)

        with open(total_file, 'a+') as total:
            for key, value in total_reads_cells.items():
                print(f'{key},{value}', file=total)

        with open(missed_file, 'w+') as missed:
            print(f'Number of missed barcodes = {missed_barcodes}', file=missed)
        

class BarcodeProgramTelomemore(ProgramTelomemore):
    
    def telomere_count(self, sam: Path, barcode: Path, cutoff: int, pattern: str) -> Tuple[dict, dict, int]:
        '''Counts number of telomeres from barcode file and returns the total reads per cells, 
        telomeres per cells and reads with missed barcodes. '''
        
        sam = pysam.AlignmentFile(sam, 'rb')
        barcode = pd.read_csv(barcode, header=None, delimiter='\t', names=['bc'])
        
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
                if cb in telomeres_cells and self.number_telomers(pattern, seq) >= cutoff:
                    telomeres_cells[cb] += 1

        return telomeres_cells, total_reads_cells, missed_barcodes
    
    def run_program(self, bam_file: Path, barcode: Path, cutoff: int, pattern: str, telomere_file: Path, total_file: Path, missed_file: Path) -> None:

        telomeres_cells, total_reads_cells, missed_barcodes = self.telomere_count(bam_file, barcode, cutoff, pattern)

        with open(telomere_file, 'a+') as telomere:
            for key, value in telomeres_cells.items():
                print(f'{key},{value}', file=telomere)

        with open(total_file, 'a+') as total:
            for key, value in total_reads_cells.items():
                print(f'{key},{value}', file=total)

        with open(missed_file, 'w+') as missed:
            print(f'Number of missed barcodes = {missed_barcodes}', file=missed)


