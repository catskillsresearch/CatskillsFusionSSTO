# Orbitron-TestStand → FlightGear under ./Aircraft (incremental).
# All computed assets (glTF, .ac, WAV, surrogate JSON) live under Aircraft/ only;
# ssto/orbitron/Orbitron-TestStand/ holds source XML/Nasal/sound.xml only.

REPO_ROOT := $(abspath .)
ORBITRON := $(REPO_ROOT)/ssto/orbitron
AIRCRAFT := $(REPO_ROOT)/Aircraft
STAND := $(AIRCRAFT)/Orbitron-TestStand
BUILD := $(REPO_ROOT)/build/orbitron

# CadQuery / Blender / PIC inputs (sources)
GLTF_LAB := $(STAND)/build/orbitron_lab_v5.gltf
GLTF_ARC := $(STAND)/build/arcjet_outdoor_stand.gltf
FUSION_CAD := $(ORBITRON)/fusion_arcjet_engine_cad.py
LAB_CAD_SRC := $(ORBITRON)/full_reactor_cad.py $(FUSION_CAD)

POETRY ?= poetry
BLENDER ?= blender
SURROGATE ?= warpx
GRID ?= 4

export ORBITRON_AC_OUT := $(STAND)/Models/orbitron.ac

WARPX_MAKE_ARGS ?=

# Static aircraft sources only (no generated wav / .ac / surrogate in tree)
STAND_SRC_FILES := $(shell find $(ORBITRON)/Orbitron-TestStand -type f \
	'!' -path '*/Models/orbitron.ac' \
	'!' -name 'engine_surrogate.json' \
	'!' -name '*.wav' 2>/dev/null)

SUR_DEP_ALL := \
	$(REPO_ROOT)/tools/build_surrogate_map.py \
	$(REPO_ROOT)/tools/warpx_to_jsbsim_surrogate.py \
	$(ORBITRON)/laminar_flow_2d_arcjet.py

MERMAID_OUT := $(STAND)/build/dependency_graph.mmd

# Computed FlightGear model + audio (all under Aircraft/)
MODEL_ARTIFACTS := \
	$(GLTF_LAB) \
	$(GLTF_ARC) \
	$(STAND)/Models/orbitron.ac \
	$(STAND)/engine_surrogate.json \
	$(STAND)/Sounds/.sounds_built \
	$(STAND)/build/surrogate_sweep_results.csv

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
	@echo "  Sources: $(ORBITRON)/Orbitron-TestStand/ (XML, Nasal, sound.xml). Built model: $(MODEL_ARTIFACTS)"
	@echo "Use ./stand.sh for Poetry + WarpX library paths, then make."

fg-ready: $(STAND)/.dirs $(STAND)/.static_synced $(MODEL_ARTIFACTS)

$(STAND)/.dirs:
	mkdir -p $(STAND)/Models $(STAND)/Nasal $(STAND)/Sounds $(STAND)/build $(BUILD)/warpx-runs
	touch $@

$(BUILD)/warpx-runs:
	mkdir -p '$(BUILD)' '$(BUILD)/warpx-runs'

$(STAND)/.static_synced: $(STAND_SRC_FILES) | $(STAND)/.dirs
	rsync -a --exclude='Models/orbitron.ac' --exclude='engine_surrogate.json' --exclude='*.wav' \
		$(ORBITRON)/Orbitron-TestStand/ $(STAND)/
	touch $@

# --- CadQuery → glTF (Aircraft/.../build only) ---
$(GLTF_LAB): $(LAB_CAD_SRC) | $(STAND)/.dirs
	mkdir -p $(STAND)/build
	cd $(ORBITRON) && ORBITRON_LAB_GLTF='$(GLTF_LAB)' $(POETRY) run python full_reactor_cad.py

$(GLTF_ARC): $(ORBITRON)/arcjet_test_stand_cad.py | $(STAND)/.dirs
	mkdir -p $(STAND)/build
	cd $(ORBITRON) && ORBITRON_ARCJET_GLTF='$(GLTF_ARC)' $(POETRY) run python arcjet_test_stand_cad.py

