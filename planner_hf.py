import os
import re
import requests

HF_ROUTER_CHAT_URL = "https://router.huggingface.co/v1/chat/completions"

def _hf_token() -> str:
    token = (os.getenv("HF_TOKEN") or "").strip()
    if not token:
        raise RuntimeError("HF_TOKEN is missing. Add it to .env (local) or Streamlit Secrets (cloud).")
    return token

def _call_hf_chat(model: str, messages, temperature: float = 0.2, max_tokens: int = 900) -> str:
    headers = {
        "Authorization": f"Bearer {_hf_token()}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    r = requests.post(HF_ROUTER_CHAT_URL, headers=headers, json=payload, timeout=60)
    if r.status_code != 200:
        raise RuntimeError(f"HF router error {r.status_code}: {r.text[:250]}")
    data = r.json()
    return data["choices"][0]["message"]["content"].strip()

def _parse_week_plan(text: str):
    """
    Parse format:
    WEEK 1: <milestone>
    - <subtopic 1>
    - <subtopic 2>
    ...
    WEEK 2: <milestone>
    - ...
    """
    weeks = []
    # Split by WEEK blocks
    blocks = re.split(r"\bWEEK\s+(\d+)\s*:\s*", text, flags=re.IGNORECASE)
    # blocks looks like: ["", "1", "milestone...\n- a\n- b", "2", "milestone...\n- ..."]
    if len(blocks) < 3:
        return []

    i = 1
    while i < len(blocks) - 1:
        week_no = int(blocks[i])
        body = blocks[i + 1].strip()

        # milestone is first line
        lines = [ln.strip() for ln in body.splitlines() if ln.strip()]
        if not lines:
            i += 2
            continue

        milestone = lines[0]
        subtopics = []

        for ln in lines[1:]:
            m = re.match(r"^[-•]\s*(.+)$", ln)
            if m:
                subtopics.append(m.group(1).strip())

        # If bullet list missing, try comma-separated line(s)
        if not subtopics:
            # take remaining lines and split by comma
            rest = " ".join(lines[1:])
            parts = [p.strip() for p in rest.split(",") if p.strip()]
            subtopics.extend(parts[:7])

        # Enforce size
        subtopics = [s for s in subtopics if len(s) > 2][:7]

        if milestone and subtopics:
            weeks.append({
                "week_no": week_no,
                "milestone": milestone,
                "subtopics": subtopics
            })

        i += 2

    return weeks

def generate_plan_hf(goal, duration_days, hours_per_week, intensity, learning_pref):
    """
    Reliable approach:
    - Ask HF for week-wise milestones + bullet subtopics (NOT JSON)
    - Parse the text deterministically
    - Return in {"weeks":[...]} format for your app
    """
    # Better JSON/structure-following models (try these first)
    # If one fails on your token/provider, swap in .env using HF_MODEL
    default_model = "mistralai/Mistral-7B-Instruct-v0.3:fastest"
    model = (os.getenv("HF_MODEL") or default_model).strip()

    weeks_count = max(1, (int(duration_days) + 6) // 7)

    user_prompt = f"""
Create a topic-specific study plan for: {goal}
Duration: {duration_days} days (~{weeks_count} weeks)
Intensity: {intensity}
Preference: {learning_pref}

Return in EXACT TEXT FORMAT (no JSON, no markdown fences):

WEEK 1: <milestone>
- <subtopic 1>
- <subtopic 2>
- <subtopic 3>
- <subtopic 4>
- <subtopic 5>

WEEK 2: <milestone>
- ...

Rules:
- Make subtopics syllabus-like and specific to the goal (real units/topics).
- For Indian History, include Ancient/Medieval/Modern style units and key events.
- Avoid generic labels like fundamentals/examples/FAQs/terminology.
- 5 to 7 subtopics per week.
- Final week must include Revision, Mock Practice, Error Analysis.
"""

    messages = [
        {"role": "system", "content": "You are a study planner. Follow the output format exactly."},
        {"role": "user", "content": user_prompt},
    ]

    text = _call_hf_chat(model, messages, temperature=0.2, max_tokens=1100)

    weeks = _parse_week_plan(text)

    if not weeks:
        raise ValueError("Could not parse week plan from model output.")

    # Ensure we have all weeks; if model returned fewer, still return whatever parsed
    return {"weeks": weeks}
