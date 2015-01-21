# Skeleton of a CLI

import click

import tiledrasterio


@click.command('tiledrasterio')
@click.argument('count', type=int, metavar='N')
def cli(count):
    """Echo a value `N` number of times"""
    for i in range(count):
        click.echo(tiledrasterio.has_legs)
