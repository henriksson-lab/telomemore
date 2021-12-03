from pathlib import Path
from typing import List, Tuple

class Files_copy:
    '''Returns list of one file or list of all bam files is input is a folder.'''
    def __init__(self, path: str):
        self.files = self.init_files(path)
        
    def init_files(self, path: str) -> List[Path]:
        if Path(path).is_file():
            return [Path(path)]
        return sorted([bam for bam in Path(path).rglob('*.bam') if bam.is_file()])
    
    @classmethod
    def make_folder(cls, input_folder: str) -> None:
        path = Path(input_folder)
        if not path.exists():
            path.mkdir(exist_ok=True, parents=True)
    
    @classmethod
    def save_files_default(cls, file: Path, pattern: str) -> Path:
        telomere_file = file.parent / f'telomemore_count_{pattern}.csv'
        return telomere_file
        
    @classmethod
    def save_files_output(cls, file: Path, input_folder: str, pattern: str) -> Tuple[Path, Path, Path]:
        folder = Path(input_folder)
        cls.make_folder(folder)
        telomere_file = folder / f'{file.stem}_telomemore_count_{pattern}.csv'
        return telomere_file
    
