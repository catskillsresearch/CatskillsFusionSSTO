# Orbitron-TestStand → FlightGear under ./Aircraft (incremental).
# All computed assets (glTF, .ac, WAV, surrogate JSON) live under Aircraft/ only;
# ssto/orbitron/Orbitron-TestStand/ holds source XML/Nasal/sound.xml only.

REPO_ROOT := $(abspath .)
ORBITRON := $(REPO_ROOT)/ssto/orbitron
AIRCRAFT := $(REPO_ROOT)/Aircraft
STAND := $(AIRCRAFT)/Orbitron-TestStand
BUILD := $(REPO_ROOT)/build/orbitron

# CadQuery / Blender / PIC inputs (sources)
# CadQuery → flat glTF → nested glTF (Blender / FG use nested file).
GLTF_LAB_CAD := $(STAND)/build/orbitron_lab_v5_from_cad.gltf
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
PARTS_MERMAID := $(STAND)/build/orbitron_ac_parts_hierarchy.mmd
PARTS_LOGICAL_MERMAID := $(STAND)/build/orbitron_logical_assemblies.mmd
ORBITRON_MODEL_XML := $(ORBITRON)/Orbitron-TestStand/Models/Orbitron.xml
ASSEMBLIES_JSON := $(ORBITRON)/Orbitron-TestStand/orbitron_logical_assemblies.json

# Inputs that define the build graph (edit Makefile subgraph block when topology changes).
GRAPH_INPUTS := Makefile $(LAB_CAD_SRC) $(ORBITRON)/arcjet_test_stand_cad.py \
	$(ORBITRON)/build_ac3d.py $(ORBITRON)/fix_screen_uv.py $(SUR_DEP_ALL) \
	$(ORBITRON)/add_reactor_sound.py \
	$(REPO_ROOT)/tools/orbitron_ac_hierarchy_mmd.py \
	$(REPO_ROOT)/tools/gltf_nest_from_assemblies.py \
	$(ASSEMBLIES_JSON)

# Computed FlightGear model + audio (all under Aircraft/)
MODEL_ARTIFACTS := \
	$(GLTF_LAB) \
	$(GLTF_ARC) \
	$(STAND)/Models/orbitron.ac \
	$(STAND)/engine_surrogate.json \
	$(STAND)/Sounds/.sounds_built \
	$(STAND)/build/surrogate_sweep_results.csv \
	$(MERMAID_OUT) \
	$(PARTS_MERMAID) \
	$(PARTS_LOGICAL_MERMAID)

.PHONY: all help clean graph parts-graph run-fgfs fg-ready

all: fg-ready

help:
	@echo "Orbitron-TestStand Makefile"
	@echo "  make / make all     Build $(STAND); fg-ready includes $(MERMAID_OUT), $(PARTS_MERMAID), $(PARTS_LOGICAL_MERMAID) (SURROGATE=$(SURROGATE))"
	@echo "  SURROGATE=warpx|dry|mesh   Surrogate source (warpx is slow)"
	@echo "  make graph          Regenerate $(MERMAID_OUT) only (also runs as part of make all)"
	@echo "  make parts-graph    Regenerate mesh Mermaid: $(PARTS_MERMAID) + $(PARTS_LOGICAL_MERMAID)"
	@echo "  Blender: import $(GLTF_LAB) for nested fusion_arcjet_engine tree; optional:"
	@echo "    blender --python $(REPO_ROOT)/tools/blender_orbitron_viewport_collections.py -- '$(GLTF_LAB)'"
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

# --- CadQuery → flat glTF ---
$(GLTF_LAB_CAD): $(LAB_CAD_SRC) | $(STAND)/.dirs
	mkdir -p $(STAND)/build
	cd $(ORBITRON) && ORBITRON_LAB_GLTF='$(GLTF_LAB_CAD)' $(POETRY) run python full_reactor_cad.py

# --- Nest glTF node tree (orbitron_logical_assemblies.json) for Blender inspection ---
$(GLTF_LAB): $(GLTF_LAB_CAD) $(ASSEMBLIES_JSON) $(REPO_ROOT)/tools/gltf_nest_from_assemblies.py | $(STAND)/.dirs
	cp -f '$(GLTF_LAB_CAD)' '$(GLTF_LAB)'
	python3 '$(REPO_ROOT)/tools/gltf_nest_from_assemblies.py' \
		--gltf '$(GLTF_LAB)' --assemblies-json '$(ASSEMBLIES_JSON)' \
		--root-name fusion_arcjet_engine

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

