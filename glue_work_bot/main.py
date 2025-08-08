from github_scraper import GitHubScraper
from classifier_agents import ClassifierAgent
from config_handler import ConfigHandler
from output_handler import OutputHandler
import argparse
import os
import yaml

def main():
    github_scraper = GitHubScraper()
    classifier_agent = ClassifierAgent()
    issues = github_scraper.get_issues(per_page=3)
    for issue in issues:
        print("\n-------------------ISSUE CLASSIFICATION-------------------\n")
        issue_str = github_scraper.get_issue_str(issue)
        if issue_str == "":
            print("Bot, continuing...")
            continue
        response = classifier_agent.classify_data(issue_str)
        print("\n" + issue_str + "\n")
        print("\n-------------------CLASSIFICATION-------------------\n")
        print(response)
        print("\n-------------------ISSUE CLASSIFICATION END-------------------\n")
    pull_requests = github_scraper.get_pull_requests(per_page=3)
    for pull_request in pull_requests:
        print("\n-------------------PULL REQUEST CLASSIFICATION-------------------\n")
        pull_request_str = github_scraper.get_pull_request_str(pull_request)
        if pull_request_str == "":
            print("Bot, continuing...")
            continue
        response = classifier_agent.classify_data(pull_request_str)
        print("\n" + pull_request_str + "\n")
        print("\n-------------------CLASSIFICATION-------------------")
        print(response)
        print("\n-------------------PULL REQUEST CLASSIFICATION END-------------------\n")

def test():
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
    test()