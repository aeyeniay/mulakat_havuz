import os
import sys
import click

@click.group()
def cli():
    """Mülakat Soru Havuzu CLI"""
    pass

@cli.command()
@click.option('--role', required=False, help='Rol kodu')
@click.option('--difficulty', required=False, type=int, help='Zorluk katsayısı (2,3,4)')
@click.option('--count', required=False, type=int, default=10, help='Üretilecek soru sayısı')
@click.option('--job-file', required=False, type=click.Path(exists=True), help='İlan metni dosyası')
def generate(role, difficulty, count, job_file):
    """Soru üret (PLACEHOLDER)."""
    click.echo("CLI iskeleti hazır. Üretim mantığı eklenecek.")
    if job_file:
        click.echo(f"İlan dosyası: {job_file}")
    click.echo(f"role={role} difficulty={difficulty} count={count}")

@cli.command('batch-generate')
@click.option('--config-file', required=False, type=click.Path(exists=True))
def batch_generate(config_file):
    """Toplu soru üret (PLACEHOLDER)."""
    click.echo("Batch üretim CLI iskeleti hazır. Mantık eklenecek.")
    if config_file:
        click.echo(f"Config: {config_file}")

if __name__ == '__main__':
    cli()