# Dependency map for mermaid.live (rebuilt when Makefile changes; part of fg-ready).
$(MERMAID_OUT): $(GRAPH_INPUTS) | $(STAND)/.dirs
	mkdir -p $(STAND)/build
	@{ \
	echo '%% Auto-generated by `make graph`. Paste into https://mermaid.live'; \
	echo '%% Scripts→scripts, scripts→files, engine I/O, then only FG-runtime files→fgfs.'; \
	echo 'flowchart LR'; \
	echo '  smap_py["tools/build_surrogate_map.py"]'; \
	echo '  wfit_py["tools/warpx_to_jsbsim_surrogate.py"]'; \
	echo '  smap_py -->|subprocess| pic_py["ssto/orbitron/laminar_flow_2d_arcjet.py"]'; \
	echo '  smap_py -->|subprocess| wfit_py'; \
	echo '  subgraph CQ["CadQuery"]'; \
	echo '    cq_in["inputs: solid geometry in Python"]'; \
	echo '    fusion_py["fusion_arcjet_engine_cad.py"]'; \
	echo '    lab_py["full_reactor_cad.py"]'; \
	echo '    arc_py["arcjet_test_stand_cad.py"]'; \
	echo '    cq_in --> fusion_py'; \
	echo '    cq_in --> arc_py'; \
	echo '    fusion_py -->|import| lab_py'; \
	echo '    lab_py --> gltf_lab["Aircraft/.../build/orbitron_lab_v5.gltf"]'; \
	echo '    lab_py --> bin_lab["Aircraft/.../build/orbitron_lab_v5.bin"]'; \
	echo '    arc_py --> gltf_arc["Aircraft/.../build/arcjet_outdoor_stand.gltf"]'; \
	echo '    arc_py --> bin_arc["Aircraft/.../build/arcjet_outdoor_stand.bin"]'; \
	echo '  end'; \
	echo '  subgraph BL["Blender"]'; \
	echo '    gltf_lab --> blend_py["build_ac3d.py"]'; \
	echo '    blend_py --> ac["Aircraft/.../Models/orbitron.ac"]'; \
	echo '    uv_py["fix_screen_uv.py"] --> ac'; \
	echo '  end'; \
	echo '  subgraph PARTS["AC mesh parts (Mermaid)"]'; \
	echo '    parts_py["tools/orbitron_ac_hierarchy_mmd.py"]'; \
	echo '    ac --> parts_py'; \
	echo '    foxml -.->|offset header| parts_py'; \
	echo '    asm_json["repo …/orbitron_logical_assemblies.json"]'; \
	echo '    asm_json --> parts_py'; \
	echo '    parts_py --> parts_flat["Aircraft/…/build/orbitron_ac_parts_hierarchy.mmd"]'; \
	echo '    parts_py --> parts_logical["Aircraft/…/build/orbitron_logical_assemblies.mmd"]'; \
	echo '    mk_parts["Makefile: parts-graph"] --> parts_flat'; \
	echo '    mk_parts --> parts_logical'; \
	echo '  end'; \
	echo '  subgraph WX["WarpX PIC"]'; \
	echo '    wx_in["inputs: PIC deck + WarpX"]'; \
	echo '    wx_in --> pic_py'; \
	echo '    pic_py --> wruns["build/orbitron/warpx-runs/*"]'; \
	echo '    wruns -->|yt reduce| smap_py'; \
	echo '    smap_py --> csv_br["build/orbitron/surrogate_sweep_results.csv"]'; \
	echo '  end'; \
	echo '  csv_br -->|CSV in| wfit_py'; \
	echo '  wfit_py --> jsur["Aircraft/.../engine_surrogate.json"]'; \
	echo '  mk_cp["Makefile: cp CSV mirror"]'; \
	echo '  csv_br --> mk_cp'; \
	echo '  jsur -.->|ordering| mk_cp'; \
	echo '  mk_cp --> csv_air["Aircraft/.../build/surrogate_sweep_results.csv"]'; \
	echo '  subgraph SND["add_reactor_sound"]'; \
	echo '    snd_in["input: repo Sounds/sound.xml"]'; \
	echo '    snd_py["add_reactor_sound.py"]'; \
	echo '    snd_in --> snd_py'; \
	echo '    snd_py --> w1["Aircraft/.../Sounds/orbitron_core_loop.wav"]'; \
	echo '    snd_py --> w2["Aircraft/.../Sounds/orbitron_inlet_loop.wav"]'; \
	echo '    snd_py --> w3["Aircraft/.../Sounds/orbitron_jet_loop.wav"]'; \
	echo '    snd_py --> w4["Aircraft/.../Sounds/orbitron_dec_arc_loop.wav"]'; \
	echo '    snd_py --> w5["Aircraft/.../Sounds/orbitron_screen_sputter_loop.wav"]'; \
	echo '    snd_py --> w6["Aircraft/.../Sounds/orbitron_motor_whine_loop.wav"]'; \
	echo '    snd_py --> w7["Aircraft/.../Sounds/orbitron_duct_heat_loop.wav"]'; \
	echo '    snd_py --> w8["Aircraft/.../Sounds/orbitron_stressor_loop.wav"]'; \
	echo '    snd_py --> w9["Aircraft/.../Sounds/reactor_audio_heavy.wav"]'; \
	echo '  end'; \
	echo '  subgraph SYNC["Makefile rsync"]'; \
	echo '    rsync["rsync → Aircraft"]'; \
	echo '    fset["repo …/Orbitron-TestStand-set.xml"] --> rsync'; \
	echo '    fjsb["repo …/orbitron-jsbsim.xml"] --> rsync'; \
	echo '    foxml["repo …/Models/Orbitron.xml"] --> rsync'; \
	echo '    fpng["repo …/Models/warpx_frame.png"] --> rsync'; \
	echo '    fnas["repo …/Nasal/*.nas"] --> rsync'; \
	echo '    fsnd["repo …/Sounds/sound.xml"] --> rsync'; \
	echo '  end'; \
	echo '  rsync --> a_set["Aircraft/…/Orbitron-TestStand-set.xml"]'; \
	echo '  rsync --> a_jsb["Aircraft/…/orbitron-jsbsim.xml"]'; \
	echo '  rsync --> a_ox["Aircraft/…/Models/Orbitron.xml"]'; \
	echo '  rsync --> a_png["Aircraft/…/Models/warpx_frame.png"]'; \
	echo '  rsync --> a_nas["Aircraft/…/Nasal/*.nas"]'; \
	echo '  rsync --> a_snd["Aircraft/…/Sounds/sound.xml"]'; \
	echo '  subgraph FG["FlightGear"]'; \
	echo '    fg["fgfs"]'; \
	echo '  end'; \
	echo '  a_set --> fg'; \
	echo '  a_jsb --> fg'; \
	echo '  a_ox --> fg'; \
	echo '  a_png --> fg'; \
	echo '  a_nas --> fg'; \
	echo '  a_snd --> fg'; \
	echo '  ac --> fg'; \
	echo '  jsur --> fg'; \
	echo '  w1 --> fg'; \
	echo '  w2 --> fg'; \
	echo '  w3 --> fg'; \
	echo '  w4 --> fg'; \
	echo '  w5 --> fg'; \
	echo '  w6 --> fg'; \
	echo '  w7 --> fg'; \
	echo '  w8 --> fg'; \
	echo '  w9 --> fg'; \
	echo '  mk_mmd["Makefile: graph target"] --> mmd["Aircraft/…/build/dependency_graph.mmd"]'; \
	} > '$@'
	@echo "Wrote $@"

