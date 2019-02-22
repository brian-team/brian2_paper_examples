#include <string>
#include <stdint.h>
#include <unistd.h>
#include <stdlib.h>
#include <stdio.h>

#define CHECK(x) { if(!(x)) { \
fprintf(stderr, "%s:%i: failure at: %s\n", __FILE__, __LINE__, #x); \
_exit(1); } }

int numChannels;
int sampleRate;
int bytesPerSample, bitsPerSample;

std::string freadStr(FILE* f, size_t len) {
    std::string s(len, '\0');
    CHECK(fread(&s[0], 1, len, f) == len);
    return s;
}

template<typename T>
T freadNum(FILE* f) {
    T value;
    CHECK(fread(&value, sizeof(value), 1, f) == 1);
    return value; // no endian-swap for now... WAV is LE anyway...
}

void readFmtChunk(FILE *wavfile, uint32_t chunkLen) {
    CHECK(chunkLen >= 16);
    uint16_t fmttag = freadNum<uint16_t>(wavfile);
    CHECK(fmttag == 1 /*PCM*/);
    numChannels = freadNum<uint16_t>(wavfile);
    CHECK(numChannels == 2);
    sampleRate = freadNum<uint32_t>(wavfile);
    CHECK(sampleRate == 44100);
    uint32_t byteRate = freadNum<uint32_t>(wavfile);
    uint16_t blockAlign = freadNum<uint16_t>(wavfile);
    bitsPerSample = freadNum<uint16_t>(wavfile);
    bytesPerSample = bitsPerSample / 8;
    CHECK(byteRate == sampleRate * numChannels * bytesPerSample);
    CHECK(blockAlign == numChannels * bytesPerSample);
    CHECK(bitsPerSample == 16);
    if(chunkLen > 16) {
        uint16_t extendedSize = freadNum<uint16_t>(wavfile);
        CHECK(chunkLen == 18 + extendedSize);
        fseek(wavfile, extendedSize, SEEK_CUR);
    }
}

void readHeader(FILE *wavfile) {
    CHECK(freadStr(wavfile, 4) == "RIFF");
    uint32_t wavechunksize = freadNum<uint32_t>(wavfile);
    CHECK(freadStr(wavfile, 4) == "WAVE");
    while(true) {
        std::string chunkName = freadStr(wavfile, 4);
        uint32_t chunkLen = freadNum<uint32_t>(wavfile);
        if(chunkName == "fmt ")
            readFmtChunk(wavfile, chunkLen);
        else if(chunkName == "data") {
            CHECK(sampleRate != 0);
            CHECK(numChannels > 0);
            CHECK(bytesPerSample > 0);
            printf("bytesPerSample: %d\n", bytesPerSample);
            printf("len: %.2f secs\n", double(chunkLen) / sampleRate / numChannels / bytesPerSample);
            break; // start playing now
        } else {
            // skip chunk
            CHECK(fseek(wavfile, chunkLen, SEEK_CUR) == 0);
        }
    }
}

FILE *init_file() {
    FILE *wavfile = fopen(FILENAME, "r");  // will be replaced via macro
    readHeader(wavfile);
    return wavfile;
}

float get_sample(const double t) {
    static FILE *wavfile = init_file();
    static int16_t samples[2];
    if (fread(samples, bytesPerSample * numChannels, 1, wavfile) == 0) {
        // end of file
        return 0.0;
    }
    return samples[0]*1.0/32767;
}
