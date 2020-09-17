
DESIGN=pdm_test
QUARTUS_DIR = /home/tom/altera/19.1/quartus/bin/

SW_DIR = ../sw

CPU_RAM0 = $(wildcard ./db/*ram0_CCPipelinedMemory*.mif)
CPU_RAM1 = $(wildcard ./db/*ram1_CCPipelinedMemory*.mif)
CPU_RAM2 = $(wildcard ./db/*ram2_CCPipelinedMemory*.mif)
CPU_RAM3 = $(wildcard ./db/*ram3_CCPipelinedMemory*.mif)

CPU_RAMS = $(CPU_RAM0) $(CPU_RAM1) $(CPU_RAM2) $(CPU_RAM3)

all: 
	$(QUARTUS_DIR)/quartus_map --read_settings_files=on --write_settings_files=off $(DESIGN) -c $(DESIGN)
	$(QUARTUS_DIR)/quartus_fit --read_settings_files=on --write_settings_files=off $(DESIGN) -c $(DESIGN)
	$(QUARTUS_DIR)/quartus_asm --read_settings_files=on --write_settings_files=off $(DESIGN) -c $(DESIGN)
	$(QUARTUS_DIR)/quartus_sta $(DESIGN) -c $(DESIGN)

update_ram: sw $(CPU_RAMS)
	$(QUARTUS_DIR)/quartus_cdb $(DESIGN) -c $(DESIGN) --update_mif
	$(QUARTUS_DIR)/quartus_asm --read_settings_files=on --write_settings_files=off $(DESIGN) -c $(DESIGN)

$(CPU_RAM0): $(SW_DIR)/progmem0.mif
	cp $< $@

$(CPU_RAM1): $(SW_DIR)/progmem1.mif
	cp $< $@

$(CPU_RAM2): $(SW_DIR)/progmem2.mif
	cp $< $@

$(CPU_RAM3): $(SW_DIR)/progmem3.mif
	cp $< $@

.PHONY: clean
sw:
	cd $(SW_DIR) && make clean && make
