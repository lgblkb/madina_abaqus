from functools import partial

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from box import Box
import itertools as it
import more_itertools as mit
from pathlib import Path
import logging

from utils import Step, get_steps, get_keywords, write_steps

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('madina')
files_folder = Path('files').resolve()
results_folder = Path('results').resolve()


def create_lateral_pseudo_steps():
    lateral_files = files_folder.joinpath('lateral')
    element_data = pd.read_excel(lateral_files.joinpath('element_data.xlsx'), header=None)
    inital_gap = pd.read_excel(lateral_files.joinpath('initial_gap.xlsx'), header=None)
    surface_behav = pd.read_excel(lateral_files.joinpath('surface_behav.xlsx'), header=None)
    surface_behav = list(surface_behav.ffill().groupby(0).apply(lambda df: df.iloc[:, 1:].values))
    assert len(surface_behav) == inital_gap.shape[0] == 61
    max_count = len(surface_behav)
    pseudo_steps = list()
    for i in range(max_count):
        pseudo_step = Step(get_keywords(lateral_files.joinpath('lateral_template.txt')))

        element_kw = pseudo_step['Element']

        # Update *Element
        new_name = element_kw.params['ELSET'][:-1] + str(i + 1)
        element_kw.params['ELSET'] = new_name

        # Read i'th row from element_data.xlsx and insert it into element_kw.data
        element_datum = element_data.iloc[i].tolist()
        element_kw.data = [element_datum]

        # Update *GAP
        gap_kw = pseudo_step['GAP']
        gap_kw.params['ELSET'] = new_name

        gap_kw.data[0][0] = -inital_gap.iloc[i, 0]
        if i == 0 or i == max_count - 1:  # if first or last, then ignore
            pass
        else:  # else multiply by 2
            gap_kw.data[0][-1] = float(gap_kw.data[0][-1]) * 2

        # Update *SURFACE BEHAVIOR
        surfbeh_kw = pseudo_step['SURFACE BEHAVIOR']
        surfbeh_kw.data = list(surface_behav[i])
        pseudo_steps.append(pseudo_step)

    write_steps(pseudo_steps, results_folder.joinpath('lateral_pseudo_steps.txt'))


def create_end_pseudo_steps():
    end_files = files_folder.joinpath('end')
    end_data = pd.read_excel(end_files.joinpath('element_data_end.xlsx'), header=None)
    area_data = pd.read_excel(end_files.joinpath('area_data.xlsx'), header=None)
    qz_curve = pd.read_excel(end_files.joinpath('qz_curve.xlsx'), header=None)

    max_count = 21
    pseudo_steps = list()
    for i in range(max_count):
        pseudo_step = Step(get_keywords(end_files.joinpath('end_template.txt')))

        element_kw = pseudo_step['Element']

        # Update *Element
        new_name = element_kw.params['ELSET'][:-1] + str(i + 1)
        element_kw.params['ELSET'] = new_name

        # Read i'th row from element_data_end.xlsx and insert it into element_kw.data
        element_datum = end_data.iloc[i].tolist()
        element_kw.data = [element_datum]

        # Update *GAP
        gap_kw = pseudo_step['GAP']
        gap_kw.params['ELSET'] = new_name

        # Replace only the last value
        gap_kw.data[0][-1] = area_data.iloc[i, 0]

        # Update *SURFACE BEHAVIOR
        surfbeh_kw = pseudo_step['SURFACE BEHAVIOR']
        surfbeh_kw.data = list(qz_curve.values)
        pseudo_steps.append(pseudo_step)

    write_steps(pseudo_steps, results_folder.joinpath('end_pseudo_steps.txt'))

    pass


def main():
    create_lateral_pseudo_steps()
    create_end_pseudo_steps()
    pass


if __name__ == '__main__':
    main()
