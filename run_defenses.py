"""Phase 5 — measure each defense layer ALONE and COMBINED.

Measuring layers in isolation is what makes the story rigorous:
"input sanitization alone cut ASR to X%; prompt hardening alone to Y%; all three
together to Z%" shows you understand defense in depth — far stronger than one number.
Change one thing at a time so every delta is attributable.
"""
from run_benchmark import run
from target_agent import BASE_SYSTEM, HARDENED_SYSTEM
from defenses import sanitize_input, scrub_output

if __name__ == "__main__":
    run(BASE_SYSTEM, label="baseline")                                       # no defense
    run(BASE_SYSTEM, label="input_only", input_defense=sanitize_input)       # Layer 1 alone
    run(HARDENED_SYSTEM, label="hardened_only")                              # Layer 2 alone
    run(BASE_SYSTEM, label="output_only", output_defense=scrub_output)       # Layer 3 alone
    run(HARDENED_SYSTEM, label="defended",                                   # all three combined
        input_defense=sanitize_input, output_defense=scrub_output)
