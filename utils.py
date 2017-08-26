import json
import numpy as np
from math import isnan
from sklearn.model_selection import train_test_split


class MyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        else:
            return super(MyEncoder, self).default(obj)


def check_for_nan_elements(variables_dict, variables_to_check, verbose=False):
    idx_to_remove = []
    num_variables = len(variables_dict)
    counter = 0
    for variable in variables_to_check:
        counter += 1
        for idx, element in enumerate(variables_dict[variable]):
            if isnan(element):
                idx_to_remove.append(idx)
        if verbose:
            print("Finished Checking NaN for Variable {} of {}".format(counter, num_variables))
    print("Finished Checking for NaN Elements")
    return set(idx_to_remove)


def remove_nan_elements(variables_dict, idx_to_remove, verbose=False):
    num_variables = len(variables_dict)
    counter = 0
    for key, value in variables_dict.items():
        counter += 1
        variables_dict[key] = [i for j, i in enumerate(value) if j not in idx_to_remove]
        if verbose:
            print("Finished Removing NaN for Variable {} of {}".format(counter, num_variables))
    print('Finished Removing NaN Elements')


def write_to_json(variables_dict, verbose=False):
    print('Beginning json dump')
    counter = 0
    num_variables = len(variables_dict)
    for key, value in variables_dict.items():
        counter += 1
        with open('json_files/' + key + '.json', 'w') as fd:
            fd.write(json.dumps(value, indent=4, cls=MyEncoder))
        if verbose:
            print("Finished writing to json variable {} of {}".format(counter, num_variables))


def load_from_json(predictors, response, verbose=False):
    variables_dict = {}
    num_variables = len(predictors) + 1
    counter = 0
    print('Beginning Download')
    for predictor in predictors + [response]:
        counter += 1
        with open('json_files/' + predictor + '.json', 'r') as fd:
            variables_dict[predictor] = json.loads(fd.read())
        if verbose:
            print("Finished downloading json variable {} of {}".format(counter, num_variables))
    return variables_dict


def create_model_data(variables_dict, predictors, response):
    predictors = np.column_stack(([variables_dict[variable_name] for variable_name in predictors]))
    print('Finished Munging Data')
    xtrain, xtest, ytrain, ytest = train_test_split(predictors, variables_dict[response])
    ytrain_hot = np.zeros((len(ytrain), 2))
    ytrain_hot[np.arange(len(ytrain)), ytrain] = 1
    ytest_hot = np.zeros((len(ytest), 2))
    ytest_hot[np.arange(len(ytest)), ytest] = 1
    print('Finished Splitting Data')
    return xtrain, xtest, ytrain_hot, ytest_hot


def scale_and_save(variables_dict, predictor_names, verbose=False):
    scaling_params = {}
    num_variables = len(predictor_names)
    counter = 0
    for variable_name in predictor_names:
        counter += 1
        mean = np.mean(variables_dict[variable_name])
        std = np.std(variables_dict[variable_name])
        variables_dict[variable_name] = (variables_dict[variable_name] - mean) / std
        scaling_params[variable_name] = {'mean': mean, 'std': std}
        if verbose:
            print("Finished Scaling Variable {} of {}".format(counter, num_variables))
    with open('scaling_params.json', 'w') as fd:
        fd.write(json.dumps(scaling_params, indent=4))
    print('Finished Scaling Variables')


def scale_individual_stock(variables_dict):
    with open('scaling_params.json', 'r') as fd:
        scaling_params = json.loads(fd.read())
    for key, value in variables_dict.items():
        if 'MA' not in key:
            mean = scaling_params[key]['mean']
            std = scaling_params[key]['std']
            variables_dict[key] = (value - mean) / std
