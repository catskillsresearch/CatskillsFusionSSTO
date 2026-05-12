# Orbitron-TestStand → FlightGear under ./Aircraft (incremental).
#
# Usage (repo root):
#   make help
#   make                    # default: full WarpX surrogate sweep (slow) + mesh + sounds
#   make SURROGATE=mesh     # fast: placeholder surrogate, still runs CadQuery + Blender
#   make SURROGATE=dry      # yt/CSV fit without pywarpx
#   make graph              # Mermaid dependency chart for mermaid.live
#   make run-fgfs           # launch fgfs against ./Aircraft
#
# WarpX + pywarpx: set PYTHONPATH/LD_LIBRARY_PATH (see ./stand.sh) or use:
#   ./stand.sh
#
# Optional passthrough to build_surrogate_map.py (warpx/dry only):
#   make WARPX_MAKE_ARGS='--steps 600 --diag-period 100 --grid 4'

REPO_ROOT := $(abspath .)
ORBITRON := $(REPO_ROOT)/ssto/orbitron
AIRCRAFT := $(REPO_ROOT)/Aircraft
STAND := $(AIRCRAFT)/Orbitron-TestStand
BUILD := $(REPO_ROOT)/build/orbitron

POETRY ?= poetry
BLENDER ?= blender
SURROGATE ?= warpx
GRID ?= 4

export ORBITRON_AC_OUT := $(STAND)/Models/orbitron.ac

WARPX_MAKE_ARGS ?=

STAND_SRC_FILES := $(shell find $(ORBITRON)/Orbitron-TestStand -type f \
	'!' -path '*/Models/orbitron.ac' \
	'!' -name 'engine_surrogate.json' \
	'!' -name '*.wav' 2>/dev/null)

SUR_DEP_ALL := \
	$(REPO_ROOT)/tools/build_surrogate_map.py \
	$(REPO_ROOT)/tools/warpx_to_jsbsim_surrogate.py \
	$(ORBITRON)/laminar_flow_2d_arcjet.py

MERMAID_OUT := $(STAND)/build/dependency_graph.mmd

.PHONY: all help clean graph run-fgfs fg-ready

all: fg-ready

help:
	@echo "Orbitron-TestStand Makefile"
	@echo "  make / make all     Build $(STAND) (default SURROGATE=$(SURROGATE))"
	@echo "  SURROGATE=warpx|dry|mesh   Surrogate source (warpx is slow)"
	@echo "  make graph          Write $(MERMAID_OUT)"
	@echo "  make run-fgfs       fgfs with --fg-aircraft=$(AIRCRAFT)"
	@echo "  make clean          Remove $(AIRCRAFT) and $(BUILD) (not all of ./build if other projects use it)"
	@echo "  Tip: after rm -rf build, either make clean or rm Aircraft/Orbitron-TestStand/.dirs so .dirs is recreated."
	@echo "Use ./stand.sh for Poetry + WarpX library paths, then make."

fg-ready: \
	$(STAND)/.dirs \
	$(STAND)/.static_synced \
	$(ORBITRON)/orbitron_lab_v5.gltf \
	$(ORBITRON)/arcjet_outdoor_stand.gltf \
	$(STAND)/.orbitron_ac_done \
	$(STAND)/engine_surrogate.json \
	$(STAND)/Sounds/orbitron_core_loop.wav \
	$(STAND)/build/orbitron_lab_v5.gltf \
	$(STAND)/build/arcjet_outdoor_stand.gltf \
	$(STAND)/build/surrogate_sweep_results.csv

$(STAND)/.dirs:
	mkdir -p $(STAND)/Models $(STAND)/Nasal $(STAND)/Sounds $(STAND)/build $(BUILD)/warpx-runs
	touch $@

# Ensures build/orbitron exists if someone removed ./build but kept Aircraft/.dirs (stale stamp).
$(BUILD)/warpx-runs:
	mkdir -p '$(BUILD)' '$(BUILD)/warpx-runs'

