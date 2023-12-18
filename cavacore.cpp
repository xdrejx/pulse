#include "cavacore.h"
#ifndef M_PI
#define M_PI 3.1415926535897932385
#endif
#include <fftw3.h>
#include <math.h>
#include <stdlib.h>
#include <string.h>

struct cava_plan *cava_init(int number_of_bars, unsigned int rate, int channels, int autosens,
                            double noise_reduction, int low_cut_off, int high_cut_off)
{
    int treble_buffer_size = 128;

    if (rate > 8125 && rate <= 16250)
        treble_buffer_size *= 2;
    else if (rate > 16250 && rate <= 32500)
        treble_buffer_size *= 4;
    else if (rate > 32500 && rate <= 75000)
        treble_buffer_size *= 8;
    else if (rate > 75000 && rate <= 150000)
        treble_buffer_size *= 16;
    else if (rate > 150000 && rate <= 300000)
        treble_buffer_size *= 32;
    else if (rate > 300000)
        treble_buffer_size *= 64;

    p->number_of_bars = number_of_bars;
    p->rate = rate;
    p->autosens = 1;
    p->sens_init = 1;
    p->sens = 1.0;
    p->autosens = autosens;
    p->framerate = 75;
    p->frame_skip = 1;
    p->noise_reduction = noise_reduction;

    p->FFTbassbufferSize = treble_buffer_size * 8;
    p->FFTmidbufferSize = treble_buffer_size * 4;
    p->FFTtreblebufferSize = treble_buffer_size;

    p->input_buffer_size = p->FFTbassbufferSize * channels;

    for (int i = 0; i < p->FFTbassbufferSize; i++)
    {
        p->bass_multiplier[i] = 0.5 * (1 - cos(2 * M_PI * i / (p->FFTbassbufferSize - 1)));
    }
    for (int i = 0; i < p->FFTmidbufferSize; i++)
    {
        p->mid_multiplier[i] = 0.5 * (1 - cos(2 * M_PI * i / (p->FFTmidbufferSize - 1)));
    }
    for (int i = 0; i < p->FFTtreblebufferSize; i++)
    {
        p->treble_multiplier[i] = 0.5 * (1 - cos(2 * M_PI * i / (p->FFTtreblebufferSize - 1)));
    }

    // process: calculate cutoff frequencies and eq
    int lower_cut_off = low_cut_off;
    int upper_cut_off = high_cut_off;
    int bass_cut_off = 100;
    int treble_cut_off = 500;

    // calculate frequency constant (used to distribute bars across the frequency band)
    double frequency_constant = log10((float)lower_cut_off / (float)upper_cut_off) /
                                (1 / ((float)p->number_of_bars + 1) - 1);

    float *relative_cut_off = (float *)malloc((p->number_of_bars + 1) * sizeof(float));

    p->bass_cut_off_bar = -1;
    p->treble_cut_off_bar = -1;
    int first_bar = 1;
    int first_treble_bar = 0;
    int *bar_buffer = (int *)malloc((p->number_of_bars + 1) * sizeof(int));

    for (int n = 0; n < p->number_of_bars + 1; n++)
    {
        double bar_distribution_coefficient = frequency_constant * (-1);
        bar_distribution_coefficient +=
            ((float)n + 1) / ((float)p->number_of_bars + 1) * frequency_constant;
        p->cut_off_frequency[n] = upper_cut_off * pow(10, bar_distribution_coefficient);

        if (n > 0)
        {
            if (p->cut_off_frequency[n - 1] >= p->cut_off_frequency[n] &&
                p->cut_off_frequency[n - 1] > bass_cut_off)
                p->cut_off_frequency[n] =
                    p->cut_off_frequency[n - 1] +
                    (p->cut_off_frequency[n - 1] - p->cut_off_frequency[n - 2]);
        }

        relative_cut_off[n] = p->cut_off_frequency[n] / (p->rate / 2);
        // remember nyquist!, per my calculations this should be rate/2
        // and nyquist freq in M/2 but testing shows it is not...
        // or maybe the nq freq is in M/4

        p->eq[n] = pow(p->cut_off_frequency[n], 1);

        // the numbers that come out of the FFT are verry high
        // the EQ is used to "normalize" them by dividing with this very huge number
        p->eq[n] /= pow(2, 29);

        p->eq[n] /= log2(p->FFTbassbufferSize);

        if (p->cut_off_frequency[n] < bass_cut_off)
        {
            // BASS
            bar_buffer[n] = 1;
            p->FFTbuffer_lower_cut_off[n] = relative_cut_off[n] * (p->FFTbassbufferSize / 2);
            p->bass_cut_off_bar++;
            p->treble_cut_off_bar++;
            if (p->bass_cut_off_bar > 0)
                first_bar = 0;

            if (p->FFTbuffer_lower_cut_off[n] > p->FFTbassbufferSize / 2)
            {
                p->FFTbuffer_lower_cut_off[n] = p->FFTbassbufferSize / 2;
            }
        }
        else if (p->cut_off_frequency[n] > bass_cut_off &&
                 p->cut_off_frequency[n] < treble_cut_off)
        {
            // MID
            bar_buffer[n] = 2;
            p->FFTbuffer_lower_cut_off[n] = relative_cut_off[n] * (p->FFTmidbufferSize / 2);
            p->treble_cut_off_bar++;
            if ((p->treble_cut_off_bar - p->bass_cut_off_bar) == 1)
            {
                first_bar = 1;
                if (n > 0)
                {
                    p->FFTbuffer_upper_cut_off[n - 1] =
                        relative_cut_off[n] * (p->FFTbassbufferSize / 2);
                }
            }
            else
            {
                first_bar = 0;
            }

            if (p->FFTbuffer_lower_cut_off[n] > p->FFTmidbufferSize / 2)
            {
                p->FFTbuffer_lower_cut_off[n] = p->FFTmidbufferSize / 2;
            }
        }
        else
        {
            // TREBLE
            bar_buffer[n] = 3;
            p->FFTbuffer_lower_cut_off[n] = relative_cut_off[n] * (p->FFTtreblebufferSize / 2);
            first_treble_bar++;
            if (first_treble_bar == 1)
            {
                first_bar = 1;
                if (n > 0)
                {
                    p->FFTbuffer_upper_cut_off[n - 1] =
                        relative_cut_off[n] * (p->FFTmidbufferSize / 2);
                }
            }
            else
            {
                first_bar = 0;
            }

            if (p->FFTbuffer_lower_cut_off[n] > p->FFTtreblebufferSize / 2)
            {
                p->FFTbuffer_lower_cut_off[n] = p->FFTtreblebufferSize / 2;
            }
        }

        if (n > 0)
        {
            if (!first_bar)
            {
                p->FFTbuffer_upper_cut_off[n - 1] = p->FFTbuffer_lower_cut_off[n] - 1;

                // pushing the spectrum up if the exponential function gets "clumped" in the
                // bass and caluclating new cut off frequencies
                if (p->FFTbuffer_lower_cut_off[n] <= p->FFTbuffer_lower_cut_off[n - 1])
                {

                    // check if there is room for more first
                    int room_for_more = 0;

                    if (bar_buffer[n] == 1)
                    {
                        if (p->FFTbuffer_lower_cut_off[n - 1] + 1 < p->FFTbassbufferSize / 2 + 1)
                            room_for_more = 1;
                    }
                    else if (bar_buffer[n] == 2)
                    {
                        if (p->FFTbuffer_lower_cut_off[n - 1] + 1 < p->FFTmidbufferSize / 2 + 1)
                            room_for_more = 1;
                    }
                    else if (bar_buffer[n] == 3)
                    {
                        if (p->FFTbuffer_lower_cut_off[n - 1] + 1 < p->FFTtreblebufferSize / 2 + 1)
                            room_for_more = 1;
                    }

                    if (room_for_more)
                    {
                        // push the spectrum up
                        p->FFTbuffer_lower_cut_off[n] = p->FFTbuffer_lower_cut_off[n - 1] + 1;
                        p->FFTbuffer_upper_cut_off[n - 1] = p->FFTbuffer_lower_cut_off[n] - 1;

                        // calculate new cut off frequency
                        if (bar_buffer[n] == 1)
                            relative_cut_off[n] = (float)(p->FFTbuffer_lower_cut_off[n]) /
                                                  ((float)p->FFTbassbufferSize / 2);
                        else if (bar_buffer[n] == 2)
                            relative_cut_off[n] = (float)(p->FFTbuffer_lower_cut_off[n]) /
                                                  ((float)p->FFTmidbufferSize / 2);
                        else if (bar_buffer[n] == 3)
                            relative_cut_off[n] = (float)(p->FFTbuffer_lower_cut_off[n]) /
                                                  ((float)p->FFTtreblebufferSize / 2);

                        p->cut_off_frequency[n] = relative_cut_off[n] * ((float)p->rate / 2);
                    }
                }
            }
            else
            {
                if (p->FFTbuffer_upper_cut_off[n - 1] <= p->FFTbuffer_lower_cut_off[n - 1])
                    p->FFTbuffer_upper_cut_off[n - 1] = p->FFTbuffer_lower_cut_off[n - 1] + 1;
            }
        }
    }
    free(bar_buffer);
    free(relative_cut_off);
    return p;
}

