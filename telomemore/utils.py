import re
from pathlib import Path
import pysam

class BamFile:
    '''Searches through a folder and stores all bam files in a list.'''
    
    def __init__(self, folder: str):
        self.folder = Path(folder)
        self.files = sorted([bam for bam in self.folder.rglob('*.bam') if bam.is_file()])

class BaseKmerFinder:
    '''Superclass for finding kmer in bam file.'''
    
    def __init__(self, folder: str, pattern: str, out_folder: str):
        self.bam = BamFile(folder)
        self.pattern = re.compile(pattern)
        self.out_folder = Path(out_folder).resolve()
        
    def _number_telomers(self, sequence: str) -> int:
        counts = re.findall(self.pattern, sequence)
        return len(counts)


    
def make_directory(directory: str) -> None:
    '''Create directories which does not yet exists'''
    
    directory = Path(directory)
    if not directory.exists():
        directory.mkdir(exist_ok=True, parents=True)
