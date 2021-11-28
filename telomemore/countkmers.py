from telomemore.utils import BaseKmerFinder
from typing import Tuple
from collections import Counter, defaultdict
import pysam
from pathlib import Path
import pandas as pd
from joblib import Parallel, delayed

class CountKmers(BaseKmerFinder):
    '''Finds occurances of kmers in bam file and stores'''
    
    def __init__(self, input_folder: str, pattern: str, output_folder: str, threads: int = 1):
        super().__init__(input_folder, pattern, output_folder, threads)
        
    def _k_mer_per_read(self, bamfile: Path) -> Tuple[dict, int]:
        '''Counts number of kmer in each read and stores the number in list.'''
        kmer_counts = []
        missed_reads = 0
        for read in bamfile:
            try:
                counts = self._number_telomers(read.seq)
                kmer_counts.append(counts)
            except Exception:
                missed_reads += 1

        counter = Counter(kmer_counts)
        return counter, missed_reads
    
    def _run_program(self, file: str):
        '''Outputs a csv file with information about kmer occurance for each bam file in the folder.'''
        
        sam = pysam.AlignmentFile(file, 'rb')

        counter, missed_reads = self._k_mer_per_read(sam)

        # part[-3] is the name of the folder which contains the out folder and the possorted.bam file 
        kmer_file = self.out_folder / f'{file.parts[-3]}_{self.pattern.pattern}_kmer.csv'
        exception_file = self.out_folder / f'{file.parts[-3]}_missed_reads.txt'

        number = [key for key in counter.keys()]
        count = [value for value in counter.values()]

        pd.DataFrame({'number': number, 'count': count}).to_csv(kmer_file, index=False)

        with open(exception_file, 'w+') as missed:
            print(f'Reads that could not be read in {file}: {missed_reads}', file=missed)

        

        
