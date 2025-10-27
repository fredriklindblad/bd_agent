#TODO short README.
how to run intent eval and generative eval
where is golden set and generative set
how to add new cases

how eval works:
- cases are stored in golden_intents.jsonl in /reference sets
- run generate_synthetic_intents to get more examples.
- run intents_eval that runs the intents_classfier on all refenerce files.
    it calcualtes metrics through /metrics.classificaiton.py file
    and stores to /artifacts.intent_report.json

