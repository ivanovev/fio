
from collections import OrderedDict as OD
from util.columns import *
from util import Data, Control, Tftp, dev_io_cb, telnet_io_cb

class FileIO(Control):
    def __init__(self, dev, title='File IO'):
        data = Data()
        data.dev = dev
        data.buttons = OD()
        #data.buttons['TX stop'] = self.dma_stop_cb
        self.add_tx_cmds(data, txcrc32=False)
        data.add('txstop', wdgt='button', text='TX stop', click_cb=self.dma_stop_cb)
        self.add_rx_cmds(data)
        Control.__init__(self, data, dev, title=title)
        self.fileext = 'pcm'
        self.center()

    def init_io(self):
        self.io = Tftp(self.data.dev[c_ip_addr], 69, self, 'rxd.pcm', read=False, wnd=self)

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

    def read_cb(self, *args):
        self.io.read = True
        if hasattr(self.io, 'st'):
            if getattr(self.io.st, 'closed', False):
                self.io.st.close()
        if fname:
            fname = self.data.get_value('fname')
            self.io.st = open(fname, 'wb')
            self.io.remotefname = 'rxd.pcm'
            self.io_start()

    def write_cb(self, *args):
        self.io.read = False
        if hasattr(self.io, 'st'):
            if getattr(self.io.st, 'closed', False):
                self.io.st.close()
        if fname:
            fname = self.data.get_value('fname')
            self.io.st = open(fname, 'rb')
            self.io.remotefname = 'txd.pcm'
            self.io_start()

