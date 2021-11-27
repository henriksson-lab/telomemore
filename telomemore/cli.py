import click
from telomemore.countkmers import CountKmers
from telomemore.counttelomeres import CountTelomeres
 
@click.group()
def cli():
    '''WELCOME TO teloMeMore'''
    
    pass

             
@cli.command()
@click.argument('input_folder')
@click.argument('output_folder')
@click.argument('pattern')
def count_kmers(input_folder, output_folder, pattern):
    '''Count the occurances of kmers user specifies and stores the results in a csv file. 
    Finds all bam files in the input folder and output files is stored in output folder.
    
    Required arguments: 
    input_folder,
    output_folder,
    pattern. '''
    
    kmers = CountKmers(input_folder=input_folder, output_folder=output_folder, pattern=pattern)
    kmers.run_program()
    
    
    
@cli.command()
@click.argument('input_folder')
@click.argument('output_folder')
@click.argument('pattern')
@click.argument('cutoff')
def count_telomeres(input_folder, output_folder, pattern, cutoff):
    '''Count the occurances of telomere read in each cell. The telomere is defined by the user, as a read
    which contains the pattern a number of times above the specified cutoff.
    The program goes through all bam files in the input folder and stores the results as csv files in the output
    folder.
    A cell is defined by the cell barcode in the bam file.
    
    Required arguments: 
    input_folder,
    output_folder,
    pattern,
    cutoff.'''
    
    telomeres = CountTelomeres(input_folder=input_folder, output_folder=output_folder, pattern=pattern, cutoff=cutoff)
    telomeres.run_program()
