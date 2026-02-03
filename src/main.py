# Raspberry Pi Pico With Heart Rate Monitoring System, Laitteisto_2_Project

# Completed by group_4: Besart Gashi, Konsta Hovivuori, Lauri Karhu

from piotimer import Piotimer as Timer
from ssd1306 import SSD1306_I2C
from machine import Pin, ADC, I2C, PWM
from fifo import Fifo
import utime
import array
import time

# OLED Screen
i2c = I2C(1, scl = Pin(15), sda = Pin(14))
oled = SSD1306_I2C(128, 64, i2c)

# Rotary Encoder
push_rotator = Pin(12, mode = Pin.IN, pull = Pin.PULL_UP)

# ADC
adc = ADC(26)

# Menu selection and switch
mode = 0
count = 0
switch_state = 0

# LED
led_onboard = Pin("LED", Pin.OUT)
led21 = PWM(Pin(21))
led21.freq(1000)

# Sample Rate
sample_rate = 250
samples = Fifo(32)

def read_adc(tid):
    x = adc.read_u16()
    samples.put(x)

def press_to_start():
    oled.fill(0)
    oled.text("Press to start", 4, 7, 1)
    oled.text("the measurement", 4, 17, 1)
    oled.show()

def PPI_calculator(data): # Pulse to Pulse Interval
    sum_PPI = 0 
    for i in data:
        sum_PPI += i
    rounded_PPI = round(sum_PPI/len(data), 0)
    return int(rounded_PPI)

def HR_calculator(PPI): # Heart rate
    HR_rounded = round(60*1000/PPI, 0)
    return int(HR_rounded)

def SDNN_calculator(data, PPI): # Standard Deviation of NN Intervals
    summary = 0
    for i in data:
        summary += (i-PPI)**2
    SDNN = (summary/(len(data)-1))**(1/2)
    rounded_SDNN = round(SDNN, 0)
    return int(rounded_SDNN)

def RMSSD_calculator(data): # Root Mean Square of Successive Differences
    i = 0
    summary = 0
    while i < len(data)-1:
        summary += (data[i+1]-data[i])**2
        i +=1
    rounded_RMSSD = round((summary/(len(data)-1))**(1/2), 0)
    return int(rounded_RMSSD)

avg_size = 128
buffer = array.array('H',[0]*avg_size)

while True:
    press_to_start()
    new_state = push_rotator.value()

    if new_state != switch_state:
        count += 1
        if count > 3:
            if new_state == 0:
                if mode == 0:
                    mode = 1
                else:
                    mode = 0
                led_onboard.value(1)
                time.sleep(0.15)
                led_onboard.value(0)
            switch_state = new_state
            count = 0
    else:
        count = 0
    utime.sleep(0.01)
    
    if mode == 1:
        count = 0
        switch_state = 0

        oled.fill(0)
        oled.show()
        
        x1 = -1
        y1 = 32
        m0 = 65535 / 2
        a = 1 / 10

        disp_div = sample_rate / 25
        disp_count = 0
        capture_length = sample_rate * 30

        index = 0
        capture_count = 0
        subtract_old_sample = 0
        sample_sum = 0

        minimum_bpm = 30
        maximum_bpm = 200
        sample_peak = 0
        sample_index = 0
        previous_peak = 0
        previous_index = 0
        interval_ms = 0
        PPI_array = []
        
        brightness = 0

        tmr = Timer(freq = sample_rate, callback = read_adc)
  
        while capture_count < capture_length:
            if not samples.empty():
                x = samples.get()
                disp_count += 1
        
                if disp_count >= disp_div:
                    disp_count = 0
                    m0 = (1 - a) * m0 + a * x
                    y2 = int(32 * (m0 - x) / 14000 + 35)
                    y2 = max(10, min(53, y2))
                    x2 = x1 + 1
                    oled.fill(0)
                
                    if len(PPI_array) > 3:
                        PPI_actual = PPI_calculator(PPI_array)
                        HR_actual = HR_calculator(PPI_actual)
                        oled.text(f'HR:{HR_actual}', 2, 1, 1)
                        oled.text(f'PPI:{interval_ms}', 2, 20, 1)
                    oled.text(f'Timer:  {int(capture_count/sample_rate)}s', 2, 55, 1)
                    oled.show()
                    x1 = x2
                    if x1 > 127:
                        x1 = -1
                    

                if subtract_old_sample:
                    old_sample = buffer[index]
                else:
                    old_sample = 0
                sample_sum = sample_sum + x - old_sample

         

                if subtract_old_sample:
                    sample_avg = sample_sum / avg_size
                    sample_val = x
                    if sample_val > (sample_avg * 1.05):
                        if sample_val > sample_peak:
                            sample_peak = sample_val
                            sample_index = capture_count

                    else:
                        if sample_peak > 0:
                            if (sample_index - previous_index) > (60 * sample_rate / minimum_bpm):
                                previous_peak = 0
                                previous_index = sample_index
                            else:
                                if sample_peak >= (previous_peak*0.8):
                                    if (sample_index - previous_index) > (60 * sample_rate / maximum_bpm):
                                        if previous_peak > 0:
                                            interval = sample_index - previous_index
                                            interval_ms = int(interval * 1000 / sample_rate)
                                            PPI_array.append(interval_ms)
                                            brightness = 5
                                            led21.duty_u16(4000)
                                        previous_peak = sample_peak
                                        previous_index = sample_index
                        sample_peak = 0

                    if brightness > 0:
                        brightness -= 1
                    else:
                        led21.duty_u16(0)

                buffer[index] = x
                capture_count += 1
                index += 1
                if index >= avg_size:
                    index = 0
                    subtract_old_sample = 1

        tmr.deinit()
        
        while not samples.empty():
            x = samples.get()

        oled.fill(0)
        if len(PPI_array) >= 3:
    
            PPI = PPI_calculator(PPI_array)
            HR = HR_calculator(PPI)
            SDNN = SDNN_calculator(PPI_array, PPI)
            RMSSD = RMSSD_calculator(PPI_array)
         
            oled.text('PPI:'+ str(int(PPI)) +'ms', 0, 0, 1)
            oled.text('HR:'+ str(int(HR)) +'bpm', 0, 9, 1)
            oled.text('SDNN:'+str(int(SDNN)) +'ms', 0, 18, 1)
            oled.text('RMSSD:'+str(int(RMSSD)) +'ms', 0, 27, 1)
        else:
            oled.text('Error', 45, 10, 1)
            oled.text('restart', 8, 30, 1)
            oled.text('measurement', 20, 40, 1)
        oled.show()
        
        while mode == 1:
            new_state = push_rotator.value()
            if new_state != switch_state:
                count += 1
                if count > 3:
                    if new_state == 0:
                        if mode == 0:
                            mode = 1
                        else:
                            mode = 0
                        led_onboard.value(1)
                        time.sleep(0.15)
                        led_onboard.value(0)
                    switch_state = new_state
                    count = 0
            else:
                count = 0
            utime.sleep(0.01)
