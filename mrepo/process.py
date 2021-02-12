import click

from mrepo import ManagedRepo, filter_specs


def find_specs_to_process(mr, command, select):

    all_specs_to_process = mr.specs_to_process(command)

    constraints = {}
    if select:
        for constraint_pair in select.split(","):
            k, v = constraint_pair.split("=")
            constraints[k] = v

    specs_to_process = filter_specs(all_specs_to_process, **constraints)

    return specs_to_process


def generate_next_command_line(repo_fpath, command_name, select):

    mr = ManagedRepo(repo_fpath)
    command = mr.get_command(command_name)

    specs_to_process = find_specs_to_process(mr, command, select)

    spec = next(specs_to_process)

    command_line = mr.commandline_from_command_and_item(command, spec)

    return command_line


@click.command()
@click.argument('repo_fpath')
@click.argument('command_name')
@click.option('--select', default=None)
def echo_next_command(repo_fpath, command_name, select):

    command_line = generate_next_command_line(repo_fpath, command_name, select)

    click.echo(command_line)


@click.command()
@click.argument('repo_fpath')
@click.argument('command_name')
@click.option('--select', default=None)
def echo_all_commands(repo_fpath, command_name, select):

    mr = ManagedRepo(repo_fpath)
    command = mr.get_command(command_name)
    specs_to_process = find_specs_to_process(mr, command, select)

    for spec in specs_to_process:
        command_line = mr.commandline_from_command_and_item(command, spec)
        click.echo(command_line)

