#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from __future__ import print_function

from urllib.parse import urljoin

from requests import get
from decouple import config
from argparse import ArgumentParser

try:
    import gi
    gi.require_version('Gtk', '3.0')
    from gi.repository import Gtk
    gtk_loaded = True
except:
    gtk_loaded = False


class ReleEthernet(object):
    """ This class is a interface between Python and the Arduino to controls
    the relays. """

    def __init__(self):
        self.conectado = self.testar_comunicacao()
        self.arduino_ip = config('arduino_ip', default='192.168.0.16')
        self.arduino_host_name = config('arduino_host_name',
                                        default='http://%s' % self.arduino_ip)

    """
    Return the correct url to perform a command on a relay.
    """

    def _get_url(self, rele=0, comando=1):
        if comando == '?':
            # Acerta o parse da URL incluindo um parâmetro qualquer
            comando = '?foo=bar'
        path = '/' + str(rele) + comando
        return urljoin(self.arduino_host_name, path)

    """
    Send a HTTP GET with a command to perform on a relay to Arduino.
    """

    def enviar_comando(self, rele=0, comando='1', show_return=False):
        url = self._get_url(rele, comando)
        r = get(url)
        estado = r.json()
        if show_return:
            print(estado)
        return estado

    def testar_comunicacao(self):
        """ Try to send a command to device. """
        try:
            self.enviar_comando(0, '?')
            return True
        except Exception:
            return False

    def ligar(self, rele=0):
        """ Turn on a relay. """
        return self.enviar_comando(rele, '1')

    def desligar(self, rele=0):
        """ Turn off a relay. """
        return self.enviar_comando(rele, '0')

    def inverter(self, rele=0):
        """ Switch the state of a relay. """
        return self.enviar_comando(rele, '!')

    def estado(self, rele=0):
        """ Ask Arduino the state of a relay. """
        return self.enviar_comando(rele, '?')

    def rele_ligado(self, rele=0):
        """ Return true if the given relay is on, false if relay is off. Otherwise
        raise a Exception. """
        estado = self.estado(rele)
        erro = estado.get("error")
        if erro:
            raise Exception(erro)
        return estado["rele"]


if gtk_loaded:
    class GuiWindow(Gtk.Window):
        """
        This class is a grapic user interface to control the relays.
        """

        def __init__(self, rele_ethernet):
            Gtk.Window.__init__(self, title='Rele Ethernet')
            self.rele_ethernet = rele_ethernet
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
            switch.set_active(self.rele_ethernet.rele_ligado())
            switch.connect('notify::active', self.on_switch_activate, 0)
            hbox.pack_start(switch, False, True, 0)

            listbox.add(row)

        def on_switch_activate(self, widget, gparam, rele):
            if widget.get_active():
                self.rele_ethernet.ligar()
            else:
                self.rele_ethernet.desligar()


def main():
    argument_parser = ArgumentParser(
        epilog='Author: Diego Rocha <diego@diegorocha.com.br>')
    sub_parser = argument_parser.add_subparsers()

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

    args = argument_parser.parse_args()
    rele = ReleEthernet()
    if not args.__dict__:
        print("Two few arguments")
        exit(1)
    if args.gui:
        if gtk_loaded:
            win = GuiWindow(rele_ethernet=rele)
            win.connect("delete-event", Gtk.main_quit)
            win.show_all()
            Gtk.main()
        else:
            print('Could not load GTK')
    else:
        if rele.conectado:
            estado = rele.enviar_comando(comando=args.command)
            if '?' in args.command:
                print(estado['rele'])
        else:
            print('Arduino Not Found')


if __name__ == '__main__':
    main()
