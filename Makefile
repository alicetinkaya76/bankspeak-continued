PY=python
CFG=config/config.yaml

test:
	$(PY) -m pytest tests/ -q

facets:
	$(PY) src/s00_discover_facets.py --config $(CFG)

metadata:
	$(PY) src/s01_fetch_metadata.py --config $(CFG)

texts:
	$(PY) src/s02_download_texts.py --config $(CFG)

features:
	$(PY) src/s03_extract_text.py --config $(CFG)
	$(PY) src/s04_features_classic.py --config $(CFG)
	$(PY) src/s05_features_markers.py --config $(CFG)

power:
	$(PY) src/s07_power_analysis.py --config $(CFG)

its:
	$(PY) src/s08_its_analysis.py --config $(CFG)

.PHONY: test facets metadata texts features power its

# --- sprint-2 additions (2026-08-10; round-6 build plan) ---
selftest:
	$(PY) src/bootstrap_engine.py --selftest

smoke:
	$(PY) src/mde_sim.py --mode smoke --theta-grid 0.0:0.9:0.9 --sigma-delta 0.1

package:
	$(PY) tools/build_audit_package.py --out $(OUT)

.PHONY: selftest smoke package
