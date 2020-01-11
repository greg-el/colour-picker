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


#TODO: fix vbox/hbox with controls in

class UI(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="Pallete")
        self.set_border_width(1)
        self.set_default_size(300, 300)

        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)

        self.vbox = Gtk.VBox()
        self.hbox = Gtk.HBox()

        provider = Gtk.CssProvider()
        button_css = """
                    button {
                        background: rgba(255, 255, 255, 0.5);

                        border: none;
                        border-radius: 0px;
                        outline: none;
                        box-shadow: none;
                    }
                """
        button_css_bytes = bytes(button_css.encode())

        add_color_button = Gtk.Button.new_with_label("+")
        add_color_button.connect("clicked", self.add_color)
        add_color_button.set_size_request(60, 40)

        provider.load_from_data(button_css_bytes)
        add_color_button.get_style_context().add_provider(provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        add_color_button.get_style_context().add_class("button")

        self.hbox.add(add_color_button)




        self.flowbox = Gtk.FlowBox()
        self.flowbox.set_valign(Gtk.Align.START)
        self.flowbox.set_max_children_per_line(8)
        self.flowbox.set_selection_mode(Gtk.SelectionMode.NONE)
        scrolled.add(self.flowbox)

        self.vbox.pack_start(self.hbox, expand=False, fill=False, padding=0)
        self.vbox.pack_start(self.flowbox, expand=True, fill=True, padding=0)


        self.add(self.vbox)


    def add_color(self, button):
        provider = Gtk.CssProvider()
        rgb = get_rgb_at_click()
        button_background = f"rgb({rgb.r}, {rgb.g}, {rgb.b})"
        click_rgb = darken_color(rgb)
        if (rgb.r * 0.299 + rgb.g * 0.587 + rgb.b * 0.114) < 149:
            click_rgb = lighten_color(rgb)

        button_background_clicked = f"rgb({click_rgb.r}, {click_rgb.g}, {click_rgb.b})"
        button_css = f"""
                    button {{
                        background: {button_background};
                        text-shadow: none;
                        border: none;
                        border-radius: 0px;
                        outline: none;
                        box-shadow: none;
                        color: {button_background_clicked}
                    }}
                    button label {{
                        color: {button_background_clicked};
                    }}
                """
        button_css_bytes = bytes(button_css.encode())

        color_button = Gtk.Button.new()
        color_button.set_label(button_background)
        provider.load_from_data(button_css_bytes)
        color_button.get_style_context().add_provider(provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        color_button.get_style_context().add_class("button")
        color_button.set_property("hexpand", False)
        color_button.set_property("width-request", 60)
        color_button.set_property("height-request", 40)
        self.flowbox.add(color_button)
        self.flowbox.show_all()


supports_alpha = False


def screen_changed(widget, old_screen, userdata=None):
    global supports_alpha

    screen = widget.get_screen()
    visual = screen.get_rgba_visual()

    if visual is None:
        visual = screen.get_system_visual()
        supports_alpha = False
    else:
        supports_alpha = True

    widget.set_visual(visual)



def expose_draw(widget, event, userdata=None):
    global supports_alpha

    cr = Gdk.cairo_create(widget.get_window())

    if supports_alpha:
        cr.set_source_rgba(1.0, 1.0, 1.0, 0.0)
        ui.unset_state_flags(Gtk.StateFlags.BACKDROP)
    else:
        cr.set_source_rgb(1.0, 1.0, 1.0)

    cr.set_operator(cairo.OPERATOR_SOURCE)
    cr.paint()

    return False


def clicked(window, event, userdata=None):
    # toggle window manager frames
    window.set_decorated(not window.get_decorated())


class ClickCoordinates:
    def __init__(self, arr):
        self.x = arr[0]
        self.y = arr[1]

    def __str__(self):
        return f'x:{self.x} y:{self.y}'


class RGB:
    def __init__(self, r, g, b):
        self.r = r
        self.g = g
        self.b = b


def lighten_color(rgb):
    r = rgb.r
    g = rgb.b
    b = rgb.b
    color_factor = 70
    if r+color_factor < 255:
        r = r+color_factor
    else:
        r = 255
    if g+color_factor < 255:
        g = g+color_factor
    else:
        g = 255
    if b+color_factor < 255:
        b = b+color_factor
    else:
        b = 255
    return RGB(r, g, b)


def darken_color(rgb):
    r = rgb.r
    g = rgb.b
    b = rgb.b
    color_factor = 100
    if r-color_factor > 0:
        r = r-color_factor
    else:
        r = 0
    if g-color_factor > 0:
        g = g-color_factor
    else:
        g = 0
    if b-color_factor > 0:
        b = b-color_factor
    else:
        b = 0
    return RGB(r, g, b)


def get_rgb_at_click():
    coords = coord.coordinates()
    c = ClickCoordinates([x for x in coords])
    if c.x == -1 and c.y == -1:
        return False
    r = ctypes.c_int(0)
    g = ctypes.c_int(0)
    b = ctypes.c_int(0)
    color.getColor(c.x, c.y, ctypes.byref(r), ctypes.byref(g), ctypes.byref(b))
    return RGB(round(r.value/256), round(g.value/256), round(b.value/256))


def rgb_to_hex(r, g, b):
    return "#{:02x}{:02x}{:02x}".format(r, g, b)


if __name__ == "__main__":
    ui = UI()
    ui.connect("destroy", Gtk.main_quit)

    ui.set_app_paintable(True)
    ui.connect("draw", expose_draw)
    ui.connect("screen-changed", screen_changed)


    ui.set_decorated(False)
    ui.add_events(Gdk.EventMask.BUTTON_PRESS_MASK)
    ui.connect("button-press-event", clicked)

    screen_changed(ui, None, None)

    ui.show_all()
    Gtk.main()
