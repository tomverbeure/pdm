
#ifndef TOP_DEFINES_H
#define TOP_DEFINES_H

//============================================================
// Timer
//============================================================

//== TIMER PRESCALER

#define TIMER_PRESCALER_LIMIT_ADDR  0x00000000

#define TIMER_PRESCALER_LIMIT_VALUE_FIELD_START         0
#define TIMER_PRESCALER_LIMIT_VALUE_FIELD_LENGTH        16

//== TIMER IRQ

#define TIMER_IRQ_STATUS_ADDR       0x00000010

#define TIMER_IRQ_STATUS_PENDING_FIELD_START            0
#define TIMER_IRQ_STATUS_PENDING_FIELD_LENGTH           2

#define TIMER_IRQ_MASK_ADDR         0x00000014

#define TIMER_IRQ_MASK_VALUE_FIELD_START                0
#define TIMER_IRQ_MASK_VALUE_FIELD_LENGTH               2

//== TIMERS

#define TIMER_A_CONFIG_ADDR         0x00000040

#define TIMER_A_CONFIG_TICKS_ENABLE_FIELD_START         0
#define TIMER_A_CONFIG_TICKS_ENABLE_FIELD_LENGTH        16

#define TIMER_A_CONFIG_CLEARS_ENABLE_FIELD_START        16
#define TIMER_A_CONFIG_CLEARS_ENABLE_FIELD_LENGTH       16

#define TIMER_A_LIMIT_ADDR          0x00000044

#define TIMER_A_LIMIT_VALUE_FIELD_START                 0
#define TIMER_A_LIMIT_VALUE_FIELD_LENGTH                32

#define TIMER_A_VALUE_ADDR          0x00000048

#define TIMER_A_VALUE_VALUE_FIELD_START                 0
#define TIMER_A_VALUE_VALUE_FIELD_LENGTH                32

#define TIMER_B_CONFIG_ADDR         0x00000050

#define TIMER_B_CONFIG_TICKS_ENABLE_FIELD_START         0
#define TIMER_B_CONFIG_TICKS_ENABLE_FIELD_LENGTH        16

#define TIMER_B_CONFIG_CLEARS_ENABLE_FIELD_START        16
#define TIMER_B_CONFIG_CLEARS_ENABLE_FIELD_LENGTH       16

#define TIMER_B_LIMIT_ADDR          0x00000054

#define TIMER_B_LIMIT_VALUE_FIELD_START                 0
#define TIMER_B_LIMIT_VALUE_FIELD_LENGTH                32

#define TIMER_B_VALUE_ADDR          0x00000058

#define TIMER_B_VALUE_VALUE_FIELD_START                 0
#define TIMER_B_VALUE_VALUE_FIELD_LENGTH                32

//============================================================
// LEDs
//============================================================

#define LED_READ_ADDR               0x00010000
#define LED_WRITE_ADDR              0x00010004
#define	LED_DIR_ADDR                0x00010008


#endif
