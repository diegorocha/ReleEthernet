#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from __future__ import print_function
from json import loads
from requests import get
from decouple import config
from argparse import ArgumentParser, Action

try:
    import gi
    gi.require_version('Gtk', '3.0')
    from gi.repository import Gtk
    gtk_loaded = True
except:
    gtk_loaded = False


class ReleEthernet(object):
    """ This class is a interface between Python and the Arduino to controls the relays. """

    __arduino_ip__ = config('arduino_ip', default='192.168.1.118')
    __arduino_host_name__ = config('arduino_host_name', default='http://%s' % (__arduino_ip__))

    def __init__(self):
        self.conectado = self.testarComunicacao()

    """
    Return the correct url to perform a command on a relay.
    """

    def _getUrl(self, rele=0, comando=1):
        if comando == '?':
            # Acerta o parse da URL incluindo um parâmetro qualquer
            comando = '?foo=bar'
        return '%s/%d%s' % (self.__arduino_host_name__, rele, comando)

    """
    Send a HTTP GET with a command to perform on a relay to Arduino.
    """

    def enviarComando(self, rele=0, comando='1', showReturn=False):
        url = self._getUrl(rele, comando)
        r = get(url)
        estado = loads(r.text)
        if showReturn:
            print(estado)
        return estado

    def testarComunicacao(self):
        """ Try to send a command to device. """
        try:
            self.enviarComando(0, '?')
            return True
        except Exception:
            return False

    def ligar(self, rele=0):
        """ Turn on a relay. """
        return self.enviarComando(rele, '1')

    def desligar(self, rele=0):
        """ Turn off a relay. """
        return self.enviarComando(rele, '0')

    def inverter(self, rele=0):
        """ Switch the state of a relay. """
        return self.enviarComando(rele, '!')

    def estado(self, rele=0):
        """ Ask Arduino the state of a relay. """
        return self.enviarComando(rele, '?')

    def releLigado(self, rele=0):
        """ Return true if the given relay is on, false if relay is off. Otherwise
        raise a Exception. """
        estado = self.estado(rele)
        erro = estado.get("error")
        if erro:
            raise Exception(erro)
        return estado["rele"]
pass

if gtk_loaded:
    class GuiWindow(Gtk.Window):
        """
        This class is a grapic user interface to control the relays.
        """

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
            switch.set_active(self.releEthernet.releLigado())
            switch.connect('notify::active', self.on_switch_activate, 0)
            hbox.pack_start(switch, False, True, 0)

            listbox.add(row)

        def on_switch_activate(self, widget, gparam, rele):
            if widget.get_active():
                self.releEthernet.ligar()
            else:
                self.releEthernet.desligar()
    pass


def main():
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
    rele = ReleEthernet()
    if args.gui:
        if gtk_loaded:
            win = GuiWindow(ReleEthernet=rele)
            win.connect("delete-event", Gtk.main_quit)
            win.show_all()
            Gtk.main()
        else:
            print('Could not load GTK')
    else:
        if rele.conectado:
            estado = rele.enviarComando(comando=args.command)
            if '?' in args.command:
                print(estado['rele'])
        else:
            print('Arduino Not Found')

if __name__ == '__main__':
    main()
