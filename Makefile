# Orbitron-TestStand → FlightGear under ./Aircraft (incremental).
# All computed assets (glTF, .ac, WAV, surrogate JSON) live under Aircraft/ only;
# ssto/orbitron/Orbitron-TestStand/ holds source XML/Nasal; Sounds/sound.xml is generated
# from assembly_specs/orbitron_sound_assets.yaml (tools/compile_sound_xml_from_yaml.py).

REPO_ROOT := $(abspath .)
ORBITRON := $(REPO_ROOT)/ssto/orbitron
AIRCRAFT := $(REPO_ROOT)/Aircraft
STAND := $(AIRCRAFT)/Orbitron-TestStand
BUILD := $(REPO_ROOT)/build/orbitron

# Lab glTF: assembly YAML → flat → stem-normalized → nest → Blender → .ac.
# Arcjet-only glTF still from CadQuery (arcjet_test_stand_cad.py).
GLTF_LAB_FLAT := $(STAND)/build/orbitron_lab_flat.gltf
GLTF_LAB := $(STAND)/build/orbitron_lab.gltf
GLTF_ARC := $(STAND)/build/arcjet_outdoor_stand.gltf
COPY_GLTF_STEM := $(REPO_ROOT)/tools/copy_gltf_with_stem.py

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
	$(REPO_ROOT)/tools/warpx_expression_presets.py \
	$(ORBITRON_PHYSICS_SPEC) \
	$(ORBITRON_PHYSICS_SPEC_PY) \
	$(ORBITRON)/laminar_flow_2d_arcjet.py

MERMAID_OUT := $(STAND)/build/dependency_graph.mmd
PARTS_MERMAID := $(STAND)/build/orbitron_ac_parts_hierarchy.mmd
PARTS_LOGICAL_MERMAID := $(STAND)/build/orbitron_logical_assemblies.mmd
ORBITRON_MODEL_XML := $(ORBITRON)/Orbitron-TestStand/Models/Orbitron.xml
ASSEMBLY_SPECS_DIR := $(ORBITRON)/assembly_specs
ORBITRON_LOGICAL_ASSEMBLIES := $(ASSEMBLY_SPECS_DIR)/orbitron_logical_assemblies.yaml
LOGICAL_ASSEMBLIES_SPEC_PY := $(REPO_ROOT)/tools/orbitron_logical_assemblies_spec.py

# YAML assembly specs → glTF (A/B/C/D). First artifacts in fg-ready: rebuilt only when
# these YAMLs or the compiler / CadQuery templates they call change.
ORBITRON_LAB_YAMLS := \
	$(ASSEMBLY_SPECS_DIR)/air_breathing_intake.yaml \
	$(ASSEMBLY_SPECS_DIR)/fusion_reactor_stack.yaml \
	$(ASSEMBLY_SPECS_DIR)/test_stand_and_services.yaml \
	$(ASSEMBLY_SPECS_DIR)/orbitron_lab.yaml \
	$(ORBITRON_LOGICAL_ASSEMBLIES)
GLTF_YAML_A := $(STAND)/build/air_breathing_intake_from_yaml.gltf
GLTF_YAML_B := $(STAND)/build/fusion_reactor_stack_from_yaml.gltf
GLTF_YAML_C := $(STAND)/build/test_stand_and_services_from_yaml.gltf
YAML_LAB_GLTF_ARTIFACTS := $(GLTF_YAML_A) $(GLTF_YAML_B) $(GLTF_YAML_C) $(GLTF_LAB)
ORBITRON_SOUND_ASSETS := $(ASSEMBLY_SPECS_DIR)/orbitron_sound_assets.yaml
SOUND_COMPILER := $(REPO_ROOT)/tools/sound_compiler.py
COMPILE_SOUND_XML := $(REPO_ROOT)/tools/compile_sound_xml_from_yaml.py
ORBITRON_SOUND_XML := $(ORBITRON)/Orbitron-TestStand/Sounds/sound.xml
ORBITRON_PHYSICS_SPEC := $(ASSEMBLY_SPECS_DIR)/orbitron_physics_surrogate.yaml
ORBITRON_PHYSICS_SPEC_PY := $(REPO_ROOT)/tools/orbitron_physics_spec.py
YAML_LAB_COMPILER_DEPS := \
	$(REPO_ROOT)/tools/compile_assembly_yaml.py \
	$(REPO_ROOT)/tools/yaml_assembly/compiler.py \
	$(REPO_ROOT)/tools/yaml_assembly/transform_ops.py \
	$(REPO_ROOT)/tools/yaml_assembly/templates_registry.py \
	$(COPY_GLTF_STEM) \
	$(ORBITRON)/arcjet_test_stand_cad.py \
	$(ORBITRON)/full_reactor_cad.py

