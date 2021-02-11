import shutil
import logging
import pathlib

import click

from mrepo import ManagedRepo


logger = logging.getLogger(__file__)


@click.command()
@click.argument("repo_fpath")
@click.argument("output_dirpath")
def main(repo_fpath, output_dirpath):

    logging.basicConfig(level=logging.INFO)

    dspec_name = "projection"

    mr = ManagedRepo(repo_fpath)

    new_base_path = pathlib.Path(output_dirpath)
    new_data_path = new_base_path/"data"
    new_base_path.mkdir(exist_ok=True, parents=True)
    repospec_dstpath = new_base_path/"repospec.yml"
    shutil.copy(mr.repospec_fpath, repospec_dstpath)

    dspec = mr.dataspec_dict[dspec_name]

    ispecs_by_dspec = mr.item_specs_by_dataspec()

    ispecs = ispecs_by_dspec[dspec_name]

    for ispec in ispecs:
        abspath = mr.item_abspath(ispec, dspec)

        dirpath_template = "{data_dirpath}/{genotype}/{position}/{dspec_name}"
        metadata = {
            "data_dirpath": new_data_path,
            "dspec_name": dspec_name
        }
        metadata.update(ispec.__dict__)
        metadata.update(dspec)

        dirpath = pathlib.Path(dirpath_template.format(**metadata))
        fname = mr.fname_template.format(**metadata)
        dstpath = dirpath/fname

        dirpath.mkdir(exist_ok=True, parents=True)
        logger.info(f"Copy {abspath} to {dstpath}")
        shutil.copy(abspath, dstpath)



if __name__ == "__main__":
    main()
