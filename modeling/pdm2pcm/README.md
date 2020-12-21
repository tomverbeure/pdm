
Code to generate the plots and HTML tables for 
[Design of a Multi-Stage PDM to PCM Decimation Pipeline](https://tomverbeure.github.io/2020/12/20/Design-of-a-Multi-Stage-PDM-to-PCM-Decimation-Pipeline.html#coming-up)

Edit the following lines at the top of `pdm2pcm.py` to select which graph or
table to generate:

```
plot_cic_decimation_passband_droop  = False
plot_cic_stages_passband_droop      = False
passband_droop_table                = False
stopband_attenuation_table          = False
passband_stopband_attenuation_table = False
number_of_muls_table                = True
```

Then just execute `./pdm2pcm.py`.

