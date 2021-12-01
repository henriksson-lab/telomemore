from pathlib import Path
from typing import List

class Barcodes:
    '''Returns list of one file or list of all barcodes.tsv files is input is a folder.'''
    def __init__(self, path: str):
        self.files = self.init_barcodes(path)
        
    def init_barcodes(self, path: str) -> List[Path]:
        if Path(path).is_file():
            return [Path(path)]
        
        return sorted([bc for bc in Path(path).rglob('filtered_peak_bc_matrix/barcodes.tsv')])
    
#WORKS
