import click
from telomemore.filehandler import Files
from telomemore.programs import NobarcodeProgramTelomemore, BarcodeProgramTelomemore, ProgramTelomemore
from telomemore.barcodes import Barcodes
from telomemore.telomemore import TeloMemore

@click.group()
def cli():
    '''WELCOME TO teloMeMore'''
    pass
   
    
@cli.command()
@click.option('--inputs', '-i', type=str, required=True, help='input folder or file for TeloMeMore')
@click.option('--pattern', '-p', type=str, required=True, default='CCCTAA', help='pattern for searching the bam files')
@click.option('--barcodes', '-bc', type=str, required=False, default=None, help='barcode file or folder is barcode file exists')
@click.option('--cutoff', '-c', type=int, required=False, default=3, help='cutoff for which telomermore count occurance of pattern as telomere read')
@click.option('--output', '-o', type=str, required=False, default=None, help='specify customize output folder if wanted')
def count(inputs, barcodes, pattern, cutoff, output):
    
    '''Count the occurances of telomere read in each cell. The telomere is defined by the user, as a read
    which contains the pattern a number of times above the specified cutoff.
    The program goes through all bam files in the input folder and stores the results as csv files in the output
    folder. A cell is defined by the cell barcode in the bam file.

    Required arguments: 
    
    inputs: a folder or file
    
    pattern: a pattern which TeloMemore searches the bamfile for. 'CCCTAA' as default. 
        
    Optional arguments:
    
    cutoff: integer for which Telomemore uses as cutoff for counting read as telomere. Default = 3.
    
    barcodes: file or folder with barcode files.
    
    output: Specify folder to which the count files should be written. Default is the same folder as input. 
    
    '''

    files = Files(inputs)
    
    if barcodes is not None:
        program = BarcodeProgramTelomemore()
        barcodes = Barcodes(barcodes)
        telomemore = TeloMemore(pattern=pattern, files=files, program=program, cutoff=cutoff, barcode=barcodes, output_dir=output)
        telomemore.run_program()
    else:
        program = NobarcodeProgramTelomemore()
        telomemore = TeloMemore(pattern=pattern, files=files, program=program, cutoff=cutoff, output_dir=output)
        telomemore.run_program()
    
    
    
    
    
  
    
    