# --- Blender + UV → orbitron.ac ---
$(STAND)/.orbitron_ac_done: \
		$(GLTF_LAB) \
		$(ORBITRON)/build_ac3d.py \
		$(ORBITRON)/fix_screen_uv.py \
		| $(STAND)/.dirs $(STAND)/.static_synced
	rm -f '$(STAND)/Models/orbitron.ac'
	cd $(ORBITRON) && ORBITRON_AC_OUT='$(STAND)/Models/orbitron.ac' ORBITRON_GLTF_IN='$(GLTF_LAB)' \
		$(BLENDER) -b --python build_ac3d.py
	test -f '$(STAND)/Models/orbitron.ac'
	cd $(ORBITRON) && ORBITRON_AC_OUT='$(STAND)/Models/orbitron.ac' $(POETRY) run python fix_screen_uv.py
	touch $@

$(STAND)/Models/orbitron.ac: $(STAND)/.orbitron_ac_done
	@test -f '$@'

# --- Surrogate JSON (+ CSV under build/orbitron for warpx/dry) ---
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

# --- Synthesized WAV beds (add_reactor_sound.py) ---
$(STAND)/Sounds/.sounds_built: \
		$(ORBITRON)/add_reactor_sound.py \
		$(ORBITRON)/Orbitron-TestStand/Sounds/sound.xml \
		| $(STAND)/.dirs $(STAND)/.static_synced
	$(POETRY) run python $(ORBITRON)/add_reactor_sound.py --out-dir '$(STAND)/Sounds'
	touch '$@'

$(STAND)/build/surrogate_sweep_results.csv: $(STAND)/engine_surrogate.json | $(STAND)/.dirs
	mkdir -p '$(STAND)/build'
	cp -f '$(BUILD)/surrogate_sweep_results.csv' '$@'