graph: $(MERMAID_OUT)

# Mesh part inclusion tree (Mermaid); complements dependency_graph.mmd (build pipeline).
# Physical AC tree + logical assembly Mermaid (grouped rule: one recipe, two outputs).
$(PARTS_MERMAID) $(PARTS_LOGICAL_MERMAID) &: $(REPO_ROOT)/tools/orbitron_ac_hierarchy_mmd.py $(STAND)/Models/orbitron.ac $(ORBITRON_MODEL_XML) $(ASSEMBLIES_JSON) | $(STAND)/.dirs
	mkdir -p $(STAND)/build
	cd $(REPO_ROOT) && python3 tools/orbitron_ac_hierarchy_mmd.py \
		--ac '$(STAND)/Models/orbitron.ac' \
		--orbitron-xml '$(ORBITRON_MODEL_XML)' \
		--assemblies-json '$(ASSEMBLIES_JSON)' \
		-o '$(PARTS_MERMAID)' \
		--logical-out '$(PARTS_LOGICAL_MERMAID)'

parts-graph: $(PARTS_MERMAID) $(PARTS_LOGICAL_MERMAID)

run-fgfs: fg-ready
	cd $(REPO_ROOT) && fgfs --fg-aircraft=$(AIRCRAFT) --aircraft=Orbitron-TestStand \
		--airport=BIKF --parkpos=East-Apron-119 --timeofday=noon --ai-traffic=0 \
		--real-weather-fetch=0 --clouds3d=0 \
		--prop:/sim/sound/chatter/volume=0.0 --prop:/sim/sound/atc/volume=0.0 \
		--prop:/instrumentation/comm/volume=0.0

clean:
	rm -rf '$(AIRCRAFT)' '$(BUILD)'
