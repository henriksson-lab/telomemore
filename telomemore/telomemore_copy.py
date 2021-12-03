from pathlib import Path
from typing import List, Optional
from telomemore.filehandler_copy import Files_copy
from telomemore.programs import ProgramTelomemore
from telomemore.barcodes import Barcodes
from dataclasses import dataclass


@dataclass
class TeloMemore_copy:
    pattern: str
    files: Files_copy
    program: ProgramTelomemore
    cutoff: int = 3
    barcode: Optional[Barcodes] = None
    output_dir: Optional[str] = None 
    
    def output_files(self, file: Path) -> List[Path]:
        if self.output_dir is not None:
            return self.files.save_files_output(file, self.output_dir, self.pattern)
        return self.files.save_files_default(file, self.pattern)
  
    def run_program(self) -> None:
        if self.barcode is not None:
            for bam, bc in zip(self.files.files, self.barcode.files):
                print(f'processing {bam}...')
                telomere_file = self.output_files(bam)
                self.program.run_program(bam, bc, self.cutoff, self.pattern, telomere_file)
                print(f'{bam} done!')
        else:
            for bam in self.files.files:
                print(f'processing {bam}...')
                telomere_file = self.output_files(bam)
                self.program.run_program(bam, self.cutoff, self.pattern, telomere_file)
                print(f'{bam} done!')
            
