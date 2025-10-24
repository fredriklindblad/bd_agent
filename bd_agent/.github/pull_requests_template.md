## What
- Add `bd_agent/evals` with runners and metrics
- Intent eval uses golden set (100 rows)
- Generative eval uses rubric-based scoring

## Why
- Establish baseline metrics and repeatable evals before further features

## How to test
```bash
pytest -q
python -m bd_agent.evals.runners.intent_eval
python -m bd_agent.evals.runners.generative_eval