# Inputs that define the build graph (edit Makefile subgraph block when topology changes).
GRAPH_INPUTS := Makefile $(ORBITRON_LAB_YAMLS) $(YAML_LAB_COMPILER_DEPS) \
	$(ORBITRON_SOUND_ASSETS) $(SOUND_COMPILER) $(COMPILE_SOUND_XML) \
	$(ORBITRON_PHYSICS_SPEC) $(ORBITRON_PHYSICS_SPEC_PY) $(REPO_ROOT)/tools/warpx_expression_presets.py \
	$(ORBITRON)/build_ac3d.py $(ORBITRON)/fix_screen_uv.py $(SUR_DEP_ALL) \
	$(REPO_ROOT)/tools/orbitron_ac_hierarchy_mmd.py \
	$(REPO_ROOT)/tools/gltf_nest_from_assemblies.py \
	$(LOGICAL_ASSEMBLIES_SPEC_PY) \
	$(ORBITRON_LOGICAL_ASSEMBLIES)

# Computed FlightGear model + audio (all under Aircraft/)
MODEL_ARTIFACTS := \
	$(YAML_LAB_GLTF_ARTIFACTS) \
	$(GLTF_ARC) \
	$(STAND)/Models/orbitron.ac \
	$(STAND)/engine_surrogate.json \
	$(STAND)/Sounds/.sounds_built \
	$(STAND)/build/surrogate_sweep_results.csv \
	$(MERMAID_OUT) \
	$(PARTS_MERMAID) \
	$(PARTS_LOGICAL_MERMAID)

.PHONY: all help clean graph parts-graph open-lab run-fgfs fg-ready yaml-lab-gltfs orbitron-lab-gltf

all: fg-ready

help:
	@echo "Orbitron-TestStand Makefile"
	@echo "  make / make all     Build $(STAND); YAML lab → $(GLTF_LAB), arcjet glTF, .ac, surrogate, sounds from $(ORBITRON_SOUND_ASSETS), $(MERMAID_OUT), … (SURROGATE=$(SURROGATE))"
	@echo "  SURROGATE=warpx|dry|mesh   Surrogate source (default warpx = full sweep; dry|mesh = fast placeholders)"
	@echo "  Cold-tree regression: mv Aircraft Aircraft.bak && ./stand.sh   # rebuilds everything incl. WarpX surrogate"
	@echo "  make graph          Regenerate $(MERMAID_OUT) only (also runs as part of make all)"
	@echo "  make parts-graph    Regenerate mesh Mermaid: $(PARTS_MERMAID) + $(PARTS_LOGICAL_MERMAID)"
	@echo "  make open-lab       Launch Blender on nested $(GLTF_LAB) (same as ./bl.sh)"
	@echo "  make orbitron-lab-gltf  Build only $(GLTF_LAB) (YAML flat → stem → nest); for scripts / CI"
	@echo "  ./bl.sh             Blender + nested lab glTF; ./bl.sh --collections for VIEW__* isolate collections"
	@echo "  make yaml-lab-gltfs  Only the four YAML-driven glTFs (same rules as make all; optional shortcut)"
	@echo "  ORBITRON_LAB_GLTF=... ./bl.sh   Override glTF path (default: $(GLTF_LAB); e.g. flat debug: …/orbitron_lab_flat.gltf)"
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

$(ORBITRON_SOUND_XML): $(ORBITRON_SOUND_ASSETS) $(COMPILE_SOUND_XML)
	cd '$(REPO_ROOT)' && $(POETRY) run python $(COMPILE_SOUND_XML) \
		--spec '$(ORBITRON_SOUND_ASSETS)' --out '$(ORBITRON_SOUND_XML)'

$(STAND)/.static_synced: $(STAND_SRC_FILES) $(ORBITRON_SOUND_XML) | $(STAND)/.dirs
	rsync -a --exclude='Models/orbitron.ac' --exclude='engine_surrogate.json' --exclude='*.wav' \
		$(ORBITRON)/Orbitron-TestStand/ $(STAND)/
	touch $@

$(GLTF_YAML_A): $(ASSEMBLY_SPECS_DIR)/air_breathing_intake.yaml $(YAML_LAB_COMPILER_DEPS) | $(STAND)/.dirs
	cd '$(REPO_ROOT)' && $(POETRY) run python tools/compile_assembly_yaml.py \
		--spec '$(ASSEMBLY_SPECS_DIR)/air_breathing_intake.yaml' --out '$@'

