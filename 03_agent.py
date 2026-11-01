"""
Agentic Organizational Audit - Proof of Concept

Flow:
  01_survey_questions.md + 02_survey_responses.md  ->  03_agent.py  ->  04_outputs/

Pipeline:
  1. Follow-up agent:  detects vague answers and generates targeted follow-up questions
  2. Mapping agent:    builds a team-level map of who works on what (teams, projects, collaboration)
  3. Diagnosis agent:  identifies strengths, weaknesses and recommendations, citing respondents as evidence

Usage:
  pip install anthropic
  export ANTHROPIC_API_KEY=...
  python3 03_agent.py
"""

import json
import pathlib
import anthropic

MODEL = "claude-sonnet-5-5"  # any capable LLM works; swap model name as needed
QUESTIONS_FILE = pathlib.Path("01_survey_questions.md")
RESPONSES_FILE = pathlib.Path("02_survey_responses.md")
OUTPUT_DIR = pathlib.Path("04_outputs")

client = anthropic.Anthropic()


def call_llm(system: str, user: str, max_tokens: int = 16000) -> str:
    """Single LLM call; returns only the text of the response.

    Newer models may return a 'thinking' block before the answer, so we
    collect the text blocks instead of assuming the first block is text.
    max_tokens is generous because thinking counts against it.
    """
    response = client.messages.create(
        model=MODEL,
        max_tokens=max_tokens,
        system=system,
        messages=[{"role": "user", "content": user}],
    )
    text = "".join(block.text for block in response.content if block.type == "text")
    if response.stop_reason == "max_tokens":
        raise RuntimeError("Model hit max_tokens before finishing; raise max_tokens in call_llm.")
    if not text.strip():
        raise RuntimeError("Model returned no text output.")
    return text


def parse_json(raw: str) -> dict:
    """Parse JSON, tolerating code fences or extra text around the object."""
    text = raw.strip()
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end == -1:
        raise ValueError(f"No JSON object found in model output:\n{raw[:500]}")
    return json.loads(text[start:end + 1])


# ---------------------------------------------------------------------------
# Step 1: Follow-up agent
# ---------------------------------------------------------------------------
FOLLOWUP_SYSTEM = """You are an organizational interviewer.
You review employee survey answers and identify answers that are too vague
to understand what the person actually does (e.g. "various stuff", "depends").
For each vague respondent, write 2-3 short, friendly, specific follow-up questions
that would make their role and work concrete. Do not judge the person.

Return JSON only:
{"followups": [{"respondent": "R..", "reason": "...", "questions": ["...", "..."]}]}"""


def run_followup_agent(survey: str) -> dict:
    return parse_json(call_llm(FOLLOWUP_SYSTEM, survey))


# ---------------------------------------------------------------------------
# Step 2: Mapping agent
# ---------------------------------------------------------------------------
MAPPING_SYSTEM = """You are an organizational analyst.
From employee survey answers, build a factual map of the organization at TEAM level.
Only use information stated in the answers. Do not invent people, teams or projects.

Return JSON only:
{
  "teams": [{"name": "...", "headcount_in_sample": 0, "main_activities": ["..."]}],
  "projects": [{"name": "...", "lead": "R.. or unknown", "teams_involved": ["..."], "respondents": ["R.."]}],
  "collaboration": [{"from_team": "...", "to_team": "...", "reason": "..."}],
  "single_points_of_dependency": [{"respondent": "R..", "what_depends_on_them": "...", "evidence": ["R.."]}]
}"""


def run_mapping_agent(survey: str) -> dict:
    return parse_json(call_llm(MAPPING_SYSTEM, survey))


# ---------------------------------------------------------------------------
# Step 3: Diagnosis agent
# ---------------------------------------------------------------------------
DIAGNOSIS_SYSTEM = """You are an experienced organizational consultant.
You receive (a) raw employee survey answers and (b) a structured org map.
Identify the organization's main strengths and weaknesses and give recommendations.

Rules:
- Every finding must cite the respondents it is based on (e.g. R01, R04).
- Distinguish clearly between evidence and interpretation.
- Give 3-4 strengths, 3-4 weaknesses, and 3 prioritized recommendations.
- Write in clear, concise English as a short Markdown report for the internal strategy team."""


def run_diagnosis_agent(survey: str, org_map: dict) -> str:
    user = (
        survey +
        "\n\n## Org map (from mapping agent)\n\n" + json.dumps(org_map, indent=2)
    )
    return call_llm(DIAGNOSIS_SYSTEM, user)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> None:
    survey = (
        QUESTIONS_FILE.read_text(encoding="utf-8")
        + "\n\n"
        + RESPONSES_FILE.read_text(encoding="utf-8")
    )
    OUTPUT_DIR.mkdir(exist_ok=True)

    print("Step 1/3: follow-up questions ...")
    followups = run_followup_agent(survey)
    (OUTPUT_DIR / "01_followups.json").write_text(json.dumps(followups, indent=2), encoding="utf-8")

    print("Step 2/3: org map ...")
    org_map = run_mapping_agent(survey)
    (OUTPUT_DIR / "02_org_map.json").write_text(json.dumps(org_map, indent=2), encoding="utf-8")

    print("Step 3/3: diagnosis ...")
    report = run_diagnosis_agent(survey, org_map)
    (OUTPUT_DIR / "03_diagnosis.md").write_text(report, encoding="utf-8")

    print(f"Done. Outputs written to {OUTPUT_DIR.resolve()}")


if __name__ == "__main__":
    main()
