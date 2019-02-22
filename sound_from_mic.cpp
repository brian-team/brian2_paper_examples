#include <string.h>
#include <portaudio.h>
#include <string>
#include <stdint.h>
#include <unistd.h>
#include <stdlib.h>
#include <iostream>

PaStream *_init_stream()
{
    PaStream* stream;
    PaError err;

    err = Pa_Initialize();
    if (err != paNoError)
    {
        std::cerr << "Initializing PortAudio failed with error: " << Pa_GetErrorText(err) << std::endl;
        exit(err);
    }

    err = Pa_OpenDefaultStream(&stream, 1, 0, paFloat32, SAMPLE_RATE, BUFFER_SIZE, NULL, NULL);
    if (err != paNoError)
    {
       std::cerr << "Opening the default input stream failed with error: " << Pa_GetErrorText(err) << std::endl;
       exit(err);
    }

    err = Pa_StartStream(stream);
    if (err != paNoError)
    {
       std::cerr << "Starting the stream failed with error: " << Pa_GetErrorText(err) << std::endl;
       exit(err);
    }

    return stream;
}

float get_sample(const double t)
{
    static PaStream* stream = _init_stream();
    static float buffer[BUFFER_SIZE];
    static int next_sample = BUFFER_SIZE;

    if (next_sample >= BUFFER_SIZE)
    {
        Pa_ReadStream(stream, buffer, BUFFER_SIZE);
        next_sample = 0;
    }
    return buffer[next_sample++];
}

