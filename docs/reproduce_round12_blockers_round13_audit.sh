#!/usr/bin/env bash
set -uo pipefail
REPO="${1:?repo checkout}"
CAL="${2:?calibration json}"
PY="${PYTHON:-python}"
TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
REPO="$(cd "$REPO" && pwd)"; CAL="$(cd "$(dirname "$CAL")" && pwd)/$(basename "$CAL")"
CAL_SHA="$(sha256sum "$CAL" | awk '{print $1}')"
COMMON=("$REPO/src/mde_sim.py" --mode curve --family p1p2 --theta-grid 0.0:0.0:1.0 --reps 2 --B 19 --sigma-delta 0.1 --calib-json "$CAL")
(
 cd "$REPO"
 "$PY" "${COMMON[@]}" >"$TMP/no_hash.out" 2>"$TMP/no_hash.err"
); R_NO=$?
(
 cd "$REPO"
 "$PY" "${COMMON[@]}" --calib-expected-sha256 "$CAL_SHA" >"$TMP/hash.out" 2>"$TMP/hash.err"
); R_HASH=$?
printf 'A1 no_hash_rc=%s correct_hash_rc=%s\n' "$R_NO" "$R_HASH"
printf 'A1 no_hash_stderr=%s\n' "$(tr '\n' ' ' < "$TMP/no_hash.err")"
printf 'A1 correct_hash_verified_lines=%s\n' "$(grep -cF "calibration artifact sha256 verified: $CAL_SHA" "$TMP/hash.out" || true)"
printf 'A1 correct_hash_nested_lines=%s\n' "$(grep -cF 'curve decision engine: full_nested_pass_p' "$TMP/hash.out" || true)"
if [[ "$R_NO" -ne 0 && "$R_HASH" -eq 0 ]] && grep -qF -- '--calib-expected-sha256' "$TMP/no_hash.err" && grep -qF "calibration artifact sha256 verified: $CAL_SHA" "$TMP/hash.out" && grep -qF 'curve decision engine: full_nested_pass_p' "$TMP/hash.out"; then
  echo 'A1 NOT REPRODUCED'
else
  echo 'A1 REPRODUCED/INCONCLUSIVE'
fi

BROKEN="$TMP/schema_broken_false.json"
"$PY" - "$CAL" "$BROKEN" <<'PY'
import json, sys
src,dst=sys.argv[1:]
d=json.load(open(src,encoding='utf-8'))
d['calibration_ok']=False
d['surprise']=1
d['binding']['years']=[1994,1994]
open(dst,'w',encoding='utf-8').write(json.dumps(d,sort_keys=True))
PY
BROKEN_SHA="$(sha256sum "$BROKEN" | awk '{print $1}')"
(
 cd "$REPO"
 "$PY" "$REPO/src/mde_sim.py" --mode curve --family p1p2 --theta-grid 0.0:0.0:1.0 --reps 2 --B 19 --sigma-delta 0.1 --calib-json "$BROKEN" --calib-expected-sha256 "$BROKEN_SHA" >"$TMP/broken.out" 2>"$TMP/broken.err"
); R_BROKEN=$?
printf 'A2 broken_rc=%s\n' "$R_BROKEN"
printf 'A2 broken_stderr=%s\n' "$(tr '\n' ' ' < "$TMP/broken.err")"
printf 'A2 verified_lines=%s\n' "$(grep -cF 'calibration artifact sha256 verified:' "$TMP/broken.out" || true)"
if [[ "$R_BROKEN" -ne 0 ]] && grep -qF 'calibration schema' "$TMP/broken.err" && ! grep -qF 'calibration artifact sha256 verified:' "$TMP/broken.out"; then
  echo 'A2 NOT REPRODUCED'
else
  echo 'A2 REPRODUCED/INCONCLUSIVE'
fi

PYTHONPATH="$REPO/src" "$PY" - <<'PY'
import json
import s01_fetch_metadata as s01
CFG={'api': {'base_url':'http://fixture','rows_per_page':5,'format':'json','lang_exact':'English','fields':['id'],'max_retries':1,'timeout':1,'backoff_base':0,'sleep_seconds':0}}
base={'docty':'X','count':'5','display_title':'A','docdt':'2024-01-01T00:00:00Z','repnb':'R1','volnb':'1'}
class Response:
    status_code=200
    def __init__(self,docs):
        self.payload={'total':len(docs),'documents':{f'D{i}':d for i,d in enumerate(docs)}}
        self.content=json.dumps(self.payload).encode()
    def json(self): return self.payload
class Session:
    def __init__(self,docs): self.docs=docs
    def get(self,*a,**kw): return Response(self.docs)
for label,ids in [('int-vs-string',[1,'1']),('trim-variant',['1',' 1 '])]:
    docs=[dict(base,id=x) for x in ids]
    try:
        rows=s01.fetch_stratum_year(Session(docs),CFG,['X'],2024)
        print(f'B {label} ACCEPTED {rows!r}')
    except Exception as e:
        print(f'B {label} REJECTED {type(e).__name__}: {e}')
PY
