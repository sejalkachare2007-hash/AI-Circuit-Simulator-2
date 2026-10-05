import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app
from database.models import db, Component, ComponentPin

components_data = [
    # POWER
    {'name': 'AC Voltage Source', 'category': 'POWER', 'default_value': '120', 'unit': 'V', 'pin_configuration': '2 pins (+, -)'},
    {'name': 'Solar Cell', 'category': 'POWER', 'default_value': '5', 'unit': 'V', 'pin_configuration': '2 pins (+, -)'},
    {'name': 'Power Supply', 'category': 'POWER', 'default_value': '12', 'unit': 'V', 'pin_configuration': '2 pins (+, -)'},
    {'name': 'VCC', 'category': 'POWER', 'default_value': '5', 'unit': 'V', 'pin_configuration': '1 pin'},
    {'name': '5V Supply', 'category': 'POWER', 'default_value': '5', 'unit': 'V', 'pin_configuration': '1 pin'},
    {'name': '3.3V Supply', 'category': 'POWER', 'default_value': '3.3', 'unit': 'V', 'pin_configuration': '1 pin'},
    {'name': '12V Supply', 'category': 'POWER', 'default_value': '12', 'unit': 'V', 'pin_configuration': '1 pin'},
    
    # PASSIVE
    {'name': 'Variable Resistor', 'category': 'PASSIVE', 'default_value': '10k', 'unit': 'Ohm', 'pin_configuration': '3 pins'},
    {'name': 'Variable Capacitor', 'category': 'PASSIVE', 'default_value': '100p', 'unit': 'F', 'pin_configuration': '2 pins'},
    {'name': 'Polarized Capacitor', 'category': 'PASSIVE', 'default_value': '10u', 'unit': 'F', 'pin_configuration': '2 pins (+, -)'},
    {'name': 'Transformer', 'category': 'PASSIVE', 'default_value': '1:10', 'unit': '', 'pin_configuration': '4 pins (Primary, Secondary)'},
    {'name': 'Thermistor', 'category': 'PASSIVE', 'default_value': '10k', 'unit': 'Ohm', 'pin_configuration': '2 pins'},
    {'name': 'LDR', 'category': 'PASSIVE', 'default_value': '10k', 'unit': 'Ohm', 'pin_configuration': '2 pins'},

    # DIODES
    {'name': 'RGB LED', 'category': 'DIODES', 'default_value': '', 'unit': '', 'pin_configuration': '4 pins (R, G, B, Common)'},
    {'name': 'Schottky Diode', 'category': 'DIODES', 'default_value': '0.2V', 'unit': 'V', 'pin_configuration': '2 pins (Anode, Cathode)'},
    {'name': 'Photodiode', 'category': 'DIODES', 'default_value': '', 'unit': '', 'pin_configuration': '2 pins (Anode, Cathode)'},
    {'name': 'Varactor Diode', 'category': 'DIODES', 'default_value': '10p', 'unit': 'F', 'pin_configuration': '2 pins (Anode, Cathode)'},
    {'name': 'Bridge Rectifier', 'category': 'DIODES', 'default_value': '', 'unit': '', 'pin_configuration': '4 pins (AC1, AC2, +, -)'},

    # TRANSISTORS
    {'name': 'N-Channel MOSFET', 'category': 'TRANSISTORS', 'default_value': 'IRFZ44N', 'unit': '', 'pin_configuration': '3 pins (Gate, Drain, Source)'},
    {'name': 'P-Channel MOSFET', 'category': 'TRANSISTORS', 'default_value': 'IRF9540', 'unit': '', 'pin_configuration': '3 pins (Gate, Drain, Source)'},
    {'name': 'JFET', 'category': 'TRANSISTORS', 'default_value': '2N5457', 'unit': '', 'pin_configuration': '3 pins (Gate, Drain, Source)'},
    {'name': 'Darlington Transistor', 'category': 'TRANSISTORS', 'default_value': 'TIP120', 'unit': '', 'pin_configuration': '3 pins (Base, Collector, Emitter)'},
    {'name': 'IGBT', 'category': 'TRANSISTORS', 'default_value': '', 'unit': '', 'pin_configuration': '3 pins (Gate, Collector, Emitter)'},

    # SWITCHES_AND_CONTROL
    {'name': 'Toggle Switch', 'category': 'SWITCHES_AND_CONTROL', 'default_value': '', 'unit': '', 'pin_configuration': '3 pins'},
    {'name': 'Slide Switch', 'category': 'SWITCHES_AND_CONTROL', 'default_value': '', 'unit': '', 'pin_configuration': '3 pins'},
    {'name': 'DIP Switch', 'category': 'SWITCHES_AND_CONTROL', 'default_value': '', 'unit': '', 'pin_configuration': '8 pins'},
    {'name': 'Relay', 'category': 'SWITCHES_AND_CONTROL', 'default_value': '5V', 'unit': 'V', 'pin_configuration': '5 pins (Coil1, Coil2, COM, NO, NC)'},
    {'name': 'SPST', 'category': 'SWITCHES_AND_CONTROL', 'default_value': '', 'unit': '', 'pin_configuration': '2 pins'},
    {'name': 'SPDT', 'category': 'SWITCHES_AND_CONTROL', 'default_value': '', 'unit': '', 'pin_configuration': '3 pins'},
    {'name': 'DPDT', 'category': 'SWITCHES_AND_CONTROL', 'default_value': '', 'unit': '', 'pin_configuration': '6 pins'},

    # OUTPUT
    {'name': 'Speaker', 'category': 'OUTPUT', 'default_value': '8', 'unit': 'Ohm', 'pin_configuration': '2 pins (+, -)'},
    {'name': 'DC Motor', 'category': 'OUTPUT', 'default_value': '5V', 'unit': 'V', 'pin_configuration': '2 pins (+, -)'},
    {'name': 'Servo Motor', 'category': 'OUTPUT', 'default_value': '5V', 'unit': 'V', 'pin_configuration': '3 pins (VCC, GND, Signal)'},
    {'name': 'Stepper Motor', 'category': 'OUTPUT', 'default_value': '5V', 'unit': 'V', 'pin_configuration': '4 pins (A+, A-, B+, B-)'},
    {'name': 'RGB Lamp', 'category': 'OUTPUT', 'default_value': '', 'unit': '', 'pin_configuration': '4 pins'},

    # SENSORS
    {'name': 'Temperature Sensor', 'category': 'SENSORS', 'default_value': 'LM35', 'unit': '', 'pin_configuration': '3 pins (VCC, GND, OUT)'},
    {'name': 'IR Sensor', 'category': 'SENSORS', 'default_value': '', 'unit': '', 'pin_configuration': '3 pins (VCC, GND, OUT)'},
    {'name': 'Ultrasonic Sensor', 'category': 'SENSORS', 'default_value': 'HC-SR04', 'unit': '', 'pin_configuration': '4 pins (VCC, Trig, Echo, GND)'},
    {'name': 'PIR Sensor', 'category': 'SENSORS', 'default_value': '', 'unit': '', 'pin_configuration': '3 pins (VCC, OUT, GND)'},
    {'name': 'Gas Sensor', 'category': 'SENSORS', 'default_value': 'MQ-2', 'unit': '', 'pin_configuration': '4 pins (VCC, GND, A0, D0)'},
    {'name': 'Humidity Sensor', 'category': 'SENSORS', 'default_value': 'DHT11', 'unit': '', 'pin_configuration': '3 pins (VCC, DATA, GND)'},
    {'name': 'Sound Sensor', 'category': 'SENSORS', 'default_value': '', 'unit': '', 'pin_configuration': '3 pins (VCC, GND, OUT)'},
    {'name': 'Touch Sensor', 'category': 'SENSORS', 'default_value': '', 'unit': '', 'pin_configuration': '3 pins (VCC, GND, OUT)'},
    {'name': 'Hall Effect Sensor', 'category': 'SENSORS', 'default_value': '', 'unit': '', 'pin_configuration': '3 pins (VCC, GND, OUT)'},

    # ICS
    {'name': '555 Timer', 'category': 'ICS', 'default_value': 'NE555', 'unit': '', 'pin_configuration': '8 pins'},
    {'name': '741 Op-Amp', 'category': 'ICS', 'default_value': 'LM741', 'unit': '', 'pin_configuration': '8 pins'},
    {'name': 'LM358', 'category': 'ICS', 'default_value': 'LM358', 'unit': '', 'pin_configuration': '8 pins'},
    {'name': 'LM324', 'category': 'ICS', 'default_value': 'LM324', 'unit': '', 'pin_configuration': '14 pins'},
    {'name': '7805 Voltage Regulator', 'category': 'ICS', 'default_value': '5V', 'unit': 'V', 'pin_configuration': '3 pins (IN, GND, OUT)'},
    {'name': '7812 Voltage Regulator', 'category': 'ICS', 'default_value': '12V', 'unit': 'V', 'pin_configuration': '3 pins (IN, GND, OUT)'},
    {'name': '7905 Voltage Regulator', 'category': 'ICS', 'default_value': '-5V', 'unit': 'V', 'pin_configuration': '3 pins (IN, GND, OUT)'},

    # DIGITAL_LOGIC
    {'name': 'AND Gate', 'category': 'DIGITAL_LOGIC', 'default_value': '74HC08', 'unit': '', 'pin_configuration': '3 pins (A, B, Y)'},
    {'name': 'OR Gate', 'category': 'DIGITAL_LOGIC', 'default_value': '74HC32', 'unit': '', 'pin_configuration': '3 pins (A, B, Y)'},
    {'name': 'NOT Gate', 'category': 'DIGITAL_LOGIC', 'default_value': '74HC04', 'unit': '', 'pin_configuration': '2 pins (A, Y)'},
    {'name': 'NAND Gate', 'category': 'DIGITAL_LOGIC', 'default_value': '74HC00', 'unit': '', 'pin_configuration': '3 pins (A, B, Y)'},
    {'name': 'NOR Gate', 'category': 'DIGITAL_LOGIC', 'default_value': '74HC02', 'unit': '', 'pin_configuration': '3 pins (A, B, Y)'},
    {'name': 'XOR Gate', 'category': 'DIGITAL_LOGIC', 'default_value': '74HC86', 'unit': '', 'pin_configuration': '3 pins (A, B, Y)'},
    {'name': 'XNOR Gate', 'category': 'DIGITAL_LOGIC', 'default_value': '', 'unit': '', 'pin_configuration': '3 pins (A, B, Y)'},
    {'name': 'Buffer', 'category': 'DIGITAL_LOGIC', 'default_value': '', 'unit': '', 'pin_configuration': '2 pins (A, Y)'},
    {'name': 'Multiplexer', 'category': 'DIGITAL_LOGIC', 'default_value': '', 'unit': '', 'pin_configuration': '4 pins'},
    {'name': 'Demultiplexer', 'category': 'DIGITAL_LOGIC', 'default_value': '', 'unit': '', 'pin_configuration': '4 pins'},
    {'name': 'Encoder', 'category': 'DIGITAL_LOGIC', 'default_value': '', 'unit': '', 'pin_configuration': '6 pins'},
    {'name': 'Decoder', 'category': 'DIGITAL_LOGIC', 'default_value': '', 'unit': '', 'pin_configuration': '6 pins'},
    {'name': 'Flip-Flop', 'category': 'DIGITAL_LOGIC', 'default_value': '', 'unit': '', 'pin_configuration': '5 pins (D, CLK, PR, CLR, Q, Q\')'},
    {'name': 'Counter', 'category': 'DIGITAL_LOGIC', 'default_value': '', 'unit': '', 'pin_configuration': '6 pins'},
    {'name': 'Shift Register', 'category': 'DIGITAL_LOGIC', 'default_value': '74HC595', 'unit': '', 'pin_configuration': '16 pins'},

    # MICROCONTROLLERS
    {'name': 'Arduino Uno', 'category': 'MICROCONTROLLERS', 'default_value': '', 'unit': '', 'pin_configuration': 'Many pins'},
    {'name': 'Arduino Mega', 'category': 'MICROCONTROLLERS', 'default_value': '', 'unit': '', 'pin_configuration': 'Many pins'},
    {'name': 'Arduino Nano', 'category': 'MICROCONTROLLERS', 'default_value': '', 'unit': '', 'pin_configuration': 'Many pins'},
    {'name': 'ESP32', 'category': 'MICROCONTROLLERS', 'default_value': '', 'unit': '', 'pin_configuration': 'Many pins'},
    {'name': 'ESP8266', 'category': 'MICROCONTROLLERS', 'default_value': '', 'unit': '', 'pin_configuration': 'Many pins'},
    {'name': 'Raspberry Pi', 'category': 'MICROCONTROLLERS', 'default_value': '', 'unit': '', 'pin_configuration': '40 pins'},
    {'name': 'Raspberry Pi Pico', 'category': 'MICROCONTROLLERS', 'default_value': '', 'unit': '', 'pin_configuration': '40 pins'},

    # CONNECTORS
    {'name': '2-Pin Connector', 'category': 'CONNECTORS', 'default_value': '', 'unit': '', 'pin_configuration': '2 pins'},
    {'name': '3-Pin Connector', 'category': 'CONNECTORS', 'default_value': '', 'unit': '', 'pin_configuration': '3 pins'},
    {'name': '4-Pin Connector', 'category': 'CONNECTORS', 'default_value': '', 'unit': '', 'pin_configuration': '4 pins'},
    {'name': 'Header', 'category': 'CONNECTORS', 'default_value': '', 'unit': '', 'pin_configuration': 'Many pins'},
    {'name': 'Terminal Block', 'category': 'CONNECTORS', 'default_value': '', 'unit': '', 'pin_configuration': '2 pins'},
    {'name': 'Jack', 'category': 'CONNECTORS', 'default_value': '', 'unit': '', 'pin_configuration': '3 pins'},
    {'name': 'USB Connector', 'category': 'CONNECTORS', 'default_value': '', 'unit': '', 'pin_configuration': '4 pins'},

    # MEASUREMENT
    {'name': 'Voltmeter', 'category': 'MEASUREMENT', 'default_value': '', 'unit': '', 'pin_configuration': '2 pins (+, -)'},
    {'name': 'Ammeter', 'category': 'MEASUREMENT', 'default_value': '', 'unit': '', 'pin_configuration': '2 pins (+, -)'},
    {'name': 'Multimeter', 'category': 'MEASUREMENT', 'default_value': '', 'unit': '', 'pin_configuration': '2 pins (+, -)'},
    {'name': 'Oscilloscope', 'category': 'MEASUREMENT', 'default_value': '', 'unit': '', 'pin_configuration': '2 pins (CH1, GND)'},
    {'name': 'Logic Analyzer', 'category': 'MEASUREMENT', 'default_value': '', 'unit': '', 'pin_configuration': 'Many pins'},
    {'name': 'Function Generator', 'category': 'MEASUREMENT', 'default_value': '', 'unit': '', 'pin_configuration': '2 pins (OUT, GND)'},

    # DISPLAY
    {'name': '7-Segment Display', 'category': 'DISPLAY', 'default_value': '', 'unit': '', 'pin_configuration': '10 pins'},
    {'name': 'LCD 16x2', 'category': 'DISPLAY', 'default_value': '', 'unit': '', 'pin_configuration': '16 pins'},
    {'name': 'LCD 20x4', 'category': 'DISPLAY', 'default_value': '', 'unit': '', 'pin_configuration': '16 pins'},
    {'name': 'OLED Display', 'category': 'DISPLAY', 'default_value': '', 'unit': '', 'pin_configuration': '4 pins (VCC, GND, SCL, SDA)'},
    {'name': 'LED Matrix', 'category': 'DISPLAY', 'default_value': '', 'unit': '', 'pin_configuration': 'Many pins'},
    {'name': 'Dot Matrix', 'category': 'DISPLAY', 'default_value': '', 'unit': '', 'pin_configuration': 'Many pins'},

    # AUDIO
    {'name': 'Microphone', 'category': 'AUDIO', 'default_value': '', 'unit': '', 'pin_configuration': '2 pins (+, -)'},
    {'name': 'Audio Jack', 'category': 'AUDIO', 'default_value': '', 'unit': '', 'pin_configuration': '3 pins (Tip, Ring, Sleeve)'},

    # COMMUNICATION
    {'name': 'Bluetooth Module', 'category': 'COMMUNICATION', 'default_value': 'HC-05', 'unit': '', 'pin_configuration': '4 pins (VCC, GND, TX, RX)'},
    {'name': 'Wi-Fi Module', 'category': 'COMMUNICATION', 'default_value': '', 'unit': '', 'pin_configuration': 'Many pins'},
    {'name': 'GSM Module', 'category': 'COMMUNICATION', 'default_value': '', 'unit': '', 'pin_configuration': 'Many pins'},
    {'name': 'GPS Module', 'category': 'COMMUNICATION', 'default_value': '', 'unit': '', 'pin_configuration': '4 pins (VCC, GND, TX, RX)'},
    {'name': 'RF Module', 'category': 'COMMUNICATION', 'default_value': '', 'unit': '', 'pin_configuration': '4 pins'},
    {'name': 'IR Receiver', 'category': 'COMMUNICATION', 'default_value': '', 'unit': '', 'pin_configuration': '3 pins (VCC, GND, OUT)'},
    {'name': 'IR Transmitter', 'category': 'COMMUNICATION', 'default_value': '', 'unit': '', 'pin_configuration': '2 pins (Anode, Cathode)'},

    # ELECTROMECHANICAL
    {'name': 'Solenoid', 'category': 'ELECTROMECHANICAL', 'default_value': '12V', 'unit': 'V', 'pin_configuration': '2 pins (+, -)'},
    {'name': 'Fan', 'category': 'ELECTROMECHANICAL', 'default_value': '12V', 'unit': 'V', 'pin_configuration': '2 pins (+, -)'},
]

