# Orbitron test stand → FlightGear under ./Aircraft (incremental).
# All computed assets (glTF, .ac, WAV, surrogate JSON, sound.xml, *-set.xml from YAML,
# orbitron-jsbsim.xml, Models/Orbitron.xml, Nasal from orbitron_nasal.yaml) live under Aircraft/ only.
# Aircraft package name: assembly_specs/orbitron_aircraft_flightgear.yaml → aircraft.package_dir
# (tools/orbitron_aircraft_paths.py). Shell XML: tools/compile_orbitron_aircraft_runtime.py.

REPO_ROOT := $(abspath .)
ORBITRON_PKG := $(shell python3 '$(REPO_ROOT)/tools/orbitron_aircraft_paths.py' package_dir --repo-root '$(REPO_ROOT)')
ORBITRON := $(REPO_ROOT)/ssto/orbitron
AIRCRAFT := $(REPO_ROOT)/Aircraft
STAND := $(AIRCRAFT)/$(ORBITRON_PKG)
BUILD := $(REPO_ROOT)/build/orbitron

# Lab glTF: unified assembly YAML (schema v2) → nested CadQuery export → Blender → .ac.
GLTF_LAB := $(STAND)/build/orbitron_lab.gltf
# Per-logical-group slices (``--subassembly``); built with ``make`` / fg-ready / ``orbitron-lab-gltf``.
GLTF_LAB_TANK_SUB_NAMES := methane_tank_assy boron_tank_assy hydrogen_tank_assy tank_assy
GLTF_LAB_TANK_SUBS := $(foreach n,$(GLTF_LAB_TANK_SUB_NAMES),$(STAND)/build/$(n).gltf)
GLTF_LAB_EXTRA_SUB_NAMES := \
	propulsive_nozzle reactor_bay turbofan_intake air_breathing_engine control_panel_stand thrust_sled
GLTF_LAB_EXTRA_SUBS := $(foreach n,$(GLTF_LAB_EXTRA_SUB_NAMES),$(STAND)/build/$(n).gltf)
GLTF_LAB_SUBASSEMBLIES := $(GLTF_LAB_TANK_SUBS) $(GLTF_LAB_EXTRA_SUBS)

POETRY ?= poetry
BLENDER ?= blender
SURROGATE ?= warpx
GRID ?= 4

export ORBITRON_AC_OUT := $(STAND)/Models/orbitron.ac
export ORBITRON_AIRCRAFT_PKG := $(ORBITRON_PKG)

WARPX_MAKE_ARGS ?=

MERMAID_OUT := $(STAND)/build/dependency_graph.mmd
PARTS_MERMAID := $(STAND)/build/orbitron_ac_parts_hierarchy.mmd
PARTS_LOGICAL_MERMAID := $(STAND)/build/orbitron_logical_assemblies.mmd
ASSEMBLY_SPECS_DIR := $(ORBITRON)/assembly_specs
LOGICAL_ASSEMBLIES_SPEC_PY := $(REPO_ROOT)/tools/orbitron_logical_assemblies_spec.py
# Single SSOT for lab geometry + logical tree (schema v2).
ORBITRON_ASSEMBLY_SPEC := $(ASSEMBLY_SPECS_DIR)/orbitron_lab.yaml

# YAML assembly spec → nested lab glTF. Rebuilt when the spec or compiler /
# CadQuery templates change.
ORBITRON_LAB_YAMLS := $(ORBITRON_ASSEMBLY_SPEC)
ORBITRON_SOUND_ASSETS := $(ASSEMBLY_SPECS_DIR)/orbitron_sound_assets.yaml
SOUND_COMPILER := $(REPO_ROOT)/tools/sound_compiler.py
COMPILE_SOUND_XML := $(REPO_ROOT)/tools/compile_sound_xml_from_yaml.py
ORBITRON_SOUND_XML := $(STAND)/Sounds/sound.xml
ORBITRON_PHYSICS_SPEC := $(ASSEMBLY_SPECS_DIR)/orbitron_physics_surrogate.yaml
ORBITRON_PHYSICS_SPEC_PY := $(REPO_ROOT)/tools/orbitron_physics_spec.py
ORBITRON_MODEL_XML := $(STAND)/Models/Orbitron.xml
ORBITRON_AIRCRAFT_SPEC := $(ASSEMBLY_SPECS_DIR)/orbitron_aircraft_flightgear.yaml
ORBITRON_NASAL_SPEC := $(ASSEMBLY_SPECS_DIR)/orbitron_nasal.yaml
ORBITRON_AIRCRAFT_PATHS := $(REPO_ROOT)/tools/orbitron_aircraft_paths.py
COMPILE_ORBITRON_NASAL := $(REPO_ROOT)/tools/compile_orbitron_nasal.py
COMPILE_AIRCRAFT_RUNTIME := $(REPO_ROOT)/tools/compile_orbitron_aircraft_runtime.py
JSBSIM_TEMPLATE := $(REPO_ROOT)/tools/templates/orbitron-jsbsim.xml
STAND_FG_SET := $(STAND)/$(ORBITRON_PKG)-set.xml
STAND_NASAL := $(STAND)/Nasal/surrogate_load.nas $(STAND)/Nasal/reactor_ui.nas
STAND_JSBSIM_XML := $(STAND)/orbitron-jsbsim.xml
SUR_DEP_ALL := \
	$(REPO_ROOT)/tools/build_surrogate_map.py \
	$(REPO_ROOT)/tools/warpx_to_jsbsim_surrogate.py \
	$(REPO_ROOT)/tools/warpx_expression_presets.py \
	$(ORBITRON_PHYSICS_SPEC) \
	$(ORBITRON_PHYSICS_SPEC_PY) \
	$(ORBITRON)/laminar_flow_2d_arcjet.py
