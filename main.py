import itertools as it
import pandas as pd
# from lgblkb_tools import logger

from utils import Step, write_steps


def process_cycle(cycle_path, out_filepath, pressure_data, mode):  # pressure data is added as argument
    cycle_data = pd.read_csv(cycle_path, index_col=0)
    y_data = cycle_data.drop(['X'], axis=1)
    pressure_generator = it.cycle(pressure_data['p'].tolist())  # cycle through pressure values at each step
    out_steps = list()
    for step_column in y_data.columns:
        step_num = int(step_column.split('-')[-1])
        the_step = Step.from_template('step_template_e.txt')
        the_step['Step'].params['name'] = f'Step-{step_num}'
        
        # change the last value of the first row in Dsload card to the next pressure value
        the_step['Dsload'].data[0][-1] = next(pressure_generator)
        
        row_labels = pd.DataFrame(the_step['Temperature'].data).iloc[:, 0]
        y_values = y_data[step_column].tolist()[::2]
        the_step['Temperature'].data = zip(row_labels, y_values)
        out_steps.append(the_step)
    write_steps(out_steps, out_filepath, mode=mode)


def main():
    cycle_paths = [f's7.0_output_files_NT_Path_cycle_{i + 1}.csv' for i in range(150)]
    # cycle_paths = [f's7.0_output_files_NT_Path_cycle_{1}.csv']
    pressure_data = pd.read_csv('pressure_data.csv')  # read pressure data
    output_filepath = 'output.inp'
    # if os.path.exists(output_filepath):
    #     os.remove(output_filepath)
    
    for cycle_path in cycle_paths:
        process_cycle(cycle_path, output_filepath, pressure_data, mode='a+')  # add pressure data as argument
    
    pass


if __name__ == '__main__':
    main()
