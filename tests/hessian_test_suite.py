import sys
import math
import matplotlib.pyplot as plt
import torch
from timeit import default_timer as timer
import os
from subprocess import PIPE, run
import numpy as np
import shutil
import json

sys.path.append('./tests/python_test_utils')
import us_utils
import wenzel_utils
import generate_function

sys.path.append('./src')
import forward_diff

def generate_params(num_params, function_num):
    print("Generating params for function_num", function_num) #, " which is: ", functions[function_num][0])
    num_variables = len(functions[function_num][1])
    function_params = np.zeros(shape=(num_variables, num_params))
    for i, var in enumerate(functions[function_num][1]):
        variable_params = np.random.rand(num_params) * 10
        function_params[i] = variable_params
    reshaped = np.reshape(function_params, num_params*num_variables, order='F')
    param_string = "\n".join(str(x) for x in reshaped)
    param_f = open("params.txt", "w+")
    param_f.write(param_string)
    param_f.close()
    return reshaped

def print_param_to_file(params):
    param_string = "\n".join(str(x) for x in params)
    param_f = open(PARAMS_FILENAME, "w+")
    param_f.write(param_string)
    param_f.close()

def cleanup():
    if os.path.exists(INPUT_FILENAME):
        os.remove(INPUT_FILENAME)
    if os.path.exists(OUTPUT_FILENAME):
        os.remove(OUTPUT_FILENAME)
    if os.path.exists(NUMPY_PARAMS_FILENAME):
        os.remove(NUMPY_PARAMS_FILENAME)
    if os.path.exists(PARAMS_FILENAME):
        os.remove(PARAMS_FILENAME)

    if os.path.exists("./tests/hessian_test/utils"):
        folder = './tests/hessian/utils'
        for the_file in os.listdir(folder):
            file_path = os.path.join(folder, the_file)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            except Exception as e:
                print(e)
    if os.path.exists("./tests/hessian/results"):
        folder = './tests/hessian/results'
        for the_file in os.listdir(folder):
            file_path = os.path.join(folder, the_file)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            except Exception as e:
                print(e)

def generate_scaling_graph(max_us_single, max_us_hessian, max_wenzel_single, max_wenzel_hessian, denom):
    plt.figure(1)
    plt.subplot(211)
    plt.plot(denom, max_us_single,
             denom, max_us_hessian,
             denom, max_wenzel_single,
             denom, max_wenzel_hessian)
    plt.xticks(denom)
    plt.title('Scaling Times for 50,000 params # It: 10')
    # legend
    plt.legend( ('Us-Single', 'Us-Hessian', 'Wenzel-Single', 'Wenzel-Hessian'),
            shadow=True, loc=(0.01, 0.48), handlelength=1.5, fontsize=16)
    plt.savefig('./tests/results/scaling.png')
    plt.clf()



