## wrapper for running the pacakge ##
## import modules ##
import pathlib
import json
import pandas as pd

## import resources ##
from .Resources import EloConstructor
from .Resources import Elo
from .Resources import DataLoader
from .Resources import AirtableWrapper
from .Resources import QBModel


def run(perform_starter_update=True, model_only=False):
    ## load configs and secrets ##
    config = None
    secrets = None
    package_folder = pathlib.Path(__file__).parent.parent.resolve()
    with open("{0}/model_config.json".format(package_folder)) as fp:
        config = json.load(fp)
    with open("{0}/secrets.json".format(package_folder)) as fp:
        secrets = json.load(fp)
    ## load data ##
    data = DataLoader()
    ## run model ##
    print("Running QB model...")
    model = QBModel(data.model_df, config)
    model.run_model()
    if model_only:
        return model
    ## update starters ##
    at_wrapper = AirtableWrapper(
        model.games, secrets["airtable"], perform_starter_update=perform_starter_update
    )
    at_wrapper.update_qb_table()
    at_wrapper.update_qb_options()
    at_wrapper.update_starters()
    ## pause and wait for confirmation that manual edits have been made in airtable ##
    decision = input(
        'When starters have been updated in Airtable, type "RUN" and press enter:'
    )
    print(decision)
    ## run elo model ##
    print("Running Elo model...")
    elo = Elo(data.games, pd.DataFrame(model.data))
    elo.run()
    ## construct elo file ##
    if decision == "RUN":
        constructor = EloConstructor(data.games, model, at_wrapper, elo, package_folder)
        constructor.construct_elo_file()
