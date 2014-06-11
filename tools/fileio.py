
from collections import OrderedDict as OD
from util import Data, dev_io_cb, telnet_io_cb
from util.io import MyIO
from util.dataio import DataIO
from util.columns import *

class FileIO(DataIO):
    def __init__(self, dev, title='File IO'):
        data = Data()
        data.dev = dev
        data.buttons = OD()
        #data.buttons['TX stop'] = self.dma_stop_cb
        self.add_tx_cmds(data, txmd5=False)
        data.add('txstop', wdgt='button', text='TX stop', click_cb=self.dma_stop_cb)
        self.add_rx_cmds(data)
        DataIO.__init__(self, data, dev, title=title)
        self.fileext = 'pcm'
        self.center()

    def init_io(self):
        del self.io[:]
        self.io.add(self.fio_cb1, self.tmp_cb2, lambda: False, self.cmdio_thread)
        self.io.add(self.tmp_cb1, self.tmp_cb2, self.tmp_cb3, self.cmdio_thread)

    def fio_cb1(self):
        fsz = self.dataio_get_fsz()
        if fsz % 0x200:
            print('file size must be multiple of 1k')
            return False
        fname = self.data.get_value('fname')
        dev = self.data.dev
        if self.read:
            cmd = dev_io_cb(dev, 'recv_file %s 0x%X' % (fname, fsz))
            return self.tmp_cb1(cmd)
        else:
            cmd = dev_io_cb(dev, 'send_file %s' % fname)
            return self.tmp_cb1(cmd)

    def dma_stop_cb(self, *args):
        self.cmdio(telnet_io_cb(self.data.dev, 'dma stop'), index=1)

