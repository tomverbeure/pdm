
YOSYS			=  yosys
YOSYS_INCLUDE	= $(shell yosys-config --datdir)/include

SRC				= tb.cpp
OBJ 			= 
VERILOG			= ../../spinal/PdmTestTop.v
MEM_FILES		= ../../spinal/PdmTestTop.v_toplevel_cpu_u_cpu_u_cpu_ram_ram_symbol0.bin \
				../../spinal/PdmTestTop.v_toplevel_cpu_u_cpu_u_cpu_ram_ram_symbol1.bin 	\
				../../spinal/PdmTestTop.v_toplevel_cpu_u_cpu_u_cpu_ram_ram_symbol2.bin	\
				../../spinal/PdmTestTop.v_toplevel_cpu_u_cpu_u_cpu_ram_ram_symbol3.bin	\
				../../spinal/PdmTestTop.v_toplevel_fir_u_fir_engine_u_mem.bin

#MEM_FILES		= ../../spinal/PdmTestTop.v_toplevel_cpu_u_cpu_u_cpu_ram_ram_symbol0.bin	\ 
#				../../spinal/PdmTestTop.v_toplevel_cpu_u_cpu_u_cpu_ram_ram_symbol1.bin	\ 
#				../../spinal/PdmTestTop.v_toplevel_cpu_u_cpu_u_cpu_ram_ram_symbol2.bin	\
#				../../spinal/PdmTestTop.v_toplevel_cpu_u_cpu_u_cpu_ram_ram_symbol3.bin	\ 
#				../../spinal/PdmTestTop.v_toplevel_fir_u_fir_engine_u_mem.bin

CLANG			= clang++

YOSYS_PREPROC = "read_verilog $(VERILOG); hierarchy -check -top PdmTestTop"
YOSYS_RECIPE  = ""

all: compile
	./tb -d 2 -v waves.vcd

.PHONY: compile
compile: tb

tb: tb.cpp PdmTestTop.cpp $(SRC) $(OBJ)
	$(CLANG) -g -O3 -std=c++14 -I $(YOSYS_INCLUDE) $(SRC) $(OBJ) -o $@

tb_v: tb.v $(VERILOG)
	iverilog $^ -o $@

PdmTestTop.cpp: $(VERILOG)
	cp $(MEM_FILES) .
	$(YOSYS) -l yosys.log -p $(YOSYS_PREPROC) -p $(YOSYS_RECIPE) -p "write_cxxrtl -O6 -g4 $@; write_ilang $@.ilang"

clean: 
	\rm -fr *.bin *.txt *.sim.* example_*_clang* example_*_gcc* example *.vcd tb PdmTestTop.cpp* *.svg *.log
