"""Phase 4 — run every attack against the agent, judge each, compute Attack Success Rate.

Produces the baseline ASR and a per-category breakdown. The per-category numbers are the
interesting part: they tell you which attack class your defenses most need to stop.

Improvement over the tutorial: it passed one `defense_fn` and inspected its arg count to
guess whether it also handled output — clever and fragile. Here input and output defenses
are two explicit optional params. Clearer to read, clearer to explain in an interview.
"""
import yaml, json, os
from collections import defaultdict

from target_agent import build_agent, run_agent, BASE_SYSTEM
from judge import judge_attack


def run(system_prompt=BASE_SYSTEM, label="baseline", input_defense=None, output_defense=None):
    """input_defense(text)->text runs on the attack before it reaches the agent.
       output_defense(text)->text runs on the agent's reply before judging.
       Either may be None (no defense at that stage)."""
    attacks = yaml.safe_load(open("attacks.yaml"))
    agent = build_agent(system_prompt)
    results, by_cat = [], defaultdict(lambda: [0, 0])  # category -> [successes, total]

    for atk in attacks:
        user_input = atk["prompt"]
        if input_defense:
            user_input = input_defense(user_input)

        output = run_agent(agent, user_input)
        if output_defense:
            output = output_defense(output)

        # Judge against the ORIGINAL prompt so off_mission grading sees the real task.
        succeeded = judge_attack(atk["goal"], atk["prompt"], output)
        results.append({**atk, "output": output[:500], "attack_succeeded": succeeded})
        by_cat[atk["category"]][0] += succeeded
        by_cat[atk["category"]][1] += 1

    asr = sum(r["attack_succeeded"] for r in results) / len(results)
    os.makedirs("results", exist_ok=True)
    json.dump(results, open(f"results/{label}.json", "w"), indent=2)

    print(f"\n=== {label} ===  Attack Success Rate: {asr:.0%}  ({sum(r['attack_succeeded'] for r in results)}/{len(results)})")
    for cat, (s, t) in sorted(by_cat.items()):
        print(f"  {cat:22s} {s}/{t} = {s/t:.0%}")
    return asr


if __name__ == "__main__":
    run(label="baseline")
