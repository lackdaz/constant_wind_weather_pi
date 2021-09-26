#include <Arduino.h>

#define adcPin PIN_PA4

#define __default_oversampleBits 4
#define __default_sampleHz 1

#define version "1.01"

uint8_t overSampleBits = __default_oversampleBits;
uint16_t overSampleCount = (1 << __default_oversampleBits);
uint32_t subSamplePeriodMicros = (1000000UL / (overSampleCount * __default_sampleHz));
uint32_t sampleAccumulator = 0;
uint32_t tLastSubSample = 0;
uint16_t subSampleCounter = 0;

#define api_maxArgs 16
uint8_t argBuf[api_maxArgs];
uint8_t argVal = 0;
uint8_t argPtr = 0;
uint8_t argCycle = 0;

float sampleRateHz = __default_sampleHz;

void parseChar(char byte);
void cmd_setOverSampleBits(uint8_t numBits);
void cmd_setSampleRateHz(float hz);

void recomputeTiming();

void performSubSample();

void exportAccumulator();

void parseMessage();

void setup()
{
    pinMode(adcPin, INPUT);
    Serial.begin(115200);
    cmd_setOverSampleBits(__default_oversampleBits);
    cmd_setSampleRateHz(__default_sampleHz);
}

void cmd_setSampleRateHz(float hz)
{
    sampleRateHz = hz;
    recomputeTiming();
}

void recomputeTiming()
{
    subSamplePeriodMicros = 1000000UL / (sampleRateHz * overSampleCount);
}

void cmd_setOverSampleBits(uint8_t numBits)
{
    overSampleBits = numBits;
    overSampleCount = (uint16_t)1 << numBits;
    recomputeTiming();
}

void loop()
{
    if (Serial.available())
    {
        while (Serial.available())
        {
            char c = Serial.read();
            parseChar(c);
        }
    }
    else
    {
        uint32_t tNow = micros();
        uint32_t tD = tNow - tLastSubSample;
        if (tD >= subSamplePeriodMicros)
        {
            tLastSubSample = tNow;
            performSubSample();
        }
    }
}

void performSubSample()
{
    uint16_t v = analogRead(adcPin);
    sampleAccumulator += v;
    subSampleCounter++;
    if (subSampleCounter >= overSampleCount)
    {
        exportAccumulator();
        sampleAccumulator = 0;
        subSampleCounter = 0;
    }
}

void exportAccumulator()
{
    Serial.print("Sample: ");
    Serial.println(sampleAccumulator, DEC);
}

void parseChar(char byte)
{
    if (argPtr < api_maxArgs)
    {
        switch (argCycle)
        {
        case 0:
        case 1:
        {
            // accept any number or hex digit
            if ((byte >= 0x30) && (byte <= 0x39))
            {
                argVal <<= 4;
                argVal |= (byte - 0x30);
                argCycle++;
            }
            else if ((byte >= 'A') && (byte <= 'F'))
            {
                argVal <<= 4;
                argVal |= (byte - 55);
                argCycle++;
            }
            else if ((byte >= 'a') && (byte <= 'f'))
            {
                argVal <<= 4;
                argVal |= (byte - 87);
                argCycle++;
            }
            else
            {
                // garbage input
                argCycle = 3;
            }
        }
        break;
        case 2:
        {
            // expecing space or end of line
            argBuf[argPtr++] = argVal;
            if ((byte == 0x20) || (byte == ','))
            {
                argCycle = 0;
                argVal = 0;
            }
        }
        break;
        }
    }

    if (byte == 0x0a)
    {
        // end of message
        parseMessage();
        argPtr = 0;
        argCycle = 0;
        argVal = 0;
    }
}

void parseMessage()
{
    uint8_t mode = argBuf[0];
    switch (mode)
    {
    case 0x00: // NOP / reserved
    {
    }
    break;
    case 0x01: // get version
    {
        Serial.print("Ver ");
        Serial.println(version);
    }
    break;
    case 0x02: // set oversample bits
    {
        cmd_setOverSampleBits(argBuf[1]);
    }
    break;
    case 0x03: // set samplerate Hz
    {
        uint16_t v = argBuf[1];
        v <<= 8;
        v |= argBuf[2];
        if (v > 0)
        {
            float hz = (float)v / 256;
            cmd_setSampleRateHz(hz);
        }
    }
    break;
    }
}
