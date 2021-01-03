#! /usr/bin/env python3

import json

import pprint
pp = pprint.PrettyPrinter(indent=4)

with open("pdm_pcm_filters.json", "r") as json_file:
    filters = json.load(json_file)

s_scala     = ""
s_c_coefs   = ""
s_c_structs = ""

nr_coef_bits = 17

for f in filters[1:]:

    max_coef = max(max(f['coefs']), abs(min(f['coefs'])))
    int_coefs = list([ round((coef/max_coef) * ((2**(nr_coef_bits-1))-1)) for coef in f['coefs'] ])

    if 'is_halfband' in f and f['is_halfband']:
        int_coefs = list(filter(lambda e: e[0] % 2 == 0 or e[0] == len(int_coefs)//2, enumerate(int_coefs)))
        int_coefs = [e[1] for e in int_coefs]

    s_scala += "firs += FirFilterInfo(\"%s\", %d, %s, %d, Array[Int](%s))\n" % (
            f['name'], 
            len(f['coefs']) + f['decimation'] * 4,
            "true" if f['is_halfband'] else "false", 
            f['decimation'], 
            ','.join([str(coef) for coef in int_coefs])
            )

    s_c_coefs += "const int %s_coefs[] = { %s };\n" % (f['name'].lower(), ", ".join([str(coef) for coef in int_coefs]))

    s_c_structs += "filter_info_t %s_info = {\n" % (f['name'].lower())
    s_c_structs += "    \"%s\",\n" % (f['name'])
    s_c_structs += "    %d,\n" % f['is_halfband']
    s_c_structs += "    %d,\n" % f['decimation']
    s_c_structs += "    %d,\n" % len(int_coefs)
    s_c_structs += "    &%s_coefs[0]\n" % f['name'].lower()
    s_c_structs += "};\n\n"

s_c_firs    = "filter_info_t firs[] = { %s };\n" % ", ".join([ f['name'].lower() + "_info" for f in filters[1:] ])

print(s_scala)

print(s_c_coefs)

print(s_c_structs)

print(s_c_firs)


