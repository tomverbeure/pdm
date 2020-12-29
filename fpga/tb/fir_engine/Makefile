

YOSYS			=  yosys
YOSYS_INCLUDE	= $(shell yosys-config --datdir)/include

SRC				= tb.cpp
OBJ 			= 
VERILOG			= ../../spinal/FirEngine.v
MEM_FILES		= ../../spinal/FirEngine.v_toplevel_u_mem.bin

CLANG			= clang++-9

YOSYS_PREPROC = "read_verilog -formal $(VERILOG); hierarchy -check -top FirEngine"
YOSYS_RECIPE  = ""

all: compile
	./tb 2 waves.vcd

.PHONY: compile
compile: \
	tb \

tb: tb.cpp FirEngine.cpp $(SRC) $(OBJ)
	$(CLANG) -g -O3 -std=c++14 -I $(YOSYS_INCLUDE) $(SRC) $(OBJ) -o $@

.PHONY: FirEngine.cpp
FirEngine.cpp:
	cp $(MEM_FILES) .
	$(YOSYS) -l yosys.log -p $(YOSYS_PREPROC) -p $(YOSYS_RECIPE) -p "write_cxxrtl -O6 -g4 $@; write_ilang $@.ilang"

clean: 
	\rm -fr *.bin *.txt *.sim.* example_*_clang* example_*_gcc* example *.vcd
