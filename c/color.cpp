#include <iostream>
#include <X11/Xlib.h>
#include <X11/Xutil.h>
#include <array>

//Compile hint: g++ -shared -Wall -fPIC -Wl,-soname,color -o ../obj/color.so color.cpp -lX11


#ifdef __cplusplus
extern "C"
#endif

unsigned long rgbToHex(int r, int g, int b) {
        return ((r & 0xff) << 16) + ((g & 0xff) << 8) + (b & 0xff);
}

unsigned long hex(int x, int y) {
    Display* d = XOpenDisplay((char *)NULL);
    XColor c;
    XImage *image;
    image = XGetImage (d, XRootWindow (d, XDefaultScreen (d)), x, y, 1, 1, AllPlanes, XYPixmap);
    c.pixel = XGetPixel(image,0,0);
    XFree (image);
    XQueryColor (d, XDefaultColormap(d, XDefaultScreen (d)), &c);
    unsigned long hex = rgbToHex(c.red, c.green, c.blue);
    XCloseDisplay(d);
    return hex;
}
