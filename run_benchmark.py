"""Phase 4 — run every attack against the agent, judge each, compute Attack Success Rate.

Produces the baseline ASR and a per-category breakdown. The per-category numbers are the
interesting part: they tell you which attack class your defenses most need to stop.

Improvement over the tutorial: it passed one `defense_fn` and inspected its arg count to
guess whether it also handled output — clever and fragile. Here input and output defenses
are two explicit optional params. Clearer to read, clearer to explain in an interview.
"""
import yaml, json, os, time
from collections import defaultdict

from target_agent import build_agent, run_agent, BASE_SYSTEM
from judge import judge_attack

# Free-tier resilience: the public Gemini endpoint throttles (429) and occasionally returns
# a transient 503. Without this, one bad call would abort the whole 42-attack run. Retry each
# call with backoff, and pace requests to stay under the free-tier per-minute limit.
PACE_SECONDS = 4        # gap between attacks (~15 requests/min)
MAX_TRIES = 5


def _resilient_run(agent, text):
    """Run one attack, retrying transient rate-limit/overload errors. Returns (output, errored)."""
    for attempt in range(MAX_TRIES):
        try:
            return run_agent(agent, text), False
        except Exception as e:
            transient = any(code in str(e) for code in ("429", "503", "RESOURCE_EXHAUSTED", "UNAVAILABLE"))
            if not transient or attempt == MAX_TRIES - 1:
                return f"[agent error: {e}]", True
            time.sleep(15 * (attempt + 1))  # linear backoff: 15s, 30s, 45s, ...
    return "[agent error: retries exhausted]", True


def run(system_prompt=BASE_SYSTEM, label="baseline", input_defense=None, output_defense=None,
        sample_per_category=None):
    """input_defense(text)->text runs on the attack before it reaches the agent.
       output_defense(text)->text runs on the agent's reply before judging.
       Either may be None (no defense at that stage).
       sample_per_category=N runs only the first N attacks of each category (a quick smoke
       run for rate-limited free tiers); None runs the full suite."""
    attacks = yaml.safe_load(open("attacks.yaml"))
    if sample_per_category:
        seen, picked = defaultdict(int), []
        for a in attacks:
            if seen[a["category"]] < sample_per_category:
                picked.append(a)
                seen[a["category"]] += 1
        attacks = picked
    agent = build_agent(system_prompt)
    results, by_cat = [], defaultdict(lambda: [0, 0])  # category -> [successes, total]

    errored = 0
    for atk in attacks:
        user_input = atk["prompt"]
        if input_defense:
            user_input = input_defense(user_input)

        output, failed = _resilient_run(agent, user_input)
        if failed:
            errored += 1
        if output_defense:
            output = output_defense(output)

        # Judge against the ORIGINAL prompt so off_mission grading sees the real task.
        succeeded = judge_attack(atk["goal"], atk["prompt"], output)
        results.append({**atk, "output": output[:500], "attack_succeeded": succeeded})
        by_cat[atk["category"]][0] += succeeded
        by_cat[atk["category"]][1] += 1
        time.sleep(PACE_SECONDS)

    asr = sum(r["attack_succeeded"] for r in results) / len(results)
    os.makedirs("results", exist_ok=True)
    json.dump(results, open(f"results/{label}.json", "w"), indent=2)

    print(f"\n=== {label} ===  Attack Success Rate: {asr:.0%}  ({sum(r['attack_succeeded'] for r in results)}/{len(results)})")
    for cat, (s, t) in sorted(by_cat.items()):
        print(f"  {cat:22s} {s}/{t} = {s/t:.0%}")
    if errored:
        print(f"  (warning: {errored}/{len(results)} attacks errored after retries and count as not-succeeded)")
    return asr


if __name__ == "__main__":
    run(label="baseline")
