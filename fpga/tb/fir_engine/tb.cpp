
#include <iostream>
#include <fstream>
#include <iomanip>

#include <unistd.h>
#include <string.h>
#include <stdio.h>

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

void print_help()
{
    fprintf(stderr, "tb [-h] [-d <dump level>] [-v <vcd file>] [-c <cycles between input samples>] [-i <data input file>] [-o <data output file>]\n"
                    "Default values:\n"
                    "   dump level: 0 (no waves)\n"
                    "   vcd file: waves.vcd\n"
                    "   cycles between input samples: 50\n"
                    "   data input file: none\n"
                    "   data output file: stdout\n"
                    "\n"
                    );
}

char default_vcd_filename[] = "waves.vcd";

int main(int argc, char **argv)
{
    int dump_level = 0;
    char *vcd_filename;
    int cycles_between_samples = 50;
    char *data_in_filename = NULL;
    char *data_out_filename = NULL;
    FILE *data_in_file = NULL;
    FILE *data_out_file = NULL;

    int c;
    opterr = 0;

    vcd_filename = &default_vcd_filename[0];

    while ((c = getopt(argc, argv, "hd:v:c:i:o:")) != -1){
        switch(c){
            case 'h':
                print_help();
                exit(1);
                break;
            case 'd':
                dump_level = atoi(optarg);
                break;
            case 'v': 
                vcd_filename = optarg;
                break;
            case 'c':
                cycles_between_samples = atoi(optarg);
                break;
            case 'i':
                data_in_filename = (char *)malloc(strlen(optarg)+1);
                strcpy(data_in_filename, optarg);
                data_in_file = fopen(data_in_filename, "rt+");
                break;
            case 'o':
                data_out_filename = (char *)malloc(strlen(optarg)+1);
                strcpy(data_out_filename, optarg);
                data_out_file = fopen(data_out_filename, "wt+");
                break;
            case '?': 
                if (optopt == 'd' || optopt == 'v'){
                    fprintf(stderr, "Option -%c requires an argument.\n", optopt);
                }
                else if (isprint(optopt)){
                    fprintf(stderr, "Unknown option `-%c`.\n", optopt);
                }
                else{
                    fprintf(stderr, "Unknown option character `\\x%x'.\n", optopt);
                }
                return 1;
            default: 
                print_help();
                abort();
                break;
        }
    }

    cxxrtl_design::p_FirEngine top;
    cxxrtl::debug_items all_debug_items;
    top.debug_info(all_debug_items);
    cxxrtl::vcd_writer vcd;
    std::ofstream waves;

    if (dump_level >= 1){
        vcd.timescale(1, "us");
        vcd.add_without_memories(all_debug_items);
        waves.open(vcd_filename);
    }


    top.p_clk.set<bool>(true);
    top.p_reset.set<bool>(true);
    top.step();

    if (dump_level >=1)
        vcd.sample(0);

    top.p_clk.set<bool>(true);
    top.p_reset.set<bool>(true);
    top.step();

    if (dump_level >=1)
        vcd.sample(0);
    
    top.p_reset.set<bool>(false);

    cxxrtl::debug_item io_data_in_valid     = all_debug_items.at("io_data_in_valid");
    cxxrtl::debug_item io_data_in_ready     = all_debug_items.at("io_data_in_ready");
    cxxrtl::debug_item io_data_in_payload   = all_debug_items.at("io_data_in_payload");

    cxxrtl::debug_item io_data_out_valid    = all_debug_items.at("io_data_out_valid");
    cxxrtl::debug_item io_data_out_payload  = all_debug_items.at("io_data_out_payload");

    int valid_value     = 0;
    int payload_value   = 0;

    int input_sample_nr = 0;

    bool end_of_sim = false;
    int cycle_cntr = 0;
    int samples_before_done = -1;
    while(!end_of_sim){
        
        if (cycle_cntr % cycles_between_samples == 5){
            valid_value     = 1;

            if (data_in_file){
                if (samples_before_done < 0){
                    int result = fscanf(data_in_file, "%d", &payload_value);
                    if (result == EOF){
                        samples_before_done = 200;
                    }
                }
                else{
                    --samples_before_done;
                }
            }
            else{
                if (input_sample_nr == 200)
                    payload_value = 32767;
                else
                    payload_value = 0;
                ++input_sample_nr;
            }


            *io_data_in_valid.curr      = valid_value;
            *io_data_in_payload.curr    = payload_value;
        }
        else if (*io_data_in_ready.curr && valid_value == 1){
            valid_value             = 0;
            *io_data_in_valid.curr  = valid_value;
        }

        if (*io_data_out_valid.curr == 1){
            int16_t data_out = (*io_data_out_payload.curr);

            if (data_out_file){
                fprintf(data_out_file, "%d\n", data_out);
            }
            else{
                printf("%d\n", data_out);
            }
        }


        top.p_clk.set<bool>(false);
        top.step();

        if (dump_level >=1)
            vcd.sample(cycle_cntr*2 + 0);

        top.p_clk.set<bool>(true);
        top.step();

        if (dump_level >= 1){
            vcd.sample(cycle_cntr*2 + 1);

            waves << vcd.buffer;
            vcd.buffer.clear();
        }

        if (!data_in_file){
            end_of_sim = cycle_cntr == 100000;
        }
        else{
            end_of_sim = samples_before_done == 0;
        }
        ++cycle_cntr;
    }
}