YAML_LAB_COMPILER_DEPS := \
	$(REPO_ROOT)/tools/compile_assembly_yaml.py \
	$(REPO_ROOT)/tools/yaml_assembly/compiler.py \
	$(REPO_ROOT)/tools/yaml_assembly/transform_ops.py \
	$(REPO_ROOT)/tools/yaml_assembly/templates_registry.py \
	$(ORBITRON)/arcjet_test_stand_cad.py \
	$(ORBITRON)/full_reactor_cad.py

# Inputs that define the build graph (edit Makefile subgraph block when topology changes).
GRAPH_INPUTS := Makefile $(ORBITRON_LAB_YAMLS) $(YAML_LAB_COMPILER_DEPS) \
	$(ORBITRON_SOUND_ASSETS) $(SOUND_COMPILER) $(COMPILE_SOUND_XML) \
	$(ORBITRON_AIRCRAFT_SPEC) $(ORBITRON_AIRCRAFT_PATHS) $(REPO_ROOT)/tools/orbitron_aircraft_pkg.py $(COMPILE_AIRCRAFT_RUNTIME) $(JSBSIM_TEMPLATE) \
	$(ORBITRON_NASAL_SPEC) $(COMPILE_ORBITRON_NASAL) \
	$(ORBITRON_PHYSICS_SPEC) $(ORBITRON_PHYSICS_SPEC_PY) $(REPO_ROOT)/tools/warpx_expression_presets.py \
	$(ORBITRON)/build_ac3d.py $(ORBITRON)/fix_screen_uv.py $(SUR_DEP_ALL) \
	$(REPO_ROOT)/tools/orbitron_ac_hierarchy_mmd.py \
	$(LOGICAL_ASSEMBLIES_SPEC_PY) \
	$(ORBITRON_ASSEMBLY_SPEC)

# Computed FlightGear model + audio (all under Aircraft/)
MODEL_ARTIFACTS := \
	$(GLTF_LAB) \
	$(GLTF_LAB_SUBASSEMBLIES) \
	$(STAND)/Models/orbitron.ac \
	$(STAND)/engine_surrogate.json \
	$(STAND)/Sounds/.sounds_built \
	$(STAND)/build/surrogate_sweep_results.csv \
	$(MERMAID_OUT) \
	$(PARTS_MERMAID) \
	$(PARTS_LOGICAL_MERMAID)

.PHONY: all help clean graph parts-graph open-lab run-fgfs fg-ready orbitron-lab-gltf orbitron-lab-tank-sub-gltfs orbitron-lab-sub-gltfs surrogate-closure

all: fg-ready