$(GLTF_YAML_B): $(ASSEMBLY_SPECS_DIR)/fusion_reactor_stack.yaml $(YAML_LAB_COMPILER_DEPS) | $(STAND)/.dirs
	cd '$(REPO_ROOT)' && $(POETRY) run python tools/compile_assembly_yaml.py \
		--spec '$(ASSEMBLY_SPECS_DIR)/fusion_reactor_stack.yaml' --out '$@'

$(GLTF_YAML_C): $(ASSEMBLY_SPECS_DIR)/test_stand_and_services.yaml $(YAML_LAB_COMPILER_DEPS) | $(STAND)/.dirs
	cd '$(REPO_ROOT)' && $(POETRY) run python tools/compile_assembly_yaml.py \
		--spec '$(ASSEMBLY_SPECS_DIR)/test_stand_and_services.yaml' --out '$@'

$(GLTF_LAB_FLAT): $(ORBITRON_LAB_YAMLS) $(YAML_LAB_COMPILER_DEPS) | $(STAND)/.dirs
	mkdir -p $(STAND)/build
	cd '$(REPO_ROOT)' && $(POETRY) run python tools/compile_assembly_yaml.py \
		--spec '$(ASSEMBLY_SPECS_DIR)/orbitron_lab.yaml' --out '$@'

# --- Nested lab glTF (stem-normalized buffer name, then logical assemblies nest) ---
$(GLTF_LAB): $(GLTF_LAB_FLAT) $(COPY_GLTF_STEM) $(ORBITRON_LOGICAL_ASSEMBLIES) $(LOGICAL_ASSEMBLIES_SPEC_PY) $(REPO_ROOT)/tools/gltf_nest_from_assemblies.py | $(STAND)/.dirs
	mkdir -p $(STAND)/build
	cd '$(REPO_ROOT)' && $(POETRY) run python tools/copy_gltf_with_stem.py \
		--src '$(GLTF_LAB_FLAT)' --dst '$(GLTF_LAB)'
	python3 '$(REPO_ROOT)/tools/gltf_nest_from_assemblies.py' \
		--gltf '$(GLTF_LAB)' --assemblies-spec '$(ORBITRON_LOGICAL_ASSEMBLIES)' \
		--root-name fusion_arcjet_engine

# Stable entry for scripts: builds $(GLTF_LAB) regardless of absolute vs relative cwd quirks.
orbitron-lab-gltf: $(GLTF_LAB)

yaml-lab-gltfs: $(YAML_LAB_GLTF_ARTIFACTS)

$(GLTF_ARC): $(ORBITRON)/arcjet_test_stand_cad.py | $(STAND)/.dirs
	mkdir -p $(STAND)/build
	cd $(ORBITRON) && ORBITRON_ARCJET_GLTF='$(GLTF_ARC)' $(POETRY) run python arcjet_test_stand_cad.py

# --- Blender + UV → orbitron.ac ---
# Real deps on surrogate + sounds (not only order-only): GNU make may otherwise schedule
# Blender before WarpX / sound_compiler; cold-tree regression must finish PIC + audio first.
$(STAND)/.orbitron_ac_done: \
		$(GLTF_LAB) \
		$(STAND)/engine_surrogate.json \
		$(STAND)/Sounds/.sounds_built \
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

