"""Run Admin GraphQL through `bunx shopify store execute` (shared by the setup scripts). --dry-run skips mutations."""
import json, os, subprocess, sys
from pathlib import Path

root = Path(__file__).resolve().parent.parent
STORE = "embrae-yaf7tdei.myshopify.com"
DRY = "--dry-run" in sys.argv
env = dict(os.environ, OPT_OUT_INSTRUMENTATION="true")


def gql(query, variables=None, mutation=False):
    if DRY and mutation:
        print("DRY", query.split("(")[0].split()[-1], json.dumps(variables)[:160]); return {}
    cmd = ["bunx", "shopify", "store", "execute", "-s", STORE, "--no-input", "-q", query]
    if variables is not None: cmd += ["-v", json.dumps(variables)]
    if mutation: cmd.append("--allow-mutations")
    r = subprocess.run(cmd, cwd=root, env=env, capture_output=True, text=True)
    if r.returncode: sys.exit(f"GraphQL failed:\n{r.stdout}\n{r.stderr}")
    return json.loads(r.stdout[r.stdout.find("{"):])


def check(payload, ok_codes=()):
    errs = [e for e in payload.get("userErrors", []) if e.get("code") not in ok_codes]
    if errs: sys.exit(f"userErrors: {errs}")
