
#include <iostream>
#include <fstream>
#include <iomanip>

#include <backends/cxxrtl/cxxrtl_vcd.h>

#include "FirEngine.cpp"

using namespace std;

int main(int argc, char **argv)
{
    char *filename;
    int dump_level = 0;

    // <executable> <debug level> <vcd filename> 
    // debug level:
    // 0 -> No dumping, no save/restore
    // 1 -> dump everything
    // 2 -> dump everything except memories
    // 3 -> dump custom (only wires)
    // 4 -> save to checkpoint
    // 5 -> restore from checkpoint

    if (argc >= 2){
        dump_level = atoi(argv[1]);
    }

    if (argc >= 3){
        filename = argv[2];
    } 

    cxxrtl_design::p_FirEngine top;
    cxxrtl::debug_items all_debug_items;
    top.debug_info(all_debug_items);
    cxxrtl::vcd_writer vcd;
    std::ofstream waves;

    if (dump_level >=1 && dump_level <= 3){
        vcd.timescale(1, "us");
        if (dump_level == 1)
            vcd.add(all_debug_items);
        else if (dump_level == 2)
            vcd.add_without_memories(all_debug_items);
        else if (dump_level == 3)
		    vcd.template add(all_debug_items, [](const std::string &, const debug_item &item) {
			    return item.type == debug_item::WIRE;
		    });
        waves.open(filename);
    }


    top.p_clk.set<bool>(true);
    top.p_reset.set<bool>(true);
    top.step();

    if (dump_level >=1 && dump_level <= 3)
        vcd.sample(0);

    top.p_clk.set<bool>(true);
    top.p_reset.set<bool>(true);
    top.step();

    if (dump_level >=1 && dump_level <= 3)
        vcd.sample(0);
    
    top.p_reset.set<bool>(false);

    cxxrtl::debug_item io_data_in_valid     = all_debug_items.at("io_data_in_valid");
    cxxrtl::debug_item io_data_in_payload   = all_debug_items.at("io_data_in_payload");

    int payload_value = 10;

    for(int i=0;i<10000;++i){
        
        if (i%1000 == 500){
            *io_data_in_valid.curr = 1;
            *io_data_in_payload.curr = payload_value;
            payload_value += 20;
        }
        else{
            *io_data_in_valid.curr = 0;
        }

        top.p_clk.set<bool>(false);
        top.step();

//        if (dump_level >=1 && dump_level <= 3)
//            vcd.sample(i*2 + 0);

        top.p_clk.set<bool>(true);
        top.step();

        if (dump_level >= 1 && dump_level <= 3)
            vcd.sample(i*2 + 1);

        if (dump_level >= 1 && dump_level <= 3){
            waves << vcd.buffer;
            vcd.buffer.clear();
        }
    }
}