help:
	@echo "Orbitron test stand Makefile (aircraft id: $(ORBITRON_PKG))"
	@echo "  make / make all     Build $(STAND); YAML lab → $(GLTF_LAB) + sub-assembly glTFs (see GLTF_LAB_SUBASSEMBLIES), .ac, surrogate, … (SURROGATE=$(SURROGATE))"
	@echo "  SURROGATE=warpx|dry|mesh   Surrogate source (default warpx = full sweep; dry|mesh = fast placeholders)"
	@echo "  Cold-tree regression: mv Aircraft Aircraft.bak && ./stand.sh   # rebuilds everything incl. WarpX surrogate"
	@echo "  make graph          Regenerate $(MERMAID_OUT) only (also runs as part of make all)"
	@echo "  make parts-graph    Regenerate mesh Mermaid: $(PARTS_MERMAID) + $(PARTS_LOGICAL_MERMAID)"
	@echo "  make open-lab       Launch Blender on nested $(GLTF_LAB) (same as ./bl.sh)"
	@echo "  make orbitron-lab-gltf  Build $(GLTF_LAB) + all sub-assembly glTFs under build/ (tanks, air path, panel, sled)"
	@echo "  make orbitron-lab-sub-gltfs  Sub-assembly glTFs only (same set as orbitron-lab-gltf minus the full lab file)"
	@echo "  make orbitron-lab-tank-sub-gltfs  The four tank-farm glTFs only (methane/boron/helium/tank_assy)"
	@echo "  make surrogate-closure  0D η·P_gross vs F²/(2ṁ) check (YAML scales); add JSON via ORBITRON_CLOSURE_JSON="
	@echo "  ./bl.sh             Blender + nested lab glTF; ./bl.sh --collections for VIEW__* isolate collections"
	@echo "  ORBITRON_LAB_GLTF=... ./bl.sh   Override glTF path (default: $(GLTF_LAB))"
	@echo "  make run-fgfs       fgfs with --fg-aircraft=$(AIRCRAFT)"
	@echo "  make clean          Remove $(AIRCRAFT) and $(BUILD) (not all of ./build if other projects use it)"
	@echo "  Tip: after rm -rf build, either make clean or rm $(STAND)/.dirs so .dirs is recreated."
	@echo "  Nasal is generated from $(ORBITRON_NASAL_SPEC); sound.xml + WAV under $(STAND)/Sounds/. Built model: $(MODEL_ARTIFACTS)"
	@echo "Use ./stand.sh for Poetry + WarpX library paths, then make."

fg-ready: $(STAND)/.dirs $(STAND_NASAL) $(STAND_FG_SET) $(STAND_JSBSIM_XML) $(ORBITRON_MODEL_XML) $(MODEL_ARTIFACTS)

$(STAND)/.dirs:
	mkdir -p $(STAND)/Models $(STAND)/Nasal $(STAND)/Sounds $(STAND)/build $(BUILD)/warpx-runs
	touch $@

$(BUILD)/warpx-runs:
	mkdir -p '$(BUILD)' '$(BUILD)/warpx-runs'

$(STAND_NASAL) &: $(ORBITRON_NASAL_SPEC) $(COMPILE_ORBITRON_NASAL) | $(STAND)/.dirs
	cd '$(REPO_ROOT)' && $(POETRY) run python $(COMPILE_ORBITRON_NASAL) \
		--spec '$(ORBITRON_NASAL_SPEC)' --out-dir '$(STAND)/Nasal'

$(ORBITRON_SOUND_XML): $(ORBITRON_SOUND_ASSETS) $(COMPILE_SOUND_XML) | $(STAND)/.dirs
	cd '$(REPO_ROOT)' && $(POETRY) run python $(COMPILE_SOUND_XML) \
		--spec '$(ORBITRON_SOUND_ASSETS)' --out '$(ORBITRON_SOUND_XML)'

$(STAND_FG_SET) $(STAND_JSBSIM_XML) $(ORBITRON_MODEL_XML) &: \
		$(ORBITRON_AIRCRAFT_SPEC) $(ORBITRON_PHYSICS_SPEC) $(COMPILE_AIRCRAFT_RUNTIME) $(JSBSIM_TEMPLATE) \
		| $(STAND)/.dirs
	cd '$(REPO_ROOT)' && $(POETRY) run python $(COMPILE_AIRCRAFT_RUNTIME) \
		--aircraft-spec '$(ORBITRON_AIRCRAFT_SPEC)' \
		--physics-spec '$(ORBITRON_PHYSICS_SPEC)' \
		--out-dir '$(STAND)'

# Nested lab glTF: CadQuery Assembly tree matches logical.groups (schema v2).
$(GLTF_LAB): $(ORBITRON_LAB_YAMLS) $(YAML_LAB_COMPILER_DEPS) | $(STAND)/.dirs
	mkdir -p $(STAND)/build
	cd '$(REPO_ROOT)' && $(POETRY) run python tools/compile_assembly_yaml.py \
		--spec '$(ORBITRON_ASSEMBLY_SPEC)' --out '$@'

# Sub-assembly glTFs: stem = logical.groups key (not ``orbitron_lab`` — that uses the rule above).
$(GLTF_LAB_SUBASSEMBLIES): $(STAND)/build/%.gltf: $(ORBITRON_ASSEMBLY_SPEC) $(YAML_LAB_COMPILER_DEPS) | $(STAND)/.dirs
	mkdir -p $(STAND)/build
	cd '$(REPO_ROOT)' && $(POETRY) run python tools/compile_assembly_yaml.py \
		--spec '$(ORBITRON_ASSEMBLY_SPEC)' --subassembly '$*' --out '$@'

# Stable entry for scripts: main lab glTF + every listed sub-assembly slice (same lab mesh step as fg-ready).
orbitron-lab-gltf: $(GLTF_LAB) $(GLTF_LAB_SUBASSEMBLIES)

orbitron-lab-sub-gltfs: $(GLTF_LAB_SUBASSEMBLIES)

