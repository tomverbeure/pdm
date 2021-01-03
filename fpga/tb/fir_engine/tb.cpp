
#include <iostream>
#include <fstream>
#include <iomanip>

#include <backends/cxxrtl/cxxrtl_vcd.h>

#include "FirEngine.cpp"

using namespace std;

typedef struct {
    const char  *name;
    bool        is_halfband;
    int         decimation;
    int         nr_coefs;
    const int   *coefs;
} filter_info_t;

/*
const int hb1_coefs[] = { 1,2,3};

filter_info_t hb1 = {
    "HB1", 
    true,
    10,
    2,
    &hb1_coefs[0]
};

filter_info_t firs = { hb1 };
*/

const int hb1_coefs[] = { 878, -6713, 38602, 65535, 38602, -6713, 878 };
const int hb2_coefs[] = { 94, -723, 3032, -9781, 40145, 65535, 40145, -9781, 3032, -723, 94 };
const int fir_coefs[] = { -14, -50, -84, -49, 117, 349, 423, 108, -518, -932, -518, 737, 1854, 1476, -738, -3193, -3245, 293, 5148, 6520, 1184, -8322, -13605, -5839, 16758, 45494, 65535, 65535, 45494, 16758, -5839, -13605, -8322, 1184, 6520, 5148, 293, -3245, -3193, -738, 1476, 1854, 737, -518, -932, -518, 108, 423, 349, 117, -49, -84, -50, -14 };

filter_info_t hb1_info = {
    "HB1",
    1,
    2,
    7,
    &hb1_coefs[0]
};

filter_info_t hb2_info = {
    "HB2",
    1,
    2,
    11,
    &hb2_coefs[0]
};

filter_info_t fir_info = {
    "FIR",
    0,
    1,
    54,
    &fir_coefs[0]
};


filter_info_t firs[] = { hb1_info, hb2_info, fir_info };


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

    int payload_value = 4096;

    for(int i=0;i<100000;++i){
        
        if (i%42 == 10){
            *io_data_in_valid.curr = 1;
            *io_data_in_payload.curr = payload_value;
        }
        else{
            *io_data_in_valid.curr = 0;
        }

        top.p_clk.set<bool>(false);
        top.step();

        if (dump_level >=1 && dump_level <= 3)
            vcd.sample(i*2 + 0);

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

