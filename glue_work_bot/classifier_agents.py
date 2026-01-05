from dotenv import load_dotenv
from openai import OpenAI
from enum import Enum
import re
import os

class GlueWorkType(Enum):
    UNKNOWN = -1
    MAINTENANCE = 0
    CODE_REVIEW = 2
    MENTORING = 3
    DOCUMENTATION = 4
    COMMUNITY_MANAGMENT = 5
    LICENSE = 6
    REPORTING = 7

    def get_label(self):
        labels = {
            GlueWorkType.UNKNOWN: "Unknown",
            GlueWorkType.MAINTENANCE: "Maintenance",
            GlueWorkType.CODE_REVIEW: "Code Review",
            GlueWorkType.MENTORING: "Mentoring and Support",
            GlueWorkType.DOCUMENTATION: "Documentation",
            GlueWorkType.COMMUNITY_MANAGMENT: "Community Managment",
            GlueWorkType.LICENSE: "License",
            GlueWorkType.REPORTING: "Bug and Issue Reporting"
        }
        return labels[self]

class ClassifierAgent:
    SHORT_TEXT_MIN_WORDS = 3
    OPENAI_MODEL = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")

    def __init__(self, aggregator):
        load_dotenv()
        self.aggregator = aggregator
        self.client = OpenAI(api_key = os.getenv("OPENAI_KEY"))

    def clean(self, text):
        text = self.strip_quoted_lines(text)
        text = self.strip_templates(text)
        return text.strip()

    def strip_quoted_lines(self, text):
        return "\n".join(
            line for line in text.splitlines()
            if not line.strip().startswith(">")
        )

    def strip_templates(self, text):
        text = re.sub(r"```.*?```", "", text, flags=re.DOTALL)
        text = re.sub(r"\[!\[.*?\)\]", "", text)
        text = re.sub(r"\[x\]|\[ \]", "", text)
        return text

    def rule_based_short_text(self, text):
        words = text.split()
        return (len(words) < self.SHORT_TEXT_MIN_WORDS)

    def classify_data(self, prompts, system_msg):
        for prompt in prompts:
            r = self.client.chat.completions.create(
                model=self.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": system_msg},
                    {"role": "user", "content": prompt},
                ],
                max_completion_tokens=10,
            )
            classification = self.get_classification_from_response(r.choices[0].message.content or "-1")

            if (classification != -1):
                return classification
        return -1

    def get_classification_from_response(self, response):
        match = re.search(r"-?\d+", response)
        if match:
            number = int(match.group())
            try:
                return GlueWorkType(number)
            except ValueError:
                return GlueWorkType.UNKNOWN
        else:
            return GlueWorkType.UNKNOWN

class CodeAgent(ClassifierAgent):
    MAINTENANCE_REGEX = re.compile(
        r"(fix|resolves|regression|deflake|flaky|timeout|backport|revert|"
        r"migrate|deprecate|refactor|remove dead code|cve|security|bump|"
        r"upgrade|pin|ci|build|tests?)",
        re.IGNORECASE
    )

    TECH_PATTERN = re.compile(
        r"(PR\s?#?\d+|issue\s?#?\d+|\b\d+\.\d+\.\d+\b|\bCI\b|\bunit tests?\b)",
        re.IGNORECASE
    )

    def rule_based_maintenance(self, text):
        if self.MAINTENANCE_REGEX.search(text) and self.TECH_PATTERN.search(text):
            return True
        return False

    MAINTENANCE_SYSTEM_MSG = """
You are a GitHub maintenance-classifier.

Label each comment or PR text strictly as:
0 = Maintenance
-1 = Not Maintenance

Maintenance includes:
- bug fixes
- regressions
- deflakes
- CI/build fixes
- dependency bumps
- refactoring that improves maintainability
- security fixes
- code cleanup

Not maintenance includes:
- new features
- design discussions
- user questions
- general conversation
- unclear/ambiguous text

You must answer ONLY “0” or “-1”.
"""

    MAINTENANCE_FEWSHOT_EXAMPLES = """
Example:
Text: "Fix timeout regression in CI"
Label: 0

Example:
Text: "Add new gameplay feature"
Label: -1

Example:
Text: "Bump dependency from 2.3.1 to 2.3.2"
Label: 0

Example:
Text: "Thanks for the contribution!"
Label: -1
"""

    def classify_code_text(self, raw_text):
        cleaned = self.clean(raw_text)

        # RULE 1 — short text
        if self.rule_based_short_text(cleaned):
            return GlueWorkType.UNKNOWN

        # RULE 2 — strong maintenance regex
        if self.rule_based_maintenance(cleaned):
            return GlueWorkType.MAINTENANCE

        # LLM classification
        return self.classify_data(self.get_maintenance_prompt(cleaned), self.MAINTENANCE_SYSTEM_MSG)

    def get_maintenance_prompt(self, text):
        return f"""
{self.MAINTENANCE_FEWSHOT_EXAMPLES}

Text to classify:
{text}

Answer with 0 or -1 only.
"""

class MentoringAgent(ClassifierAgent):
    MENTORING_SYSTEM_MSG = """
You are a mentoring-classifier.

Label each comment strictly as:
3 = Mentoring
-1 = Not Mentoring
"""

    def __init__(self, aggregator):
        super().__init__(aggregator)

    def classify_mentoring_text(self, raw_text):
        cleaned = self.clean(raw_text)
        return self.classify_data(self.get_comment_prompt(cleaned), self.MENTORING_SYSTEM_MSG)

    def get_comment_prompt(self, text):
        return f"""
Comment Body:
{text}
"""

class CommunityAgent(ClassifierAgent):
    COMMUNITY_SYSTEM_MSG = """
You are a community-management-classifier.

Label each reply text strictly as:
5 = Community Management
-1 = Not Community Management
"""

    def __init__(self, aggregator):
        super().__init__(aggregator)

    def classify_community_text(self, raw_text):
        cleaned = self.clean(raw_text)
        return self.classify_data(self.get_community_managment_prompt(cleaned), self.COMMUNITY_SYSTEM_MSG)

    def get_community_managment_prompt(self, text):
        return f"""
Reply Body:
{text}
"""