orbitron-lab-tank-sub-gltfs: $(GLTF_LAB_TANK_SUBS)

# 0D jet closure: η·P_gross vs F²/(2ṁ). Optional: ORBITRON_CLOSURE_JSON=$(STAND)/engine_surrogate.json
surrogate-closure:
	cd '$(REPO_ROOT)' && $(POETRY) run python tools/surrogate_closure_check.py \
		$(if $(ORBITRON_CLOSURE_JSON),--surrogate-json '$(ORBITRON_CLOSURE_JSON)',)

# --- Blender + UV → orbitron.ac ---
# Real deps on surrogate + sounds (not only order-only): GNU make may otherwise schedule
# Blender before WarpX / sound_compiler; cold-tree regression must finish PIC + audio first.
$(STAND)/.orbitron_ac_done: \
		$(GLTF_LAB) \
		$(STAND)/engine_surrogate.json \
		$(STAND)/Sounds/.sounds_built \
		$(ORBITRON)/build_ac3d.py \
		$(ORBITRON)/fix_screen_uv.py \
		| $(STAND)/.dirs $(STAND_NASAL)
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
		| $(STAND)/.dirs $(STAND_NASAL)
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
	echo '    y_specs["orbitron_lab.yaml (geometry + logical)"]'; \
	echo '    y_compile["tools/compile_assembly_yaml.py"]'; \
	echo '    y_specs --> y_compile'; \
	echo '    y_compile --> gltf_lab["…/orbitron_lab.gltf"]'; \
	echo '    cq_cad["ssto/orbitron/arcjet_test_stand_cad.py\n+ full_reactor_cad.py"]'; \
	echo '    cq_cad -.->|CadQuery templates| y_compile'; \
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
	echo '    asm_yaml["repo …/orbitron_lab.yaml (logical)"]'; \
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
	echo '    snd_yaml --> snd_xml_py --> a_snd["Aircraft/…/Sounds/sound.xml"]'; \
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
	echo '  subgraph FGAIR["FG aircraft shell (YAML → XML)"]'; \
	echo '    fg_air_yaml["orbitron_aircraft_flightgear.yaml"]'; \
	echo '    fg_air_py["compile_orbitron_aircraft_runtime.py"]'; \
	echo '    fg_jsb_tmpl["tools/templates/orbitron-jsbsim.xml"]'; \
	echo '    fg_air_yaml --> fg_air_py'; \
	echo '    phy2["orbitron_physics_surrogate.yaml"] --> fg_air_py'; \
	echo '    fg_jsb_tmpl --> fg_air_py'; \
	echo '    fg_air_py --> a_set["Aircraft/…/*-set.xml"]'; \
	echo '    fg_air_py --> a_jsb["Aircraft/…/orbitron-jsbsim.xml"]'; \
	echo '    fg_air_py --> a_ox["Aircraft/…/Models/Orbitron.xml"]'; \
	echo '  end'; \
	echo '  subgraph NAS["Nasal (YAML → .nas)"]'; \
	echo '    nas_yaml["orbitron_nasal.yaml"]'; \
	echo '    nas_py["compile_orbitron_nasal.py"]'; \
	echo '    nas_yaml --> nas_py --> a_nas["Aircraft/…/Nasal/*.nas"]'; \
	echo '  end'; \
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
$(PARTS_MERMAID) $(PARTS_LOGICAL_MERMAID) &: $(REPO_ROOT)/tools/orbitron_ac_hierarchy_mmd.py $(STAND)/Models/orbitron.ac $(ORBITRON_MODEL_XML) $(ORBITRON_ASSEMBLY_SPEC) $(ORBITRON_AIRCRAFT_SPEC) $(COMPILE_AIRCRAFT_RUNTIME) $(JSBSIM_TEMPLATE) | $(STAND)/.dirs
	mkdir -p $(STAND)/build
	cd $(REPO_ROOT) && python3 tools/orbitron_ac_hierarchy_mmd.py \
		--ac '$(STAND)/Models/orbitron.ac' \
		--orbitron-xml '$(ORBITRON_MODEL_XML)' \
		--assemblies-spec '$(ORBITRON_ASSEMBLY_SPEC)' \
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
	cd $(REPO_ROOT) && fgfs --fg-aircraft=$(AIRCRAFT) --aircraft=$(ORBITRON_PKG) \
		--airport=BIKF --parkpos=East-Apron-119 --timeofday=noon --ai-traffic=0 \
		--real-weather-fetch=0 --clouds3d=0 \
		--prop:/sim/sound/chatter/volume=0.0 --prop:/sim/sound/atc/volume=0.0 \
		--prop:/instrumentation/comm/volume=0.0

clean:
	rm -rf '$(AIRCRAFT)' '$(BUILD)'
