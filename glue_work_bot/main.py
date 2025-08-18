from work_distributor import WorkDistributor
from output_handler import OutputHandler
import json
import argparse

def run_bot():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output-dir', required=True)
    args = parser.parse_args()
    output_dir = args.output_dir
    output_handler = OutputHandler(output_dir)
    with open("temp/glue_work_data.json") as f:
        data = json.load(f)
    print("Loaded data and started work distribution")
    work_distributor = WorkDistributor(data, output_handler)
    work_distributor.distribute_work()
    output_handler.save_output()

if __name__ == "__main__":
    run_bot()