if __name__ == "__main__":
    import random, string
    functions = []
    alphabets = list(string.ascii_lowercase)
    alphabets.remove('i')

    for k in range(1, 20):
        function = generate_function.gen_other(k)
        functions.append(function)
        print(function)

    print(functions)

    INPUT_FILENAME = './tests/utils/hessian/functions.c'
    UTILS_FILENAME = './tests/utils/hessian/windows_utils.c'
    OUTPUT_FILENAME = './tests/utils/hessian/us_output.txt'
    PARAMS_FILENAME = './tests/utils/hessian/params.txt'
    MAX_PARAMS = 50000
    INIT_NUM_PARAMS = 10
    # num_vars = len(functions[0][1])
    NUM_ITERATIONS = 10
    NUM_THREADS_PYTORCH = 1
    RUN_C = True
    RUN_ISPC = False
    REVERSE = False

    max_us_single = []
    max_us_hessian = []
    max_wenzel_single = []
    max_wenzel_hessian = []
    num_vars_list = []
    
    output = {}

    for func_num, func in enumerate(functions):

        output[func[0]] = {}

        avg_us_single = []
        avg_us_hessian = []
        avg_pytorch = []
        avg_wenzel_single = []
        avg_wenzel_hessian = []
        denom = []
        num_params = INIT_NUM_PARAMS
        num_vars = len(func[1])

        # generate and compile our code
        us_utils.generate_function_c_file(func_num, functions, INPUT_FILENAME)
        us_utils.generate_derivatives_c_file(func_num, functions, INPUT_FILENAME, RUN_C, derivatives_filename="./tests/utils/hessian/ders_single", reverse=REVERSE, second_der=False)
        us_utils.compile_ours(RUN_C, runnable_filename="./tests/utils/static_code/runnable_single", utils_filename=UTILS_FILENAME, derivatives_filename="./tests/utils/hessian/ders_single")

        us_utils.generate_derivatives_c_file(func_num, functions, INPUT_FILENAME, RUN_C, derivatives_filename="./tests/utils/hessian/ders_hessian", reverse=REVERSE, second_der=True)
        us_utils.compile_ours(RUN_C, runnable_filename="./tests/utils/static_code/runnable_hessian", utils_filename=UTILS_FILENAME, derivatives_filename="./tests/utils/hessian/ders_hessian")

        while num_params <= MAX_PARAMS:

            print(num_params)

            # generate parameters
            params = generate_params(num_params, func_num)
            print_param_to_file(params)

            # generate and compile wenzel code
            wenzel_utils.generate_wenzel_file(func_num, num_params, functions, PARAMS_FILENAME, "single")
            wenzel_utils.compile_wenzel("single")
            wenzel_utils.generate_wenzel_file(func_num, num_params, functions, PARAMS_FILENAME, "hessian")
            wenzel_utils.compile_wenzel("hessian")

            # initialize arrays for run
            our_times_single = []
            our_times_hessian = []
            wenzel_times_single = []
            wenzel_times_hessian = []

            for i in range(NUM_ITERATIONS):
                ours_single = us_utils.run_ours(functions[func_num], num_params, functions, PARAMS_FILENAME, output_filename="./tests/utils/hessian/us_output_single.txt", runnable_filename="./tests/utils/static_code/runnable_single")
                ours_hessian = us_utils.run_ours(functions[func_num], num_params, functions, PARAMS_FILENAME, output_filename="./tests/utils/hessian/us_output_hessian.txt", runnable_filename="./tests/utils/static_code/runnable_hessian")
                wenzel_single = wenzel_utils.run_wenzel("single")
                wenzel_double = wenzel_utils.run_wenzel("hessian")
                
                num_ders = num_vars * num_vars

                assert len(ours_single[0]) == len(wenzel_single[0]) == num_params * num_vars
                assert len(ours_hessian[0]) == len(wenzel_double[0]) == num_ders * num_params

                for j in range(len(ours_hessian[0])):
                    assert math.isclose(float(ours_hessian[0][j]), float(wenzel_double[0][j]), abs_tol=10**1)
                for j in range(len(ours_single[0])):
                    assert math.isclose(float(ours_single[0][j]), float(wenzel_single[0][j]), abs_tol=10**1)

                our_times_single.append(float(ours_single[1]))
                our_times_hessian.append(float(ours_hessian[1]))
                wenzel_times_single.append(float(wenzel_single[1]))
                wenzel_times_hessian.append(float(wenzel_double[1]))

            # print for debug purposes
            print("Parameters: ", params[:10])

            output[func[0]][num_params] = {
                "us_grad": sum(our_times_single) / len(our_times_single),
                "us_hessian": sum(our_times_hessian) / len(our_times_hessian),
                "wenzel_grad": sum(wenzel_times_single) / len(wenzel_times_single),
                "wenzel_hess": sum(wenzel_times_hessian) / len(wenzel_times_hessian),
                "flags": "-ffast-math -O3",
                "num_vars": num_vars
            }

            # get the average time
            avg_us_single.append(sum(our_times_single) / len(our_times_single))
            avg_us_hessian.append(sum(our_times_hessian) / len(our_times_hessian))
            avg_wenzel_single.append(sum(wenzel_times_single) / len(wenzel_times_single))
            avg_wenzel_hessian.append(sum(wenzel_times_hessian) / len(wenzel_times_hessian))
            denom.append(num_params)

            if num_params < 10000:
                num_params += 2000
            elif num_params > 10000 and num_params < 1000000:
                num_params = num_params + 10000
            else:
                num_params = num_params + 100000

    output_file = open('./tests/results/full_results_hessian.json', "w+")
    output_file.write(json.dumps(output, indent=4, sort_keys=True))
    output_file.close()