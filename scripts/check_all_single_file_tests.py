import argparse
import glob
import os
import sys

import check_single_file_test

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("alloy_model_file")
    args = parser.parse_args()

    alloy_model_file = os.path.abspath(args.alloy_model_file)

    # Get the directory where the script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Set the working directory to the script's parent directory
    parent_dir = os.path.dirname(script_dir)
    os.chdir(parent_dir)

    test_models = glob.glob("./test/single_file/*.als")
    for test_model in test_models:
        sys.argv = ["check_single_file_test.py", alloy_model_file, test_model]
        check_single_file_test.main()


if __name__ == "__main__":
    main()