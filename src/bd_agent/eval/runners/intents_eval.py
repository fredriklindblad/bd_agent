"""Module is eval of intents classifier"""


@dataclass

# TODO delete TESTONLY
def run_intents_eval():
    data = load_default_intents()
    out_path = ensure_artifacts_dir(get_artifacts_dir()) / "probe.jsonl"
    write_jsonl(out_path, data[:2])
