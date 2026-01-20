from work_distributor import WorkDistributor
import json

def run_bot():
    with open("temp/glue_work_data.json") as f:
        data = json.load(f)
    work_distributor = WorkDistributor(data)
    work_distributor.distribute_work()

if __name__ == "__main__":
    run_bot()