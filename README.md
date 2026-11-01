# Agentic Organizational Audit – Proof of Concept

**Can an agent understand an organization?** This repository is a minimal proof of concept for a master's thesis proposal at the ETH Zurich Agentic Systems Lab. It shows the core idea: unstructured employee survey answers go in, and an agentic pipeline turns them into a structured picture of the organization and a diagnosis of its strengths and weaknesses.

## The problem

Companies rarely know who actually works on what. Org charts show reporting lines, not real tasks, projects and dependencies. Organizational audits today rely on consultants running interviews by hand, which is slow, expensive and quickly outdated.

## Flow

Files are numbered in the order the pipeline uses them:

```
01_survey_questions.md   # The fixed questionnaire (5 questions)
02_survey_responses.md   # Answers of 12 fictional employees at "Alpenwerk AG"
03_agent.py              # The three-step agent pipeline with all prompts
04_outputs/
  01_followups.json      # Step 1: follow-up questions for vague answers
  02_org_map.json        # Step 2: team-level org map
  03_diagnosis.md        # Step 3: strengths, weaknesses, recommendations
```

## What the pipeline does

| Step | Agent | Input | Output |
|---|---|---|---|
| 1 | Follow-up agent | Questions + answers | Targeted follow-up questions for vague answers |
| 2 | Mapping agent | Questions + answers | Team-level org map: teams, projects, collaboration, single points of dependency |
| 3 | Diagnosis agent | Answers + org map | Report with strengths, weaknesses and recommendations, each citing the respondents it is based on |

## The simulated company

**Alpenwerk AG** is a fictional mid-sized Swiss manufacturer of industrial pumps with about 120 employees. The survey sample covers 12 employees, three each from Sales, Engineering, Production and Finance. Each answers the same five questions on role, tasks, projects, collaboration and blockers. All names and data are invented.

## The simulated problems (ground truth)

The answers were written to contain known organizational issues, so the output can be checked against them:

| # | Planted issue | Where it shows up |
|---|---|---|
| 1 | **Key-person bottleneck:** one senior engineer (Marco) answers most technical sales questions, which slows both quotes and the new P7 pump series | R01, R04, R05 |
| 2 | **Under-resourced project:** the ERP upgrade has no dedicated people; everyone works on it on top of their job | R07, R09, R10, R11, R12 |
| 3 | **Duplicated, inconsistent data:** customer data in both CRM and Excel; master data differs between Sales and Finance; outdated cost data | R02, R10, R11 |
| 4 | **Manual single-owner tool:** capacity planning lives in an Excel only one planner maintains | R03, R07 |
| 5 | **Weak handoffs:** late drawing changes to Production; duplicate small-part orders | R08, R09 |
| 6 | **Vague respondent:** one junior engineer gives unclear answers, to test the follow-up agent | R06 |

## Results

The pipeline ran end to end. Outputs are in `04_outputs/`:

- **Follow-ups:** the agent flagged only R06 as vague and generated three concrete follow-up questions (e.g. "what are two or three specific things you worked on last week").
- **Org map:** it reconstructed the 4 teams and 9 projects, mapped cross-team collaboration, and flagged three single points of dependency: the senior engineer (R04), the production planner with the capacity Excel (R07), and the Head of Finance holding three roles (R12).
- **Diagnosis:** 4 strengths, 4 weaknesses and 3 prioritized recommendations: relieve the engineering bottleneck, staff the ERP upgrade and fix data ownership, and formalize team handoffs and project governance.

## Evaluation

All six planted issues were found, and each finding cites the respondents it is based on. The agent did not invent people or projects, and it separated evidence from interpretation. It also stated its own limits unprompted: a small sample, missing teams (Management, Quality, Maintenance), and that "unknown project lead" may reflect the survey design rather than reality. It went beyond the planted issues by noting that the same few people (R10, R12) appear across several projects, a plausible overload signal.

This is a qualitative check on one synthetic case with a known answer, not a rigorous evaluation. Systematic evaluation against real organizations is part of the thesis.

## How to run

```bash
pip install anthropic
export ANTHROPIC_API_KEY=your_key
python3 03_agent.py
```

Outputs are written to `04_outputs/`.

## Scope and limitations

This is a demonstration, not an evaluation. The thesis would add:

- a real survey platform with AI-generated follow-up questions,
- systematic evaluation against ground truth (existing org charts, project lists, manager validation),
- the legal and privacy layer (consent, anonymity thresholds, GDPR and Swiss data protection law).

## Author

Jonas Stanicki – MSc Management, Technology and Economics, ETH Zurich
