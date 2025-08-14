from config_handler import ConfigHandler
from output_handler import OutputHandler
import argparse

def run_bot():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config-file', required=True)
    parser.add_argument('--output-dir', required=True)
    args = parser.parse_args()
    config_file = args.config_file
    output_dir = args.output_dir
    config_handler = ConfigHandler(config_file)
    output_handler = OutputHandler(output_dir, config_handler)
    output_handler.save_output()

if __name__ == "__main__":
    run_bot()