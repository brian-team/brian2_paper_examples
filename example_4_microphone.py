from brian2 import *
import os

set_device('cpp_standalone', clean=True)


sample_rate = 44.1*kHz
buffer_size = 128
defaultclock.dt = 1/sample_rate
runtime = 4.5*second

# Receptor neurons ("ear")
max_delay = 20*ms # 50 Hz
tau_ear = 1*ms
tau_th = 5*ms
# Coincidence detectors
min_freq = 50*Hz
max_freq = 1000*Hz
num_neurons = 300
tau = 1*ms
sigma = .1

use_microphone = False
if use_microphone:
    # Now comes the connection to the microphone code.
    @implementation('cpp','//actual code in sound_from_mic.cpp',
                    sources=[os.path.abspath('sound_from_mic.cpp')],
                    headers=['"{}"'.format(os.path.abspath('sound_input.h'))],
                    libraries=['portaudio'],
                    define_macros=[('BUFFER_SIZE', buffer_size),
                                   ('SAMPLE_RATE', sample_rate/Hz)])
    @check_units(t=second, result=1)
    def get_sample(t):
        raise NotImplementedError('Use a C++-based code generation target.')
else:
    # Now comes the connection to the microphone code.
    @implementation('cpp','//actual code in sound_from_file.cpp',
                    sources=[os.path.abspath('sound_from_file.cpp')],
                    headers=['"{}"'.format(os.path.abspath('sound_input.h'))],
                    define_macros=[('FILENAME', os.path.abspath('scale_flute.wav'))])
    @check_units(t=second, result=1)
    def get_sample(t):
        raise NotImplementedError('Use a C++-based code generation target.')

gain = 50

# Note that the `get_sample` function does not actually make use of the time `t` that it is given, for simplicity it assumes that it is called only once per time step. This is actually enforced by using our `constant over dt` feature -- the variable `sound` can be used in several places (which is important here, since we want to record it as well):
eqs_ear = '''
dx/dt = (sound - x)/tau_ear: 1 (unless refractory)
dth/dt = (0.1*x - th)/tau_th : 1
sound = clip(get_sample(t), 0, inf) : 1 (constant over dt)
'''
receptors = NeuronGroup(1, eqs_ear, threshold='x>th', reset='x=0; th = th*2.5 + 0.01',
                        refractory=2*ms, method='exact')
receptors.th = 1
sound_mon = StateMonitor(receptors, 'sound', record=0)

eqs_neurons = '''
dv/dt = -v/tau+sigma*(2./tau)**.5*xi : 1
freq : Hz (constant)
'''

neurons = NeuronGroup(num_neurons, eqs_neurons, threshold='v>1', reset='v=0',
                      method='euler')
neurons.freq = 'exp(log(min_freq/Hz)+(i*1.0/(num_neurons-1))*log(max_freq/min_freq))*Hz'
synapses = Synapses(receptors, neurons, on_pre='v += 0.5',
                    multisynaptic_index='k')
synapses.connect(n=2)  # one synapse without delay; one with delay
synapses.delay['k == 1'] = '1/freq_post'

spikes = SpikeMonitor(neurons)

run(runtime, report='text')

plt.style.use('paper_mplstyle.cfg')
f, (ax_sound, ax_spectrogram, ax_spikes) = plt.subplots(3, 1, gridspec_kw={'height_ratios': [1, 2, 2]},
                                                        figsize=(5.35, 5), sharex='col')
ax_sound.plot(sound_mon.t/second, sound_mon.sound[0])
ax_sound.set(ylabel='amplitude', xlim=(0.4, runtime/second),
             title='Raw sound signal', yticks=[])

ax_spectrogram.set_yscale('log')
print(min_freq)
ax_spectrogram.specgram(sound_mon.sound[0], Fs=sample_rate/Hz, NFFT=2**12)
ax_spectrogram.set(ylim=(min_freq/Hz, 500), ylabel='Frequency (Hz)',
                   title='Spectrogram of sound signal')

ax_spikes.set_yscale('log')
ax_spikes.plot(spikes.t/second, neurons.freq[spikes.i]/Hz, '|', color='C0')
ax_spikes.set(xlim=(0.4, runtime/second), ylim=(min_freq/Hz, 500),
              xlabel='Time (s)', ylabel='Preferred\nFrequency (Hz)',
              title='Spiking activity')

plt.tight_layout()
plt.show()