# Update existing components categories where needed, to make them consistent
updates = [
    ('Battery', 'POWER'),
    ('DC Voltage Source', 'POWER'),
    ('Ground', 'POWER'),
    ('Resistor', 'PASSIVE'),
    ('Capacitor', 'PASSIVE'),
    ('Inductor', 'PASSIVE'),
    ('Potentiometer', 'PASSIVE'),
    ('LED', 'DIODES'),
    ('Diode', 'DIODES'),
    ('Zener Diode', 'DIODES'),
    ('Switch', 'SWITCHES_AND_CONTROL'),
    ('Push Button', 'SWITCHES_AND_CONTROL'),
    ('NPN Transistor', 'TRANSISTORS'),
    ('PNP Transistor', 'TRANSISTORS'),
    ('Lamp', 'OUTPUT'),
    ('Buzzer', 'OUTPUT'),
    ('Motor', 'OUTPUT')
]

expected_pins = {
    'AC Voltage Source': ['positive', 'negative'],
    'Solar Cell': ['positive', 'negative'],
    'Power Supply': ['positive', 'negative'],
    'VCC': ['pin1'],
    '5V Supply': ['pin1'],
    '3.3V Supply': ['pin1'],
    '12V Supply': ['pin1'],
    
    'Variable Resistor': ['pin1', 'pin2', 'wiper'],
    'Variable Capacitor': ['pin1', 'pin2'],
    'Polarized Capacitor': ['positive', 'negative'],
    'Transformer': ['pri1', 'pri2', 'sec1', 'sec2'],
    'Thermistor': ['pin1', 'pin2'],
    'LDR': ['pin1', 'pin2'],

    'RGB LED': ['red', 'green', 'blue', 'common'],
    'Schottky Diode': ['anode', 'cathode'],
    'Photodiode': ['anode', 'cathode'],
    'Varactor Diode': ['anode', 'cathode'],
    'Bridge Rectifier': ['ac1', 'ac2', 'positive', 'negative'],

    'N-Channel MOSFET': ['gate', 'drain', 'source'],
    'P-Channel MOSFET': ['gate', 'drain', 'source'],
    'JFET': ['gate', 'drain', 'source'],
    'Darlington Transistor': ['base', 'collector', 'emitter'],
    'IGBT': ['gate', 'collector', 'emitter'],

    'Toggle Switch': ['pin1', 'common', 'pin2'],
    'Slide Switch': ['pin1', 'common', 'pin2'],
    'DIP Switch': ['in1', 'out1', 'in2', 'out2', 'in3', 'out3', 'in4', 'out4'],
    'Relay': ['coil1', 'coil2', 'com', 'no', 'nc'],
    'SPST': ['pin1', 'pin2'],
    'SPDT': ['com', 'no', 'nc'],
    'DPDT': ['com1', 'no1', 'nc1', 'com2', 'no2', 'nc2'],

    'Speaker': ['positive', 'negative'],
    'DC Motor': ['positive', 'negative'],
    'Servo Motor': ['vcc', 'gnd', 'signal'],
    'Stepper Motor': ['a+', 'a-', 'b+', 'b-'],
    'RGB Lamp': ['red', 'green', 'blue', 'common'],

    'Temperature Sensor': ['vcc', 'gnd', 'out'],
    'IR Sensor': ['vcc', 'gnd', 'out'],
    'Ultrasonic Sensor': ['vcc', 'trig', 'echo', 'gnd'],
    'PIR Sensor': ['vcc', 'out', 'gnd'],
    'Gas Sensor': ['vcc', 'gnd', 'a0', 'd0'],
    'Humidity Sensor': ['vcc', 'data', 'gnd'],
    'Sound Sensor': ['vcc', 'gnd', 'out'],
    'Touch Sensor': ['vcc', 'gnd', 'out'],
    'Hall Effect Sensor': ['vcc', 'gnd', 'out'],

    '555 Timer': ['gnd', 'trig', 'out', 'reset', 'ctrl', 'thr', 'disch', 'vcc'],
    '741 Op-Amp': ['offset_n1', 'in_inv', 'in_noninv', 'v_neg', 'offset_n2', 'out', 'v_pos', 'nc'],
    'LM358': ['out1', 'in1_inv', 'in1_noninv', 'gnd', 'in2_noninv', 'in2_inv', 'out2', 'vcc'],
    'LM324': ['out1', 'in1_inv', 'in1_noninv', 'vcc', 'in2_noninv', 'in2_inv', 'out2', 'out3', 'in3_inv', 'in3_noninv', 'gnd', 'in4_noninv', 'in4_inv', 'out4'],
    '7805 Voltage Regulator': ['in', 'gnd', 'out'],
    '7812 Voltage Regulator': ['in', 'gnd', 'out'],
    '7905 Voltage Regulator': ['in', 'gnd', 'out'],

    'AND Gate': ['a', 'b', 'y'],
    'OR Gate': ['a', 'b', 'y'],
    'NOT Gate': ['a', 'y'],
    'NAND Gate': ['a', 'b', 'y'],
    'NOR Gate': ['a', 'b', 'y'],
    'XOR Gate': ['a', 'b', 'y'],
    'XNOR Gate': ['a', 'b', 'y'],
    'Buffer': ['a', 'y'],
    'Multiplexer': ['d0', 'd1', 's', 'y'],
    'Demultiplexer': ['d', 's', 'y0', 'y1'],
    'Encoder': ['d0', 'd1', 'd2', 'd3', 'a', 'b'],
    'Decoder': ['a', 'b', 'd0', 'd1', 'd2', 'd3'],
    'Flip-Flop': ['d', 'clk', 'pr', 'clr', 'q', 'q_inv'],
    'Counter': ['clk', 'reset', 'q0', 'q1', 'q2', 'q3'],
    'Shift Register': ['ser', 'oe', 'rclk', 'srclk', 'srclr', 'qh_prime', 'qa', 'qb', 'qc', 'qd', 'qe', 'qf', 'qg', 'qh'],

    'Arduino Uno': ['5v', 'gnd', 'vin', 'a0', 'a1', 'd0', 'd1', 'd2'],
    'Arduino Mega': ['5v', 'gnd', 'vin', 'a0', 'a1', 'd0', 'd1', 'd2'],
    'Arduino Nano': ['5v', 'gnd', 'vin', 'a0', 'a1', 'd0', 'd1', 'd2'],
    'ESP32': ['3v3', 'gnd', 'vin', 'en', 'vp', 'vn', 'd34', 'd35'],
    'ESP8266': ['3v3', 'gnd', 'tx', 'rx', 'd1', 'd2', 'd3', 'd4'],
    'Raspberry Pi': ['5v', '3v3', 'gnd', 'gpio2', 'gpio3', 'gpio4'],
    'Raspberry Pi Pico': ['vbus', 'vsys', 'gnd', '3v3_en', '3v3', 'gp0', 'gp1', 'gp2'],

    '2-Pin Connector': ['pin1', 'pin2'],
    '3-Pin Connector': ['pin1', 'pin2', 'pin3'],
    '4-Pin Connector': ['pin1', 'pin2', 'pin3', 'pin4'],
    'Header': ['pin1', 'pin2', 'pin3', 'pin4'],
    'Terminal Block': ['pin1', 'pin2'],
    'Jack': ['tip', 'ring', 'sleeve'],
    'USB Connector': ['vbus', 'd-', 'd+', 'gnd'],

    'Voltmeter': ['positive', 'negative'],
    'Ammeter': ['positive', 'negative'],
    'Multimeter': ['positive', 'negative'],
    'Oscilloscope': ['ch1', 'gnd'],
    'Logic Analyzer': ['ch1', 'ch2', 'ch3', 'ch4', 'gnd'],
    'Function Generator': ['out', 'gnd'],

    '7-Segment Display': ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'dp', 'com1', 'com2'],
    'LCD 16x2': ['vss', 'vdd', 'v0', 'rs', 'rw', 'e', 'd0', 'd1', 'd2', 'd3', 'd4', 'd5', 'd6', 'd7', 'a', 'k'],
    'LCD 20x4': ['vss', 'vdd', 'v0', 'rs', 'rw', 'e', 'd0', 'd1', 'd2', 'd3', 'd4', 'd5', 'd6', 'd7', 'a', 'k'],
    'OLED Display': ['vcc', 'gnd', 'scl', 'sda'],
    'LED Matrix': ['r1', 'r2', 'r3', 'c1', 'c2', 'c3'],
    'Dot Matrix': ['r1', 'r2', 'r3', 'c1', 'c2', 'c3'],

    'Microphone': ['positive', 'negative'],
    'Audio Jack': ['tip', 'ring', 'sleeve'],

    'Bluetooth Module': ['vcc', 'gnd', 'tx', 'rx'],
    'Wi-Fi Module': ['vcc', 'gnd', 'tx', 'rx'],
    'GSM Module': ['vcc', 'gnd', 'tx', 'rx'],
    'GPS Module': ['vcc', 'gnd', 'tx', 'rx'],
    'RF Module': ['vcc', 'gnd', 'data', 'ant'],
    'IR Receiver': ['vcc', 'gnd', 'out'],
    'IR Transmitter': ['anode', 'cathode'],

    'Solenoid': ['positive', 'negative'],
    'Fan': ['positive', 'negative'],
}

def seed_expanded():
    with app.app_context():
        # Update existing component categories
        for name, new_cat in updates:
            comp = Component.query.filter_by(name=name).first()
            if comp:
                comp.category = new_cat
        db.session.commit()
        
        components_added = 0
        for comp_data in components_data:
            existing = Component.query.filter_by(name=comp_data['name']).first()
            if not existing:
                comp = Component(**comp_data)
                db.session.add(comp)
                components_added += 1
        db.session.commit()
        print(f"Added {components_added} new components.")
        
        # Add pins for new components
        pins_added = 0
        for comp_name, pins in expected_pins.items():
            comp = Component.query.filter_by(name=comp_name).first()
            if comp:
                # Check if pins already exist
                existing_pins = ComponentPin.query.filter_by(component_id=comp.id).count()
                if existing_pins == 0:
                    for i, pin_name in enumerate(pins):
                        new_pin = ComponentPin(
                            component_id=comp.id,
                            pin_number=i+1,
                            pin_name=pin_name,
                            pin_type='IO'
                        )
                        db.session.add(new_pin)
                        pins_added += 1
        db.session.commit()
        print(f"Added {pins_added} pins.")

if __name__ == '__main__':
    seed_expanded()
