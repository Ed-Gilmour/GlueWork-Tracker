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

    def classify_data(self, prompts, system_msg, def_class):
        for prompt in prompts:
            r = self.client.chat.completions.create(
                model=self.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": system_msg},
                    {"role": "user", "content": prompt},
                ],
                max_completion_tokens=10,
            )
            classification = self.get_classification_from_response(r.choices[0].message.content or "-1", def_class)

            if (classification != -1):
                return classification
        return -1

    def get_classification_from_response(self, response, def_class):
        match = re.search(r"-?\d+", response)
        if match:
            number = int(match.group())
            if number == -1:
                return GlueWorkType.UNKNOWN
            else:
                return def_class
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


    POS_CUES = [
        # Feature-looking openers that are actually repair/unblock/parity
        ("Adds glob syntax to proxy server to resolve mismatch with rules and unblock issue #173435.", 0),
        ("Adds headers to proxy rules to align behavior across platforms and fix incorrect proxying in #173434.", 0),
        ("This change improves overscroll to match native Android behavior; fixes clipped fling behavior (Fixes #169659).", 0),

        # Follow-up / refiling / migration / move-as-cleanup
        ("Follow up of #174421: migrate some files to WidgetState to reduce conflicts; remaining files in later PRs.", 0),
        ("Refiling of #169273: bundle experimental data assets to restore expected tool behavior and unblock usage.", 0),
        ("Move PageTransitionsBuilder from material/ to widget/ to keep types in the correct layer.", 0),

        # Classic fixes & CI/test stability
        ("Fix DropdownMenu filtering by storing selected value instead of index; add a regression test.", 0),
        ("Deflake GPU tests by removing real-time sleeps; use a virtual clock to prevent timeouts.", 0),
    ]

    NEAR_MISS_NEGS = [
        # Pure feature without upkeep intent
        ("Introduces ReorderableListView.separated constructor (new API).", -1),
        ("Adds weekType parameter to CupertinoDatePicker to control selectable days (feature).", -1),
        ("Widget previewer filters previews by active editor location; includes UI changes (feature).", -1),

        # Process/social only
        ("Thanks! I'll merge after CI.", -1),
        ("Please rebase on main.", -1),

        # Issue mention without maintenance intent
        ("Related to #173838", -1),
    ]

    def fewshot_block(self, examples):
        return "\n\n".join([f"Comment: {t}\nLabel: {y}" for t, y in examples])

    def classify_code_text(self, raw_text):
        if raw_text == None:
            return GlueWorkType.UNKNOWN

        cleaned = self.clean(raw_text)

        # RULE 1 — short text
        if self.rule_based_short_text(cleaned):
            return GlueWorkType.UNKNOWN

        # RULE 2 — strong maintenance regex
        if self.rule_based_maintenance(cleaned):
            return GlueWorkType.MAINTENANCE

        # LLM classification
        return self.classify_data(self.get_maintenance_prompt(cleaned), self.MAINTENANCE_SYSTEM_MSG, GlueWorkType.MAINTENANCE)

    def get_maintenance_prompt(self, text):
        return f"""
Few-shot examples:
{self.fewshot_block(self.POS_CUES + self.NEAR_MISS_NEGS)}

Comment to classify:
{text}
"""

class MentoringAgent(ClassifierAgent):
    MENTORING_SYSTEM_MSG = """
You are a precise classifier for GitHub code-review comments. Output ONLY a single token: 0 or -1. Never output 1.
Before classification:
1. Ignore any quoted text from previous messages (lines starting with '>').
2. Ignore sections that are clearly repeated from earlier in the same thread.
3. Only analyze the new, original content written by the commenter.
"""

    POS_CUES = [
        # reasoning / trade-off (existing)
        ("We should keep this fix in a central location so it's easier to maintain.", 0),
        # coordination but with rationale (existing)
        ("Let's apply this to both 4.7 and 4.8 so they stay consistent.", 0),
        # concise justification (existing)
        ("We cannot change the JSON format because other clients depend on it.", 0),
        # Process Teaching/RAG (NEW)
        ("Actually, we use labels to route PRs to the right sub-team for review. I applied one and reached out to the team to confirm.", 0),
        # Constructive Rejection (NEW)
        ("I'm going to close this PR for now since there are outstanding comments, just to get this off our PR review queue. Please re-open if you address the comments.", 0),
        # Setup/Maintenance Guidance (NEW)
        ("I suspect that this change requires me to update tests in the below files. Let me know if I need to change it or make any other changes.", 0),
    ]

    NEAR_MISS_NEGS = [
        # Simple admin/social (existing)
        ("Thanks for the PR! I'll look into merging it. What's the 3rd point?", -1),
        ("OK I am +1 for this then.", -1),
        ("Please rebase after #1515 merges.", -1),
        # Pure CI/Status Update (NEW)
        ("I checked the Google testing failures, they looked like flakes unrelated to your change. Rerunning", -1),
        # Request for Admin Explanation (NEW)
        ("is there a simple explanation you can add here that does not require you to dig into the code?", -1),
        # Administrative Rebase/Force (NEW)
        ("I hope it's okay to just re-apply this commit onto upstream master using cherry-pick and force-push the branch.", -1),
    ]

    def fewshot_block(self, examples):
        return "\n\n".join([f"Comment: {t}\nLabel: {y}" for t, y in examples])

    def classify_mentoring_text(self, raw_text):
        if raw_text == None:
            return GlueWorkType.UNKNOWN

        cleaned = self.clean(raw_text)

        if self.rule_based_short_text(cleaned):
            return GlueWorkType.UNKNOWN

        return self.classify_data(self.get_mentoring_prompt(cleaned), self.MENTORING_SYSTEM_MSG, GlueWorkType.MENTORING)

    def get_mentoring_prompt(self, text):
        return f"""
Few-shot examples:
{self.fewshot_block(self.POS_CUES + self.NEAR_MISS_NEGS)}

Comment to classify:
{text}
"""

class CommunityAgent(ClassifierAgent):
    COMMUNITY_SYSTEM_MSG = """

"""

    def __init__(self, aggregator):
        super().__init__(aggregator)

    def classify_community_text(self, raw_text):
        if raw_text == None:
            return GlueWorkType.UNKNOWN

        cleaned = self.clean(raw_text)

        if self.rule_based_short_text(cleaned):
            return GlueWorkType.UNKNOWN

        return self.classify_data(self.get_community_managment_prompt(cleaned), self.COMMUNITY_SYSTEM_MSG, GlueWorkType.COMMUNITY_MANAGMENT)

    def get_community_managment_prompt(self, text):
        return f"""
Comment to classify:
{text}
"""