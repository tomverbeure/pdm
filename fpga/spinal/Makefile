
all: syn

.PHONY: submodule
submodule:
	cd ../ && git submodule update --init

.PHONY: sw
sw:
	cd ../sw && make


syn: submodule sw
	sbt "runMain pdm.PdmTestTopVerilogSyn"

sim: submodule sw
	sbt "runMain pdm.PdmTestTopVerilogSim"

sim_spdif:
	sbt "runMain pdm.SpdifVerilogSim"

fir:
	sbt "runMain pdm.FirEngineTopVerilogSim"

