import os

import numpy as np
from typing import List

import pandas as pd
# from lgblkb_tools import logger


class Keyword(object):
    def __init__(self, keyword_name, **params):
        self.keyword_name = keyword_name
        self.params = params
        self.data = list()
    
    @classmethod
    def from_line(cls, line):
        keyword_info = process_keyword(line)
        return cls(keyword_info['name'], **keyword_info['params'])
    
    def __bool__(self):
        return True
    
    def __eq__(self, other):
        if isinstance(other, str):
            return self.keyword_name == other
        elif isinstance(other, Keyword):
            return self.keyword_name == other.keyword_name
    
    def read_data_as_list(self, line):
        parts = line.replace(' ', '').split(',')
        self.data.append(parts)
    
    def get_lines(self):
        out_params = list()
        for k, v in self.params.items():
            if isinstance(v, bool) and v:
                out_params.append(k)
            else:
                out_params.append(f"{k}={v}")
        lines = list()
        lines.append("*" + ", ".join(map(str, [self.keyword_name] + out_params)))
        lines.extend([", ".join(map(str, line_data)) for line_data in self.data])
        return lines


class Step(object):
    def __init__(self, keywords):
        self.keywords: List[Keyword] = keywords
    
    @staticmethod
    def from_template(template_file):
        step = get_steps(template_file)[0]
        return step
    
    def __getitem__(self, item):
        if isinstance(item, int):
            return self.keywords[item]
        elif isinstance(item, str):
            for keyword in self.keywords:
                if keyword.keyword_name == item:
                    return keyword
        else:
            raise NotImplementedError('Unsupported type of index', dict(item_type=str(type(item))))
    
    def __len__(self):
        return len(self.keywords)
    
    def get_lines(self):
        last_line = "** ----------------------------------------------------------------"
        # return "\n".join([x.render() for x in self.keywords] + [last_line])
        lines = list()
        for keyword in self.keywords:
            lines.extend(keyword.get_lines())
        return lines + [last_line]


def process_keyword(line):
    # logger.info("line: %s",line)
    keyword_info = dict()
    parts = line.split(', ')
    keyword_info['name'] = parts[0][1:]
    keyword_params = dict()
    for key_value_pair in parts[1:]:
        if '=' in key_value_pair:
            key, value = key_value_pair.split('=')
            keyword_params[key] = value
        else:
            keyword_params[key_value_pair] = True
    keyword_info['params'] = keyword_params
    return keyword_info


def get_steps(steps_filepath):
    with open(steps_filepath) as file:
        lines = file.readlines()
    
    steps = list()
    step_keywords = list()
    current_keyword = None
    for i, line in enumerate(lines):
        line = line.strip()  # remove trailing spaces and newline characters
        # logger.debug("line: %s", line)
        if line.startswith('**'):  # I suppose double start represents a commented line?
            continue
        elif line.startswith('*'):  # Keyword line. Contains name of the keyword and optionally some parameters
            current_keyword = Keyword.from_line(line)
            step_keywords.append(current_keyword)
            if current_keyword.keyword_name == 'End Step':
                steps.append(Step(step_keywords.copy()))
                step_keywords.clear()
        elif current_keyword:
            current_keyword.read_data_as_list(line)
    
    return steps


def write_steps(steps, out_filepath, mode='w'):
    with open(out_filepath, mode) as file:
        for step in steps:
            file.write("\n".join(step.get_lines()))
            file.write("\n")


def get_step_template():
    step = get_steps('step_template_e.txt')[0]
    return step


def process_cycle(cycle_path, out_filepath, mode):
    cycle_data = pd.read_csv(cycle_path, index_col=0)
    y_data = cycle_data.drop(['X'], axis=1)

    out_steps = list()
    for step_column in y_data.columns:
        step_num = int(step_column.split('-')[-1])
        the_step = Step.from_template('step_template_e.txt')
        the_step['Step'].params['name'] = f'Step-{step_num}'
        row_labels = pd.DataFrame(the_step['Temperature'].data).iloc[:, 0]
        y_values = y_data[step_column].tolist()[::2]
        the_step['Temperature'].data = zip(row_labels, y_values)
        out_steps.append(the_step)
    write_steps(out_steps, out_filepath, mode=mode)

def process_pressure(pressure_path, out_filepath, mode):
    pressure_data = pd.read_csv(pressure_path, index_col=0 )
    p_data = pressure_data.drop(['step'], axis=0)

    out_steps = list()
    for pressure_column in p_data.columns:
        step_num = int(step_column.split('-')[-1])
        the_step = Step.from_template('step_template_e.txt')
        the_step['Step'].params['name'] = f'Step-{step_num}'
        surface_labels = pd.DataFrame(the_step['Dsload'].data).iloc[:,0]
        p_labels = pd.DataFrame(the_step['Dsload'].data).iloc[:, 1]
        p_values = p_data[pressure_column].tol0ist
        the_step['Dsload'].data = zip(surface_labels, p_labels, p_values)
        out_steps.append(the_step)
    write_steps(out_steps, out_filepath, mode=mode)


def main():
    # cycle_paths = list()
    # for i in range(150):
    #     cycle_path = f's7.0_output_files_NT_Path_cycle_{i + 1}.csv'
    #     cycle_paths.append(cycle_path)
    
    cycle_paths = [f's7.0_output_files_NT_Path_cycle_{i + 1}.csv' for i in range(150)]
    pressure_path = 'pressure_data.csv'
    output_filepath = 'output_e.inp'
    # if os.path.exists(output_filepath):
    #     os.remove(output_filepath)
    
    for cycle_path in cycle_paths:
        process_cycle(cycle_path, output_filepath, mode='a+')

    process_pressure(pressure_path,output_filepath,mode='a+')

    pass


if __name__ == '__main__':
    main()
