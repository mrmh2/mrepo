import click

from mrepo import ManagedRepo


# def list_

def available_commands(mr):

    commands_dict = mr.config["commands"]

    for cname, cinfo in commands_dict.items():
        print(cname)

@click.command()
@click.argument("repo_fpath")
def main(repo_fpath):

    mr = ManagedRepo(repo_fpath)

    dataspec_dict = mr.dataspec_dict

    # available_commands(mr)


    # spec = list(mr.available_items_by_item_spec().keys())[0]

    def specrep(spec):
        d = spec.__dict__
        items = [f"{k}={d[k]}" for k in sorted(d)]
        return ", ".join(items)

    reps = [
        specrep(spec)
        for spec in mr.available_items_by_item_spec().keys()
    ]

    print("\n".join(reps))


if __name__ == "__main__":
    main()
