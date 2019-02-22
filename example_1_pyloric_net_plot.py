import numpy as np

from plotly import tools
from plotly.offline import iplot, init_notebook_mode
import plotly.graph_objs as go

from brian2.units import second, mV

init_notebook_mode(connected=True)

def do_pyloric_net_plot(spike_trains, times, membrane_potential, varname,
                        init_time, observe_time, adapt_time):
    fig = tools.make_subplots(rows=7, cols=2, shared_xaxes=True, shared_yaxes=True,
                              start_cell='bottom-left', subplot_titles=['initial', 'adapted',
                                                                        '', '', '', '', '', ''],
                             specs=[[{}, {}],
                                    [{'rowspan': 2}, {'rowspan': 2}],
                                    [None, None],
                                    [{'rowspan': 2}, {'rowspan': 2}],
                                    [None, None],
                                    [{'rowspan': 2}, {'rowspan': 2}],
                                    [None, None]],
                             print_grid=False)
    
    traces = []
    before_adaptation = (times>=init_time) & (times < (init_time + observe_time))
    after_adapt_time = init_time + observe_time + adapt_time
    after_adaptation = (times>=after_adapt_time)
    for idx, (label, color) in enumerate(zip(['AB/PD', 'LP', 'PY'],
                                            ['#1f77b4', '#ff7f03', '#2ca02c'])):
        
        trace = go.Scattergl(x=(times[before_adaptation] - init_time) / second,
                           y=membrane_potential[idx][before_adaptation] / mV,
                           marker={'color': color},
                           showlegend=False, name=label)
        fig.append_trace(trace, 2+idx*2, 1)
        if spike_trains is not None:
            spike_times = spike_trains[idx]
            spike_times = spike_times[(spike_times >= init_time) & (spike_times < (init_time + observe_time))]
            spike_trace = go.Scattergl(x=(spike_times - init_time) / second,
                                     y=np.ones(len(spike_times))*(3-idx),
                                     marker={'symbol': 'line-ns', "line": {"width": 2, 'color': color}},
                                     mode='markers', showlegend=False, name=label)
            fig.append_trace(spike_trace, 1, 1)
        trace = go.Scattergl(x=(times[after_adaptation] - after_adapt_time) / second,
                           y=membrane_potential[idx][after_adaptation] / mV,
                           marker={'color': color},
                           name=label)
        fig.append_trace(trace, 2+idx*2, 2)
        if spike_trains is not None:
            spike_times = spike_trains[idx]
            spike_times = spike_times[spike_times >= after_adapt_time]
            spike_trace = go.Scattergl(x=(spike_times - after_adapt_time) / second,
                             y=np.ones(len(spike_times))*(3-idx),
                             marker={'symbol': 'line-ns', "line": {"width": 2, 'color': color}},
                             mode='markers', showlegend=False, name=label)
            fig.append_trace(spike_trace, 1, 2)
    fig['layout'].update(xaxis1={'range': (0, observe_time/second),
                                 'title': 'time (in s)',
                                 'zeroline': False},
                         xaxis2={'range': (0, observe_time/second),
                                 'title': 'time (in s)',
                                 'zeroline': False},
                         yaxis3={'title': 'v (in mV)'},
                         yaxis1={'showline': False,
                                 'showticklabels': False})
    iplot(fig)
