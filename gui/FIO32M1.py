
from collections import OrderedDict as OD

from util import Data, alarm_trace_cb, dev_io_cb, process_cb
from util.mainwnd import control_cb, monitor_cb
from sg.gui import LMS6002D
from ..tools import FileIO

def trx_cmd_cb(dev, cmd, val=None):
    ip_addr = dev['ip_addr']
    cmd = ' '.join(['.'.join([dev['type'], cmd]), ip_addr])
    if val != None:
        cmd = ' '.join([cmd, val])
    return cmd

def startup_cb(apps, mode, dev):
    if mode == 'fileio':
        return FileIO(dev=dev)

def get_menu(dev):
    menus = OD([('Control', control_cb), ('Monitor', monitor_cb)])
    menus['File IO'] = lambda dev: process_cb('fileio', dev)
    return menus

def get_ctrl_menu(dev):
    menu = LMS6002D.get_menu2()
    mm = menu['Mode']
    k0 = list(mm.keys())[0]
    mm[k0] = lambda wnd, m: wnd.cmdio(dev_io_cb(wnd.data.dev, 'mode %s' % m))
    mv = menu['VCOCAP']
    k0 = list(mv.keys())[0]
    mv[k0] = lambda wnd, m: wnd.cmdio(dev_io_cb(wnd.data.dev, 'txvcocap'))
    k1 = list(mv.keys())[1]
    mv[k0] = lambda wnd, m: wnd.cmdio(dev_io_cb(wnd.data.dev, 'rxvcocap'))
    '''
    mi = menu['Init']
    ki = list(mi.keys())
    for i in range(0, len(ki)):
        #mi[ki[i]] = lambda wnd, i=i: server.call(wnd.dev, '.'.join([dev['type'], 'init']), dev['ip_addr'], '%d' % (i+1,))
        mi[ki[i]] = lambda wnd, i=i: wnd.async_call('.'.join([dev['type'], 'init']), dev['ip_addr'], '%d' % (i+1,))
    '''
    menu.pop('Init')
    return menu
    
def get_ctrl(dev):
    ctrl = Data(io_cb=dev_io_cb)
    ctrl.add_page('TX', send=True)
    ctrl.add('txfreq', label='Frequency, MHz', wdgt='spin', value={'min':232.5, 'max':3720, 'step':0.01}, text='1000')
    ctrl.add('txlpf', label='LPF, MHz', wdgt='combo', value=LMS6002D.trxlpfbw_list, state='readonly', text='14')
    ctrl.add('txvga1', label='VGA1 Gain, dB', wdgt='spin', value={'min':-35, 'max':-4, 'step':1})
    ctrl.add('txvga2', label='VGA2 Gain, dB', wdgt='spin', value={'min':0, 'max':25, 'step':1})
    ctrl.add_page('RX', send=True)
    ctrl.add('rxfreq', label='Frequency, MHz', wdgt='spin', value={'min':232.5, 'max':3720, 'step':0.01})
    ctrl.add('rxlpf', label='LPF, MHz', wdgt='combo', value=LMS6002D.trxlpfbw_list, state='readonly')
    ctrl.add('rxvga2', label='VGA2 Gain, dB', wdgt='spin', value={'min':0, 'max':30, 'step':3})

    ctrl.menu = get_ctrl_menu(dev)
    #dev['spi'] = '0'
    return ctrl

def vtune_fmt_cb(val, read=True, index=0):
    if read:
        if val == '0':
            return '0'
        vv = val.split()
        if len(vv) == 4:
            return vv[index]
        return '1'

def get_mntr(dev):
    mntr = Data(name='mntr', send=True, io_cb=dev_io_cb)
    #mntr.add('temp', wdgt='entry', msg='Temperature')
    #am('dma0', 'DMA0')
    #am('dma1', 'DMA1')
    #am('dma2', 'DMA2')
    #am('dma3', 'DMA3')
    avti=lambda k,msg,i,send=False: mntr.add(k,wdgt='alarm',cmd='vtune',send=send,msg=msg,fmt_cb=lambda val,read: vtune_fmt_cb(val,read,i),trace_cb=alarm_trace_cb)
    avti('txvtuneh', 'TX VTUNE_H', 0, True)
    avti('txvtunel', 'TX VTUNE_L', 1)
    avti('rxvtuneh', 'TX VTUNE_H', 2)
    avti('rxvtunel', 'TX VTUNE_L', 3)
    return mntr

