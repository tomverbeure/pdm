#include <stdint.h>

#include "reg.h"
#include "top_defines.h"

void wait(int cycles)
{
    volatile int cnt = 0;

    for(int i=0;i<cycles/20;++i){
        ++cnt;
    }
}

#define WAIT_CYCLES 4000000

int main() 
{

    REG_WR(LED_DIR, 0xff);

    while(1){
        REG_WR(LED_WRITE, 0x01);
        wait(WAIT_CYCLES);
        REG_WR(LED_WRITE, 0x02);
        wait(WAIT_CYCLES);
        REG_WR(LED_WRITE, 0x04);
        wait(WAIT_CYCLES);
    }

    while(1);
}
