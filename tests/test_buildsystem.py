from buildtest.buildsystem.base import BuildConfig, supported_schemas

import pytest
import os

here = os.path.dirname(os.path.abspath(__file__))

def test_load_configs():

    # Examples folder
    examples_dir = os.path.join(here, "testdir")

    # An empty path evaluated to be a directory should exit
    with pytest.raises(SystemExit) as e_info:
        BuildConfig("")

    # Test loading config files
    for config_file in os.listdir(examples_dir):
        config_file = os.path.join(examples_dir, config_file)
        bc = BuildConfig(config_file)

        # The lookup should have the base schema
        # {'script': {'0.0.1': 'script-v0.0.1.schema.json', 'latest': 'script-v0.0.1.schema.json'}}
        for supported_schema in supported_schemas:
            assert supported_schema in bc.lookup