# --- Synthesized WAV beds (orbitron_sound_assets.yaml → sound_compiler.py) ---
$(STAND)/Sounds/.sounds_built: \
		$(ORBITRON_SOUND_ASSETS) $(SOUND_COMPILER) $(COMPILE_SOUND_XML) \
		$(ORBITRON_SOUND_XML) \
		| $(STAND)/.dirs $(STAND)/.static_synced
	$(POETRY) run python $(SOUND_COMPILER) --spec '$(ORBITRON_SOUND_ASSETS)' --out-dir '$(STAND)/Sounds'
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
	echo '  subgraph LAB["Orbitron lab glTF (YAML → .ac)"]'; \
	echo '    y_specs["ssto/orbitron/assembly_specs/*.yaml"]'; \
	echo '    y_compile["tools/compile_assembly_yaml.py"]'; \
	echo '    y_specs --> y_compile'; \
	echo '    y_compile --> gltf_flat0["…/orbitron_lab_flat.gltf"]'; \
	echo '    copy_stem["tools/copy_gltf_with_stem.py"]'; \
	echo '    gltf_flat0 --> copy_stem'; \
	echo '    copy_stem --> gltf_lab["…/orbitron_lab.gltf"]'; \
	echo '    nest_py["tools/gltf_nest_from_assemblies.py"]'; \
	echo '    asm_yaml2["orbitron_logical_assemblies.yaml"]'; \
	echo '    asm_yaml2 --> nest_py'; \
	echo '    gltf_lab --> nest_py'; \
	echo '  end'; \
	echo '  subgraph CQ["CadQuery (arcjet-only)"]'; \
	echo '    arc_py["arcjet_test_stand_cad.py"]'; \
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
	echo '    asm_yaml["repo …/orbitron_logical_assemblies.yaml"]'; \
	echo '    asm_yaml --> parts_py'; \
	echo '    parts_py --> parts_flat["Aircraft/…/build/orbitron_ac_parts_hierarchy.mmd"]'; \
	echo '    parts_py --> parts_logical["Aircraft/…/build/orbitron_logical_assemblies.mmd"]'; \
	echo '    mk_parts["Makefile: parts-graph"] --> parts_flat'; \
	echo '    mk_parts --> parts_logical'; \
	echo '  end'; \
	echo '  subgraph WX["WarpX PIC"]'; \
	echo '    phy_yaml["orbitron_physics_surrogate.yaml"]'; \
	echo '    phy_yaml -->|picmi_overrides.json| smap_py'; \
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
	echo '  subgraph SND["sounds (YAML compilers)"]'; \
	echo '    snd_yaml["orbitron_sound_assets.yaml"]'; \
	echo '    snd_xml_py["compile_sound_xml_from_yaml.py"]'; \
	echo '    snd_py["sound_compiler.py"]'; \
	echo '    snd_yaml --> snd_xml_py --> fsnd["repo …/Sounds/sound.xml"]'; \
	echo '    snd_yaml --> snd_py'; \
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
	echo '    fnas["repo …/Nasal/*.nas"] --> rsync'; \
	echo '    fsnd["repo …/Sounds/sound.xml"] --> rsync'; \
	echo '  end'; \
	echo '  rsync --> a_set["Aircraft/…/Orbitron-TestStand-set.xml"]'; \
	echo '  rsync --> a_jsb["Aircraft/…/orbitron-jsbsim.xml"]'; \
	echo '  rsync --> a_ox["Aircraft/…/Models/Orbitron.xml"]'; \
	echo '  rsync --> a_nas["Aircraft/…/Nasal/*.nas"]'; \
	echo '  rsync --> a_snd["Aircraft/…/Sounds/sound.xml"]'; \
	echo '  subgraph FG["FlightGear"]'; \
	echo '    fg["fgfs"]'; \
	echo '  end'; \
	echo '  a_set --> fg'; \
	echo '  a_jsb --> fg'; \
	echo '  a_ox --> fg'; \
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
$(PARTS_MERMAID) $(PARTS_LOGICAL_MERMAID) &: $(REPO_ROOT)/tools/orbitron_ac_hierarchy_mmd.py $(STAND)/Models/orbitron.ac $(ORBITRON_MODEL_XML) $(ORBITRON_LOGICAL_ASSEMBLIES) | $(STAND)/.dirs
	mkdir -p $(STAND)/build
	cd $(REPO_ROOT) && python3 tools/orbitron_ac_hierarchy_mmd.py \
		--ac '$(STAND)/Models/orbitron.ac' \
		--orbitron-xml '$(ORBITRON_MODEL_XML)' \
		--assemblies-spec '$(ORBITRON_LOGICAL_ASSEMBLIES)' \
		-o '$(PARTS_MERMAID)' \
		--logical-out '$(PARTS_LOGICAL_MERMAID)'

parts-graph: $(PARTS_MERMAID) $(PARTS_LOGICAL_MERMAID)

# Nested glTF is built by fg-ready / $(GLTF_LAB); this only opens Blender (no CadQuery run).
open-lab:
	@if ! test -f '$(GLTF_LAB)'; then \
		echo "error: missing $(GLTF_LAB) — run ./stand.sh first." >&2; \
		exit 1; \
	fi
	@$(REPO_ROOT)/bl.sh

run-fgfs: fg-ready
	cd $(REPO_ROOT) && fgfs --fg-aircraft=$(AIRCRAFT) --aircraft=Orbitron-TestStand \
		--airport=BIKF --parkpos=East-Apron-119 --timeofday=noon --ai-traffic=0 \
		--real-weather-fetch=0 --clouds3d=0 \
		--prop:/sim/sound/chatter/volume=0.0 --prop:/sim/sound/atc/volume=0.0 \
		--prop:/instrumentation/comm/volume=0.0

clean:
	rm -rf '$(AIRCRAFT)' '$(BUILD)'
