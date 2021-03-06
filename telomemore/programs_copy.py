## COPY OF CODE 
## ADD PROGRESS BAR
## ADD SAMPLE INFO TO Column
import re
from typing import Tuple, List
from abc import ABC, abstractmethod
import pysam
import pandas as pd
from pathlib import Path
from collections import defaultdict, namedtuple
from dataclasses import dataclass

@dataclass
class Count:
    '''Hold telomere count and total count when going through bam files.'''
    telomere: int = 0
    total: int = 0

class ProgramTelomemore(ABC):
    
    def __init__(self):
        self.counter = 0
    
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
    
    def reverse_comp(self, pattern: str) -> str:
        table = str.maketrans('ATCG', 'TAGC')
        return pattern.translate(table)[::-1]
    
    
class NobarcodeProgramTelomemore_copy(ProgramTelomemore):
    
    def telomere_count(self, sam: Path, cutoff: int, pattern: str) -> dict:
        sam_file = pysam.AlignmentFile(sam, 'rb')
        telomeres_cells = defaultdict(Count)
        missed_barcodes = 0
        rev_comp = self.reverse_comp(pattern)

        for read in sam_file:
            try:
                cb = read.get_tag('CB')
                seq = read.seq
                assert isinstance(seq, str)               
            except Exception:
                missed_barcodes += 1
            else:
                telomeres_cells[cb].total += 1 
                if self.number_telomere(pattern, seq) >= cutoff or self.number_telomere(rev_comp, seq) >= cutoff:
                    telomeres_cells[cb].telomere += 1
                    
            if self.counter % 10000000 == 0:
                print(f'Reads processed: {self.counter / 1000000} M')
            self.counter += 1
                    
        print(f'Number of missed barcodes or reads: {missed_barcodes} in {sam}')
        return telomeres_cells
    
    def run_program(self, bam_file: Path, cutoff: int, pattern: str, telomere_file: Path) -> None:
        telomeres_cells = self.telomere_count(bam_file, cutoff, pattern)
        df = pd.DataFrame({'bc': [key for key in telomeres_cells.keys()],
                          'count': [x.telomere for x in telomeres_cells.values()],
                          'total': [x.total for x in telomeres_cells.values()]})
        df['fraction'] = df['count'] / df['total']
        df['pattern'] = pattern
        df['file'] = bam_file
        df.to_csv(telomere_file, index=False)
        

class BarcodeProgramTelomemore_copy(ProgramTelomemore):
    
    def telomere_count(self, sam: Path, barcode: Path, cutoff: int, pattern: str) -> Tuple[dict, dict, int]:
        '''Counts number of telomeres from barcode file and returns the total reads per cells, 
        telomeres per cells and reads with missed barcodes. '''
        
        sam_file = pysam.AlignmentFile(sam, 'rb')
        barcode = pd.read_csv(barcode, header=None, delimiter='\t', names=['bc'])
        telomeres_cells = {x: Count() for x in barcode['bc'].to_list()}
        missed_barcodes = 0
        rev_comp = self.reverse_comp(pattern)

        for read in sam_file:
            try:
                cb = read.get_tag('CB')
                seq = read.seq
                assert isinstance(seq, str)
            except Exception:
                missed_barcodes += 1
            else:
                if cb in telomeres_cells:
                    telomeres_cells[cb].total += 1
                    if self.number_telomere(pattern, seq) >= cutoff or self.number_telomere(rev_comp, seq) >= cutoff:
                        telomeres_cells[cb].telomere += 1
                        
            if self.counter % 10000000 == 0:
                print(f'Reads processed: {self.counter / 1000000} M')
            self.counter += 1
                
        print(f'Number of missed barcodes or reads: {missed_barcodes} in {sam}')
        return telomeres_cells
    
    def run_program(self, bam_file: Path, barcode: Path, cutoff: int, pattern: str, telomere_file: Path) -> None:
        telomeres_cells = self.telomere_count(bam_file, barcode, cutoff, pattern)
        df = pd.DataFrame({'bc': [key for key in telomeres_cells.keys()],
                          'count': [x.telomere for x in telomeres_cells.values()],
                          'total': [x.total for x in telomeres_cells.values()]})
        df['fraction'] = df['count'] / df['total']
        df['pattern'] = pattern
        df['file'] = bam_file
        df.to_csv(telomere_file, index=False)
