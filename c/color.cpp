#include <iostream>
#include <X11/Xlib.h>
#include <X11/Xutil.h>
#include <array>

//Compile hint: g++ -shared -Wall -fPIC -Wl,-soname,color -o ../obj/color.so color.cpp -lX11


#ifdef __cplusplus
extern "C"
#endif


void getColor(int x, int y, int *r, int *g, int *b) {
    Display* d = XOpenDisplay((char *)NULL);
    XColor c;
    XImage *image;
    image = XGetImage(d, XRootWindow (d, XDefaultScreen (d)), x, y, 1, 1, AllPlanes, XYPixmap);
    c.pixel = XGetPixel(image,0,0);
    XFree(image);
    XQueryColor (d, XDefaultColormap(d, XDefaultScreen (d)), &c);
    *r = c.red;
    *g = c.green;
    *b = c.blue;
    //unsigned long hex = ((c.red/256 & 0xff) << 16) + ((c.green/256 & 0xff) << 8) + (c.blue/256 & 0xff);
    XCloseDisplay(d);
}
