import click
from telomemore.countkmers import CountKmers
from telomemore.counttelomeres import CountTelomeres
from telomemore.utils import make_directory
 
@click.group()
def cli():
    '''WELCOME TO teloMeMore'''
    
    pass

             
@cli.command()
@click.option('--input_folder', '-i', required=True, prompt=True)
@click.option('--output_folder', '-o', required=True, prompt=True)
@click.option('--pattern', '-p', required=True, prompt=True)
@click.option('--threads', '-t', default=1)
def count_kmers(input_folder, output_folder, pattern, threads):
    
    '''Count the occurances of kmers user specifies and stores the results in a csv file. 
    Finds all bam files in the input folder and output files is stored in output folder.
    
    Required arguments: 
    input_folder,
    output_folder,
    pattern. '''
    
    make_directory(output_folder)
    
    kmers = CountKmers(input_folder=input_folder, output_folder=output_folder, pattern=pattern, threads=threads)
    
    click.echo(f'Counting kmers with pattern {pattern} in files listed in {input_folder}...')
    kmers.run_program()
    click.echo(f'Counting of kmers done! Look for files in {output_folder}.')
    
    
    
@cli.command()
@click.option('--input_folder', '-i', required=True, prompt=True)
@click.option('--output_folder', '-o', required=True, prompt=True)
@click.option('--pattern', '-p', required=True, prompt=True)
@click.option('--cutoff', '-c', required=True, prompt=True)
@click.option('--threads', '-t', default=1)
def count_telomeres(input_folder, output_folder, pattern, cutoff, threads):
    
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
    
    make_directory(output_folder)
    
    telomeres = CountTelomeres(input_folder=input_folder, output_folder=output_folder, pattern=pattern, cutoff=cutoff, threads=threads)
    
    click.echo(f'Counting telomeres with pattern {pattern} in files in {input_folder}...')
    telomeres.run_program()
    click.echo(f'Counting of telomeres done! Look for files in {output_folder}.')
