# -*- coding: utf-8 -*-

## @package fio.srv.FIO32M1
# Блок цифро-аналогового вывода или аналого-цифрового ввода
# @n Функции зарегистрированные через xmlrpc имеют префикс FIO32M1.

import os, time, pdb
from util.socketio import get_fsz
from sg.gui import LMS6002D
from sg.gui.LMS6002D import trxpll_freq, lms_spi_cmd_cb, lms_spi_fmt_cb, rf_mode, rf_init, select_vcocap, trxlpfbw_list, TXVGA1GAIN_src_cb, TXVGA2GAIN_src_cb
from sg.regs import bits_src, list_src
from ctl.srv.SAM7X import SAM7X_telnet as telnet, SAM7X_send_file, SAM7X_recv_file

def FIO32M1_send_file(ip_addr, fname):
    '''
    Записать данные в SDRAM и запустить DMA ЦАП
    @param ip_addr - ip-адрес устройства
    @param fname - имя файла
    @return размер переданного файла
    '''
    fsz = get_fsz(fname)
    FIO32M1_mode(ip_addr, 'tx')
    if SAM7X_send_file(ip_addr, fname, '1', '0'):
        time.sleep(.5)
        assert telnet(ip_addr, 'dma start 2 0x%X' % fsz)
        return '0x%X' % fsz
FIO32M1_send_file.stdout = True

def FIO32M1_recv_file(ip_addr, fname, fsz):
    '''
    Записать данные из АЦП в SDRAM и скачать в файл
    @param ip_addr - ip-адрес устройства
    @param fname - имя файла
    @param fsz - размер данных, лучше в hex (например 0x10000), до 32Mb
    @return fsz
    '''
    FIO32M1_mode(ip_addr, 'rx')
    fsz = get_fsz(None, fsz)
    fsz = '0x%X' % fsz
    assert telnet(ip_addr, 'dma start 3 %s' % fsz)
    time.sleep(.1)
    if SAM7X_recv_file(ip_addr, fname, fsz, '2', '1'):
        return fsz
FIO32M1_recv_file.stdout = True

def FIO32M1_vtune(ip_addr='192.168.0.1'):
    """
    Косвенный идикатор синхронизма передающего и приёмного синтезаторов
    @param ip_addr - ip-адрес устройства
    @return - массив из четырёх цифр: TX VTUNE_H, TX_VTUNE_L, RX VTUNE_H, RX VTUNE_L
    """
    return telnet(ip_addr, 'lms_vtune')

# @cond
def trx_cmd(ip_addr, f, val):
    dev = {'spi':'0'}
    reg_io = lambda r, v=None: lms_spi_fmt_cb(telnet(ip_addr, lms_spi_cmd_cb(dev, r, v)))
    ret = f(reg_io, val)
    return ret
# @endcond

def FIO32M1_mode(ip_addr='192.168.0.1', m='off'):
    """
    Подготовить блок к приёму/передаче данных
    @param ip_addr - ip-адрес устройства
    @param m - строка tx или rx
    @return m
    """
    assert telnet(ip_addr, 'dma stop')
    time.sleep(.1)
    assert telnet(ip_addr, 'led_mode %s' % m)
    trx_cmd(ip_addr, LMS6002D.rf_mode, m)
    return m

def FIO32M1_txfreq(ip_addr, freq=''):
    """
    Чтение/установка частоты передающего синтезатора
    @param ip_addr - ip-адрес устройства
    @param freq - частота при записи, аргумент отсутствует при чтении
    @return freq
    """
    ret = trx_cmd(ip_addr, lambda x,y: trxpll_freq(x,y, '1', refin=30), freq)
    if freq:
        trx_cmd(ip_addr, lambda x, y: select_vcocap(x, y, False), '1')
    return ret

def FIO32M1_txvcocap(ip_addr):
    """
    Подобрать значение подстроечной емкости передающего синтезатора
    @param ip_addr - ip-адрес устройства
    @return vcocap
    """
    return trx_cmd(ip_addr, lambda x, y: select_vcocap(x, y, False), '1')

def FIO32M1_txlpf(ip_addr, bw=''):
    """
    Чтение/установка полосы фильтра передатчика
    @param ip_addr - ip-адрес устройства
    @param bw - полоса фильтра в МГц, диапазон значений:
    @n '14', '10', '7', '6', '5', '4.375', '3.5', '3', '2.75', '2.5', '1.92', '1.5', '1.375', '1.25', '0.875', '0.75'
    @return bw
    """
    return trx_cmd(ip_addr, lambda io,v: list_src(io,'R34',2,5,trxlpfbw_list,v), bw)

def FIO32M1_txvga1(ip_addr, gain=''):
    """
    Чтение/установка усиления vga1
    @param ip_addr - ip-адрес устройства
    @param gain - усиление при записи, аргумент отсутствует при чтении
    @return gain
    """
    return trx_cmd(ip_addr, TXVGA1GAIN_src_cb, gain)

def FIO32M1_txvga2(ip_addr, gain=''):
    """
    Чтение/установка усиления vga2
    @param ip_addr - ip-адрес устройства
    @param gain - усиление при записи, аргумент отсутствует при чтении
    @return gain
    """
    return trx_cmd(ip_addr, TXVGA2GAIN_src_cb, gain)

def FIO32M1_rxfreq(ip_addr, freq=''):
    """
    Чтение/установка частоты синтезатора приёмника
    @param ip_addr - ip-адрес устройства
    @param freq - частота при записи, аргумент отсутствует при чтении
    @return freq
    """
    ret = trx_cmd(ip_addr, lambda x,y: trxpll_freq(x,y, '2', refin=30), freq)
    if freq:
        trx_cmd(ip_addr, lambda x, y: select_vcocap(x, y, False), '2')
    return ret

def FIO32M1_rxvcocap(ip_addr):
    """
    Подобрать значение подстроечной емкости приёмного синтезатора
    @param ip_addr - ip-адрес устройства
    @return vcocap
    """
    return trx_cmd(ip_addr, lambda x, y: select_vcocap(x, y, False), '2')

def FIO32M1_rxlpf(ip_addr, bw=''):
    """
    Чтение/установка полосы фильтра приёмника
    @param ip_addr - ip-адрес устройства
    @param bw - полоса фильтра в МГц, диапазон значений:
    @n '14', '10', '7', '6', '5', '4.375', '3.5', '3', '2.75', '2.5', '1.92', '1.5', '1.375', '1.25', '0.875', '0.75'
    @return bw
    """
    return trx_cmd(ip_addr, lambda io,v: list_src(io,'R54',2,5,trxlpfbw_list,v), bw)

def FIO32M1_rxvga2(ip_addr, gain=None):
    """
    Чтение/установка усиления rxvga2
    @param ip_addr - ip-адрес устройства
    @param gain - усиление при записи, аргумент отсутствует при чтении
    @return gain
    """
    return trx_cmd(ip_addr, lambda io,v: bits_src(io,'R65',0,4,v,coef=3,maximum=30), gain)

def FIO32M1_init(ip_addr, c):
    """
    Запуск калибровочной последовательности
    @param ip_addr - ip-адрес устройства
    @param c - номер калибровочной последовательности:
    @n '1' - DC offset cancellation of the LPF tuning module
    @n '2' - LPF bandwidth tuning
    @n '3' - DC offset cancellation of the TXLPF
    @n '4' - DC offset cancellation of the RXLPF
    @n '5' - DC offset cancellation of the RXVGA2
    @return результат
    """
    return trx_cmd(ip_addr, lambda io, v: rf_init(io, v, refin=30), c)

