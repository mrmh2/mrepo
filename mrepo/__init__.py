import os
import json
import logging
import pathlib

from types import SimpleNamespace
from collections import defaultdict, namedtuple

import parse
from ruamel.yaml import YAML

logger = logging.getLogger(__name__)


class ItemSpec(SimpleNamespace):

    def template_repr(self, template):
        return template.format(**self.__dict__)

    def json_repr(self):
        return json.dumps(self.__dict__)

    def __hash__(self):
        return self.json_repr().__hash__()

    def __getitem__(self, key):
        return self.__dict__[key]


class ManagedRepo(object):

    def __init__(self, base_path):
        self.base_path = pathlib.Path(base_path)
        self.data_path = self.base_path / "data"
        self.repospec_fpath = self.base_path / "repospec.yml"
        with open(self.repospec_fpath) as fh:
            self.config = YAML().load(fh)
        self.fname_template = self.config["fname_format"]
        self.itemclass = namedtuple("ItemSpecifier", self.config["item_fields"])
        self.fieldnames = self.config["item_fields"]

    @property
    def genotypes(self):

        genotypes = set([
            p.name
            for p in pathlib.Path(self.data_path).iterdir()
        ])

        return genotypes

    def get_command(self, command_name):
        return self.config['commands'][command_name]

    @property
    def dataspec_dict(self):
        dataspec_dict = {
            ds['type_name']: ds
            for ds in self.config['dataspecs']
        }

        return dataspec_dict

    def item_abspath(self, item_specifier, data_spec):

        filldict = dict(item_specifier.__dict__)
        filldict.update(**data_spec)
        
        fname = self.fname_template.format(**filldict)

        dirpath = pathlib.Path(
            self.data_path,
            item_specifier.genotype,
            item_specifier.position,
            data_spec['type_name']
        )
        # dirpath.mkdir(exist_ok=True, parents=True)

        return dirpath / fname

    def list_by_data_spec(self, item_specifier, data_spec):

        dirpath = pathlib.Path(
            self.data_path,
            item_specifier.genotype,
            item_specifier.position,
            data_spec['type_name']
        )

        # print(f"Check {dirpath}")
        # FIXME - can't parse {name}{ext} properly
        return [
            parse.parse(self.fname_format, fpath.name)
            for fpath in pathlib.Path(dirpath).iterdir()
        ]

    def available_items_by_item_spec(self):
        available_specs = defaultdict(list)
        for (dirpath, dirnames, filenames) in os.walk(self.data_path):
            for fname in filenames:
                item_spec, data_spec = self.fname_to_(fname)
                available_specs[item_spec].append(data_spec)

        return available_specs

    def fname_to_(self, fname):
            result = parse.parse(self.fname_template, fname).named

            # Check and extract the item
            assert set(self.fieldnames).issubset(set(result))
            # item = self.itemclass(**{k: result[k] for k in self.fieldnames})
            item = ItemSpec(**{k: result[k] for k in self.fieldnames})

            # Get the datastage??? spsec
            dataspec_fields = set(result) - set(self.fieldnames)
            dataspec = {k: result[k] for k in dataspec_fields}

            return item, dataspec

    def item_specs_by_dataspec(self):
        by_dataspec = defaultdict(set)
        for item, dataspecs in self.available_items_by_item_spec().items():
            for dataspec in dataspecs:
                by_dataspec[dataspec['type_name']].add(item)

        return by_dataspec

    def fname_for_spec(self, dataspec, spec):
        metadata = vars(spec)
        metadata.update(dataspec)
        return self.fname_format.format(**metadata)

    def specs_to_process(self, command):
        by_dataspec = self.item_specs_by_dataspec()

        specsets = [
            set(by_dataspec[input_name])
            for input_name in command['inputs']
        ]

        all_input_specs = set.intersection(*specsets)

        specsets = [
            set(by_dataspec[input_name])
            for input_name in command['outputs']
        ]

        all_output_specs = set.intersection(*specsets)

        return list(all_input_specs - all_output_specs)


    def commandline_from_command_and_item(self, command, item, automkdir=False):

        components = [command["command"]]

        for inp in command["inputs"]:
            components.append(self.item_abspath(item, self.dataspec_dict[inp]))

        for extra in command.get("extras", []):
            components.append(extra)

        for output in command["outputs"]:
            output_abspath = self.item_abspath(item, self.dataspec_dict[output])

            if automkdir:
                logger.info(f"Creating {output_abspath.parent}")
                output_abspath.parent.mkdir(exist_ok=True, parents=True)

            components.append(output_abspath)

        return " ".join(str(s) for s in components)



def filter_specs(specs, **kwargs):

    def filter_by_conditions(spec):
        conditions = [
            spec.__dict__[k] == v
            for k, v in kwargs.items()
        ]
        return all(conditions)

    return filter(filter_by_conditions, specs)


def display_specs(specs, sort_key=None):

    if sort_key != None:
        display_specs = sorted(specs, key=lambda x: x[sort_key])
    else:
        display_specs = specs

    for spec in display_specs:
        print(spec)
