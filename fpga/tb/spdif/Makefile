
YOSYS			= yosys
YOSYS_INCLUDE	= $(shell yosys-config --datdir)/include

all: sim

waves: sim
	gtkwave waves.vcd waves.gtkw

sim: tb
	./tb

tb: main.cpp SpdifOut.cpp
	clang++ -g -std=c++14 -I $(YOSYS_INCLUDE) $< -o $@

SpdifOut.cpp: ../../spinal/SpdifOut.v
	$(YOSYS) -p "read_verilog $<; write_cxxrtl -Og $@"


clean:
	\rm -f SpdifOut.cpp tb *.vcd