$(STAND)/.static_synced: $(STAND_SRC_FILES) | $(STAND)/.dirs
	rsync -a --exclude='Models/orbitron.ac' --exclude='engine_surrogate.json' --exclude='*.wav' \
		$(ORBITRON)/Orbitron-TestStand/ $(STAND)/
	touch $@

$(ORBITRON)/orbitron_lab_v5.gltf: $(ORBITRON)/full_reactor_cad.py | $(STAND)/.dirs
	cd $(ORBITRON) && $(POETRY) run python full_reactor_cad.py

$(ORBITRON)/arcjet_outdoor_stand.gltf: $(ORBITRON)/arcjet_test_stand_cad.py | $(STAND)/.dirs
	cd $(ORBITRON) && $(POETRY) run python arcjet_test_stand_cad.py

$(STAND)/.orbitron_ac_done: \
		$(ORBITRON)/orbitron_lab_v5.gltf \
		$(ORBITRON)/build_ac3d.py \
		$(ORBITRON)/fix_screen_uv.py \
		| $(STAND)/.dirs $(STAND)/.static_synced
	rm -f '$(STAND)/Models/orbitron.ac'
	cd $(ORBITRON) && ORBITRON_AC_OUT='$(STAND)/Models/orbitron.ac' $(BLENDER) -b --python build_ac3d.py
	test -f '$(STAND)/Models/orbitron.ac'
	cd $(ORBITRON) && ORBITRON_AC_OUT='$(STAND)/Models/orbitron.ac' $(POETRY) run python fix_screen_uv.py
	touch $@

$(STAND)/engine_surrogate.json: $(SUR_DEP_ALL) $(BUILD)/warpx-runs | $(STAND)/.dirs
	@if [ "$(SURROGATE)" = "warpx" ]; then \
		echo "=== surrogate: WarpX sweep (SURROGATE=warpx) ==="; \
		cd $(REPO_ROOT) && $(POETRY) run python tools/build_surrogate_map.py \
			--work-dir '$(BUILD)/warpx-runs' \
			--out-csv '$(BUILD)/surrogate_sweep_results.csv' \
			--out-json '$(STAND)/engine_surrogate.json' \
			$(WARPX_MAKE_ARGS); \
	elif [ "$(SURROGATE)" = "dry" ]; then \
		echo "=== surrogate: dry-run (SURROGATE=dry) ==="; \
		cd $(REPO_ROOT) && $(POETRY) run python tools/build_surrogate_map.py --dry-run --grid $(GRID) \
			--work-dir '$(BUILD)/warpx-runs' \
			--out-csv '$(BUILD)/surrogate_sweep_results.csv' \
			--out-json '$(STAND)/engine_surrogate.json' \
			$(WARPX_MAKE_ARGS); \
	else \
		echo "=== surrogate: placeholder JSON (SURROGATE=mesh) ==="; \
		cd $(REPO_ROOT) && $(POETRY) run python tools/warpx_to_jsbsim_surrogate.py \
			--placeholder --out-json '$(STAND)/engine_surrogate.json'; \
		mkdir -p '$(BUILD)'; \
		printf 'throttle,compressor\n0,0\n' > '$(BUILD)/surrogate_sweep_results.csv'; \
	fi

$(STAND)/Sounds/orbitron_core_loop.wav: \
		$(ORBITRON)/add_reactor_sound.py \
		$(ORBITRON)/Orbitron-TestStand/Sounds/sound.xml \
		| $(STAND)/.dirs $(STAND)/.static_synced
	$(POETRY) run python $(ORBITRON)/add_reactor_sound.py --out-dir '$(STAND)/Sounds'

$(STAND)/build/orbitron_lab_v5.gltf: $(ORBITRON)/orbitron_lab_v5.gltf | $(STAND)/.dirs
	mkdir -p $(STAND)/build
	cp -f '$<' '$@'

$(STAND)/build/arcjet_outdoor_stand.gltf: $(ORBITRON)/arcjet_outdoor_stand.gltf | $(STAND)/.dirs
	mkdir -p $(STAND)/build
	cp -f '$<' '$@'

