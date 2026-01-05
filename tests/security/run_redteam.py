import yaml
import json
import os
import argparse
from typing import List, Dict
from langgraph.agents.verifier import PolicyEngine, OutputVerifier

def load_corpus(corpus_dir: str) -> List[Dict]:
    corpus = []
    for filename in os.listdir(corpus_dir):
        if filename.endswith(".yaml") or filename.endswith(".yml"):
            with open(os.path.join(corpus_dir, filename), 'r') as f:
                data = yaml.safe_load(f)
                if isinstance(data, list):
                    corpus.extend(data)
    return corpus

def run_redteam(corpus_dir: str, output_file: str):
    corpus = load_corpus(corpus_dir)
    engine = PolicyEngine()
    verifier = OutputVerifier(engine)
    
    results = []
    passed = 0
    total = 0
    
    for case in corpus:
        total += 1
        # Simulate the model outputting the payload (worst case)
        # or the prompt being the payload.
        # Here we test if the verifier catches the payload.
        verdict = verifier.verify(case["payload"], [])
        
        # Check if the verdict matches expectation
        # Note: In our corpus, "expected_verdict: FAIL" means we expect the system to BLOCK it.
        # The verifier returns "FAIL" if it blocks.
        # So if verifier returns "FAIL" and expected is "FAIL", that's a SUCCESS for the test.
        
        test_passed = (verdict["verdict"] == case["expected_verdict"])
        if test_passed:
            passed += 1
            
        results.append({
            "id": case["id"],
            "payload": case["payload"],
            "expected": case["expected_verdict"],
            "actual": verdict["verdict"],
            "test_passed": test_passed
        })
        
    with open(output_file, 'w') as f:
        json.dump({"summary": {"total": total, "passed": passed, "rate": passed/total if total else 0}, "details": results}, f, indent=2)
        
    print(f"Red Team Run Complete. Passed: {passed}/{total} ({passed/total:.2%})")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--corpus", default="tests/security/corpus")
    parser.add_argument("--results", default="redteam_results.json")
    args = parser.parse_args()
    
    run_redteam(args.corpus, args.results)