void cava_execute(double *cava_in, int new_samples, double *cava_out, struct cava_plan *p)
{

    // do not overflow
    if (new_samples > p->input_buffer_size)
    {
        new_samples = p->input_buffer_size;
    }

    int silence = 1;
    if (new_samples > 0)
    {
        p->framerate -= p->framerate / 64;
        p->framerate += (double)((p->rate * p->frame_skip) / new_samples) / 64;
        p->frame_skip = 1;
        // shifting input buffer
        for (uint16_t n = p->input_buffer_size - 1; n >= new_samples; n--)
        {
            p->input_buffer[n] = p->input_buffer[n - new_samples];
        }

        // fill the input buffer
        for (uint16_t n = 0; n < new_samples; n++)
        {
            p->input_buffer[new_samples - n - 1] = cava_in[n];
            if (cava_in[n])
            {
                silence = 0;
            }
        }
    }
    else
    {
        p->frame_skip++;
    }

    // fill the bass, mid and treble buffers
    for (uint16_t n = 0; n < p->FFTbassbufferSize; n++)
    {
        p->in_bass_l_raw[n] = p->input_buffer[n];
    }
    for (uint16_t n = 0; n < p->FFTmidbufferSize; n++)
    {
        p->in_mid_l_raw[n] = p->input_buffer[n];
    }
    for (uint16_t n = 0; n < p->FFTtreblebufferSize; n++)
    {
        p->in_treble_l_raw[n] = p->input_buffer[n];
    }

    // Hann Window
    for (int i = 0; i < p->FFTbassbufferSize; i++)
    {
        p->in_bass_l[i] = p->bass_multiplier[i] * p->in_bass_l_raw[i];
    }
    for (int i = 0; i < p->FFTmidbufferSize; i++)
    {
        p->in_mid_l[i] = p->mid_multiplier[i] * p->in_mid_l_raw[i];
    }
    for (int i = 0; i < p->FFTtreblebufferSize; i++)
    {
        p->in_treble_l[i] = p->treble_multiplier[i] * p->in_treble_l_raw[i];
    }

    // process: execute FFT and sort frequency bands

    fftw_execute(p->p_bass_l);
    fftw_execute(p->p_mid_l);
    fftw_execute(p->p_treble_l);

    // process: separate frequency bands
    for (int n = 0; n < p->number_of_bars; n++)
    {
        double temp_l = 0;
        double temp_r = 0;

        // process: add upp FFT values within bands
        for (int i = p->FFTbuffer_lower_cut_off[n]; i <= p->FFTbuffer_upper_cut_off[n]; i++)
        {

            if (n <= p->bass_cut_off_bar)
            {
                temp_l += hypot(p->out_bass_l[i][0], p->out_bass_l[i][1]);
            }
            else if (n > p->bass_cut_off_bar && n <= p->treble_cut_off_bar)
            {
                temp_l += hypot(p->out_mid_l[i][0], p->out_mid_l[i][1]);
            }
            else if (n > p->treble_cut_off_bar)
            {
                temp_l += hypot(p->out_treble_l[i][0], p->out_treble_l[i][1]);
            }
        }

        // getting average multiply with eq
        temp_l /= p->FFTbuffer_upper_cut_off[n] - p->FFTbuffer_lower_cut_off[n] + 1;
        temp_l *= p->eq[n];
        cava_out[n] = temp_l;
    }

    // applying sens or getting max value
    if (p->autosens)
    {
        for (int n = 0; n < p->number_of_bars; n++)
        {
            cava_out[n] *= p->sens;
        }
    }
    // process [smoothing]
    int overshoot = 0;
    double gravity_mod = pow((60 / p->framerate), 2.5) * 1.54 / p->noise_reduction;

    if (gravity_mod < 1)
        gravity_mod = 1;

    for (int n = 0; n < p->number_of_bars; n++)
    {

        // process [smoothing]: falloff

        if (cava_out[n] < p->prev_cava_out[n] && p->noise_reduction > 0.1)
        {
            cava_out[n] =
                p->cava_peak[n] * (1.0 - (p->cava_fall[n] * p->cava_fall[n] * gravity_mod));

            if (cava_out[n] < 0.0)
                cava_out[n] = 0.0;
            p->cava_fall[n] += 0.028;
        }
        else
        {
            p->cava_peak[n] = cava_out[n];
            p->cava_fall[n] = 0.0;
        }
        p->prev_cava_out[n] = cava_out[n];

        // process [smoothing]: integral
        cava_out[n] = p->cava_mem[n] * p->noise_reduction + cava_out[n];
        p->cava_mem[n] = cava_out[n];
        if (p->autosens)
        {
            // check if we overshoot target height
            if (cava_out[n] > 1.0)
            {
                overshoot = 1;
            }
        }
    }

    // calculating automatic sense adjustment
    if (p->autosens)
    {
        if (overshoot)
        {
            p->sens = p->sens * 0.98;
            p->sens_init = 0;
        }
        else
        {
            if (!silence)
            {
                p->sens = p->sens * 1.002;
                if (p->sens_init)
                    p->sens = p->sens * 1.1;
            }
        }
    }
}

void cava_destroy(struct cava_plan *p)
{

    free(p->input_buffer);
    free(p->bass_multiplier);
    free(p->mid_multiplier);
    free(p->treble_multiplier);
    free(p->eq);
    free(p->cut_off_frequency);
    free(p->FFTbuffer_lower_cut_off);
    free(p->FFTbuffer_upper_cut_off);
    free(p->cava_fall);
    free(p->cava_mem);
    free(p->cava_peak);
    free(p->prev_cava_out);

    fftw_free(p->in_bass_l);
    fftw_free(p->in_bass_l_raw);
    fftw_free(p->out_bass_l);
    fftw_destroy_plan(p->p_bass_l);

    fftw_free(p->in_mid_l);
    fftw_free(p->in_mid_l_raw);
    fftw_free(p->out_mid_l);
    fftw_destroy_plan(p->p_mid_l);

    fftw_free(p->in_treble_l);
    fftw_free(p->in_treble_l_raw);
    fftw_free(p->out_treble_l);
    fftw_destroy_plan(p->p_treble_l);
}
