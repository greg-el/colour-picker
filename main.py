import ctypes
import pyperclip
import sys
import gi
import cairo
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk

coord = ctypes.CDLL('./obj/coords.so')
coord.coordinates.restype = ctypes.c_int * 2

color = ctypes.CDLL('./obj/color.so')
color.getColor.restype = ctypes.POINTER(ctypes.c_int)
color.getColor.argtypes = [ctypes.c_int, ctypes.c_int]


class UI(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="FlowBox")
        self.set_border_width(1)
        self.set_default_size(300, 300)

        header = Gtk.HeaderBar(title="Palette")
        header.props.show_close_button = False
        self.set_titlebar(header)

        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)

        self.flowbox = Gtk.FlowBox()
        self.flowbox.set_valign(Gtk.Align.START)
        self.flowbox.set_max_children_per_line(8)
        self.flowbox.set_selection_mode(Gtk.SelectionMode.NONE)

        add_color_button = Gtk.Button.new_with_label("+")
        add_color_button.set_property("vexpand", False)
        add_color_button.connect("clicked", self.add_color)
        add_color_button.set_size_request(60, 40)

        self.flowbox.add(add_color_button)


        scrolled.add(self.flowbox)


        self.flowbox.set_property("vexpand", False)

        self.add(scrolled)
        self.show_all()
        self.flowbox.opactiy(0.5)

    def add_color(self, button):
        provider = Gtk.CssProvider()
        button_background = "#00ffff"
        button_background_clicked = "#00dede"
        button_css = f"""
                    .button {{
                        background: {button_background};
                        text-shadow: none;
                        border: none;
                        border-radius: 0px;
                        min-height: 40px;
                        min-width: 60px;
                        outline: none;
                        box-shadow: none;
                    }}

                    .button:active {{
                        background: {button_background_clicked};
                    }}
                """
        button_css_bytes = bytes(button_css.encode())

        color_button = Gtk.Button.new_with_label("test")
        color_button.set_property("vexpand", False)
        color_button.set_property("width-request", 60)
        color_button.set_property("height-request", 40)
        provider.load_from_data(button_css_bytes)
        color_button.get_style_context().add_provider(provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        color_button.get_style_context().add_class("button")
        self.flowbox.add(color_button)
        self.show_all()
        print("done")




if __name__ == "__main__":
    ui = UI()
    ui.connect("destroy", Gtk.main_quit)
    ui.show_all()
    Gtk.main()