# Mirror CSV beside surrogate JSON (also under build/orbitron for WarpX/dry).
$(STAND)/build/surrogate_sweep_results.csv: $(STAND)/engine_surrogate.json | $(STAND)/.dirs
	mkdir -p '$(STAND)/build'
	cp -f '$(BUILD)/surrogate_sweep_results.csv' '$@'

graph: | $(STAND)/.dirs
	mkdir -p $(STAND)/build
	@{ \
	echo '%% Auto-generated by `make graph`. Paste into https://mermaid.live'; \
	echo 'flowchart TD'; \
	echo '  subgraph sources["Source repo"]'; \
	echo '    lab_cad["ssto/orbitron/full_reactor_cad.py"]'; \
	echo '    arc_cad["ssto/orbitron/arcjet_test_stand_cad.py"]'; \
	echo '    blend["ssto/orbitron/build_ac3d.py"]'; \
	echo '    uv["ssto/orbitron/fix_screen_uv.py"]'; \
	echo '    pic["ssto/orbitron/laminar_flow_2d_arcjet.py"]'; \
	echo '    smap["tools/build_surrogate_map.py"]'; \
	echo '    wfit["tools/warpx_to_jsbsim_surrogate.py"]'; \
	echo '    snd["ssto/orbitron/add_reactor_sound.py"]'; \
	echo '    static["Orbitron-TestStand/* (excl. generated)"]'; \
	echo '  end'; \
	echo '  subgraph inter["Aircraft/Orbitron-TestStand/build + build/orbitron"]'; \
	echo '    gltf_lab["build/orbitron_lab_v5.gltf (copy)"]'; \
	echo '    gltf_arc["build/arcjet_outdoor_stand.gltf (copy)"]'; \
	echo '    csv["surrogate_sweep_results.csv"]'; \
	echo '    warpx_runs["warpx-runs/*"]'; \
	echo '  end'; \
	echo '  subgraph fg["Aircraft/Orbitron-TestStand (FlightGear)"]'; \
	echo '    ac["Models/orbitron.ac"]'; \
	echo '    json["engine_surrogate.json"]'; \
	echo '    wavs["Sounds/*.wav"]'; \
	echo '    xml["*-set.xml, JSBSim, Nasal, sound.xml"]'; \
	echo '  end'; \
	echo '  lab_cad -->|CadQuery| gltf_src["orbitron_lab_v5.gltf"]'; \
	echo '  arc_cad -->|CadQuery| arc_src["arcjet_outdoor_stand.gltf"]'; \
	echo '  gltf_src --> blend'; \
	echo '  blend --> ac'; \
	echo '  uv --> ac'; \
	echo '  gltf_src --> gltf_lab'; \
	echo '  arc_src --> gltf_arc'; \
	echo '  pic --> smap'; \
	echo '  smap --> csv'; \
	echo '  smap --> warpx_runs'; \
	echo '  smap --> wfit'; \
	echo '  wfit --> json'; \
	echo '  static --> xml'; \
	echo '  snd --> wavs'; \
	echo '  xml --> fgpack["fg-ready"]'; \
	echo '  ac --> fgpack'; \
	echo '  json --> fgpack'; \
	echo '  wavs --> fgpack'; \
	echo '  gltf_lab --> fgpack'; \
	echo '  gltf_arc --> fgpack'; \
	echo '  csv --> fgpack'; \
	} > '$(MERMAID_OUT)'
	@echo "Wrote $(MERMAID_OUT)"

run-fgfs: fg-ready
	cd $(REPO_ROOT) && fgfs --fg-aircraft=$(AIRCRAFT) --aircraft=Orbitron-TestStand \
		--airport=BIKF --parkpos=East-Apron-119 --timeofday=noon --ai-traffic=0 \
		--real-weather-fetch=0 --clouds3d=0 \
		--prop:/sim/sound/chatter/volume=0.0 --prop:/sim/sound/atc/volume=0.0 \
		--prop:/instrumentation/comm/volume=0.0

clean:
	rm -rf '$(AIRCRAFT)' '$(BUILD)'
