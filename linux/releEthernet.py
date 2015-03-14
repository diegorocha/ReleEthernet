#!/usr/bin/env python
#-*- coding: UTF-8 -*-

from urllib2 import build_opener
from gi.repository import Gtk
from argparse import ArgumentParser, Action

"""
This class is a interface between Python and the Arduino to controls the relays
"""


class ReleEthernet(object):

    __arduino_ip__ = '192.168.0.10'
    __arduino_host_name__ = 'http://%s' % (__arduino_ip__)

    def __init__(self):
        self.conectado = self.testarComunicacao()

    """
    Return the correct url to perform a command on a relay.
    """

    def _getUrl(self, rele=0, comando=1):
        return '%s/%d%s' % (self.__arduino_host_name__, rele, comando)

    """
    Send a HTTP GET with a command to perform on a relay to Arduino.
    """

    def enviarComando(self, rele=0, comando='1', showReturn=False):
        url = self._getUrl(rele, comando)
        opener = build_opener()
        f = opener.open(url)
        html = f.read()
        f.close()
        if comando == '?' and showReturn:
            print html,
        return html

    """
    """

    def testarComunicacao(self):
        try:
            self.enviarComando(0, '?')
            return True
        except Exception, e:
            return False

    """
    Turn on a relay.
    """

    def ligar(self, rele):
        return self.enviarComando(rele, '1')

    """
    Turn off a relay.
    """

    def desligar(self, rele):
        return self.enviarComando(rele, '0')

    """
    Switch the state of a relay.
    """

    def inverter(self, rele):
        return self.enviarComando(rele, '!')

    """
    Ask Arduino the state of a relay.
    """

    def estado(self, rele):
        return self.enviarComando(rele, '?')

    """
    Return true if the given relay is on, false if relay is off. Otherwise
    raise a Exception.
    """

    def releLigado(self, rele):
        estado = self.estado(rele)
        if 'ERROR' in estado:
            raise Exception('Invalid rele number %d' % (rele))
        return 'ON' in estado
pass

"""
This class is a grapic user interface to control the relays.
"""


class GuiWindow(Gtk.Window):

    def __init__(self, ReleEthernet):
        Gtk.Window.__init__(self, title='Rele Ethernet')
        self.releEthernet = ReleEthernet
        self.set_border_width(10)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_default_size(200, 0)

        hbox = Gtk.Box(spacing=6)
        self.add(hbox)

        listbox = Gtk.ListBox()
        listbox.set_selection_mode(Gtk.SelectionMode.NONE)
        hbox.pack_start(listbox, True, True, 0)

        row = Gtk.ListBoxRow()
        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=30)
        row.add(hbox)

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        hbox.pack_start(vbox, True, True, 0)

        label = Gtk.Label("Lâmpada", xalign=0)
        vbox.pack_start(label, True, True, 0)

        switch = Gtk.Switch()
        switch.props.valign = Gtk.Align.CENTER
        switch.set_active(re.releLigado(0))
        switch.connect('notify::active', self.on_switch_activate, 0)
        hbox.pack_start(switch, False, True, 0)

        listbox.add(row)

    def on_switch_activate(self, widget, gparam, rele):
        if widget.get_active():
            re.ligar(rele)
        else:
            re.desligar(rele)
pass

if __name__ == '__main__':
    re = ReleEthernet()

    argumentParser = ArgumentParser(
        epilog='Author: Diego Rocha <diego@diegorocha.com.br>')
    sub_parser = argumentParser.add_subparsers()

    on_parser = sub_parser.add_parser('on', help='turn on a relay')
    on_parser.set_defaults(command='1', gui=False)

    off_parser = sub_parser.add_parser('off', help='turn off a relay')
    off_parser.set_defaults(command='0', gui=False)

    show_parser = sub_parser.add_parser('show', help='show the relay status')
    show_parser.set_defaults(command='?', gui=False)

    invert_parser = sub_parser.add_parser(
        'invert', help='invert the relay status')
    invert_parser.set_defaults(command='!', gui=False)

    gui_parser = sub_parser.add_parser(
        'gui', help='show a grapic user interface')
    gui_parser.set_defaults(command='', gui=True)

    args = argumentParser.parse_args()

    if args.gui:
        win = GuiWindow(re)
        win.connect("delete-event", Gtk.main_quit)
        win.show_all()
        Gtk.main()
    else:
        if re.conectado:
            re.enviarComando(0, args.command, True)
        else:
            print 'Arduino Not Found'
