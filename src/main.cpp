#include <Arduino.h>

// --- Defines ---
#define ANALOG_PIN_1 PIN_A2      // Analog input pin 1
#define ANALOG_PIN_2 PIN_A3      // Analog input pin 2
#define R1 10.0                  // Resistor 1 value for voltage divider
#define R2 1.0                   // Resistor 2 value for voltage divider
#define VOLTAGE_DIVIDER_RATIO ((R1 + R2) / R2)  // Calculate the ratio
#define ALPHA 0.5                // Smoothing factor for the filter 
#define ADC_LEVEL_RESOLUTION 4095.0    // ADC resolution (12 bits)
#define VREF 3.3                 // ADC reference voltage

// --- Function Declarations ---
float ADCtoVoltage(int adc_value, float ratio = VOLTAGE_DIVIDER_RATIO);
float lowPassFilter(float value, float *filteredValue, float alpha); 
void analogCalibrate();
void printData(float voltage1, float voltage2, const char* format); // Function to print data

// --- Global Variables ---
float voltage1 = 0;      
float voltage2 = 0;      

void setup() {
  Serial.begin(9600);
  analogReadResolution(12);
  pinMode(ANALOG_PIN_1, INPUT_PULLDOWN);
  pinMode(ANALOG_PIN_2, INPUT_PULLDOWN);

  analogCalibrate(); 

  // Initialize voltage1 and voltage2 without filtering
  voltage1 = ADCtoVoltage(analogRead(ANALOG_PIN_1));  
  voltage2 = ADCtoVoltage(analogRead(ANALOG_PIN_2)); 
}

// --- Function Definitions ---

float lowPassFilter(float value, float *filteredValue, float alpha) {
  *filteredValue = alpha * value + (1 - alpha) * (*filteredValue);  
  return *filteredValue;
}

float ADCtoVoltage(int adc_value, float ratio) {
  return adc_value * (VREF / ADC_LEVEL_RESOLUTION) * ratio; 
}

void loop() {
  // Read the raw ADC values and convert to voltage
  float rawVoltage1 = ADCtoVoltage(analogRead(ANALOG_PIN_1));
  float rawVoltage2 = ADCtoVoltage(analogRead(ANALOG_PIN_2));

  // Apply the filter 
  voltage1 = lowPassFilter(rawVoltage1, &voltage1, ALPHA); 
  voltage2 = lowPassFilter(rawVoltage2, &voltage2, ALPHA); 

  // Print the filtered voltages using the printData function
  printData(voltage1, voltage2, "A2:%f A3:%f\n"); // Example format

  delay(1000); 
}

void analogCalibrate() {
  ADC1->CR |= ADC_CR_ADCAL; 
  while (ADC1->CR & ADC_CR_ADCAL); 
}

// --- Print Data Function ---
void printData(float voltage1, float voltage2, const char* format) {
  Serial.printf(format, voltage1, voltage2); 
}