graph: | $(STAND)/.dirs
	mkdir -p $(STAND)/build
	@{ \
	echo '%% Auto-generated by `make graph`. Paste into https://mermaid.live'; \
	echo '%% Full artifact graph for Orbitron-TestStand (sources → build/orbitron → Aircraft).'; \
	echo 'flowchart TD'; \
	echo '  subgraph SRC["Source repo (git) — not computed"]'; \
	echo '    fusion["ssto/orbitron/fusion_arcjet_engine_cad.py"]'; \
	echo '    lab_cad["ssto/orbitron/full_reactor_cad.py"]'; \
	echo '    arc_cad["ssto/orbitron/arcjet_test_stand_cad.py"]'; \
	echo '    blend["ssto/orbitron/build_ac3d.py"]'; \
	echo '    uv["ssto/orbitron/fix_screen_uv.py"]'; \
	echo '    pic["ssto/orbitron/laminar_flow_2d_arcjet.py"]'; \
	echo '    smap["tools/build_surrogate_map.py"]'; \
	echo '    wfit["tools/warpx_to_jsbsim_surrogate.py"]'; \
	echo '    snd["ssto/orbitron/add_reactor_sound.py"]'; \
	echo '    setxml["Orbitron-TestStand/Orbitron-TestStand-set.xml"]'; \
	echo '    jsbsim["Orbitron-TestStand/orbitron-jsbsim.xml"]'; \
	echo '    oxml["Orbitron-TestStand/Models/Orbitron.xml"]'; \
	echo '    wpng["Orbitron-TestStand/Models/warpx_frame.png"]'; \
	echo '    soundxml["Orbitron-TestStand/Sounds/sound.xml"]'; \
	echo '    nasal["Orbitron-TestStand/Nasal/*.nas"]'; \
	echo '    fusion --> lab_cad'; \
	echo '  end'; \
	echo '  subgraph BR["build/orbitron — WarpX + CSV (repo build dir)"]'; \
	echo '    csv_br["surrogate_sweep_results.csv"]'; \
	echo '    wruns["warpx-runs (one subdir per sweep cell)"]'; \
	echo '  end'; \
	echo '  subgraph AIR["Aircraft/Orbitron-TestStand — computed + synced"]'; \
	echo '    gltf_lab["build/orbitron_lab_v5.gltf"]'; \
	echo '    gltf_arc["build/arcjet_outdoor_stand.gltf"]'; \
	echo '    ac_stamp[".orbitron_ac_done (stamp)"]'; \
	echo '    ac["Models/orbitron.ac"]'; \
	echo '    jsur["engine_surrogate.json"]'; \
	echo '    csv_air["build/surrogate_sweep_results.csv (mirror)"]'; \
	echo '    snd_stamp["Sounds/.sounds_built (stamp)"]'; \
	echo '    wav_core["Sounds/orbitron_core_loop.wav"]'; \
	echo '    wav_in["Sounds/orbitron_inlet_loop.wav"]'; \
	echo '    wav_jet["Sounds/orbitron_jet_loop.wav"]'; \
	echo '    wav_dec["Sounds/orbitron_dec_arc_loop.wav"]'; \
	echo '    wav_scr["Sounds/orbitron_screen_sputter_loop.wav"]'; \
	echo '    wav_mot["Sounds/orbitron_motor_whine_loop.wav"]'; \
	echo '    wav_duct["Sounds/orbitron_duct_heat_loop.wav"]'; \
	echo '    wav_str["Sounds/orbitron_stressor_loop.wav"]'; \
	echo '    wav_heavy["Sounds/reactor_audio_heavy.wav"]'; \
	echo '    mmd["build/dependency_graph.mmd (this file via make graph)"]'; \
	echo '  end'; \
	echo '  fgready["fg-ready (make default goal)"]'; \
	echo '  lab_cad -->|ORBITRON_LAB_GLTF| gltf_lab'; \
	echo '  arc_cad -->|ORBITRON_ARCJET_GLTF| gltf_arc'; \
	echo '  gltf_lab -->|ORBITRON_GLTF_IN + Blender| blend'; \
	echo '  blend --> ac'; \
	echo '  uv --> ac'; \
	echo '  blend --> ac_stamp'; \
	echo '  uv --> ac_stamp'; \
	echo '  ac_stamp -.->|after touch| ac'; \
	echo '  pic --> smap'; \
	echo '  smap --> wruns'; \
	echo '  smap --> csv_br'; \
	echo '  smap --> wfit'; \
	echo '  wfit --> jsur'; \
	echo '  csv_br -->|cp| csv_air'; \
	echo '  jsur -->|order| csv_air'; \
	echo '  soundxml --> snd'; \
	echo '  snd --> wav_core'; \
	echo '  snd --> wav_in'; \
	echo '  snd --> wav_jet'; \
	echo '  snd --> wav_dec'; \
	echo '  snd --> wav_scr'; \
	echo '  snd --> wav_mot'; \
	echo '  snd --> wav_duct'; \
	echo '  snd --> wav_str'; \
	echo '  snd --> wav_heavy'; \
	echo '  snd --> snd_stamp'; \
	echo '  setxml --> airsync["rsync → Aircraft"]'; \
	echo '  jsbsim --> airsync'; \
	echo '  oxml --> airsync'; \
	echo '  wpng --> airsync'; \
	echo '  nasal --> airsync'; \
	echo '  airsync --> fgready'; \
	echo '  gltf_lab --> fgready'; \
	echo '  gltf_arc --> fgready'; \
	echo '  ac --> fgready'; \
	echo '  jsur --> fgready'; \
	echo '  csv_air --> fgready'; \
	echo '  wav_core --> fgready'; \
	echo '  wav_in --> fgready'; \
	echo '  wav_jet --> fgready'; \
	echo '  wav_dec --> fgready'; \
	echo '  wav_scr --> fgready'; \
	echo '  wav_mot --> fgready'; \
	echo '  wav_duct --> fgready'; \
	echo '  wav_str --> fgready'; \
	echo '  wav_heavy --> fgready'; \
	echo '  snd_stamp --> fgready'; \
	echo '  graph_run["make graph"] -.->|writes| mmd'; \
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
