#include <iostream>
#include <X11/Xlib.h>
#include <X11/Xutil.h>
#include <array>

//Compile hint: g++ -shared -Wall -fPIC -Wl,-soname,color -o color.so color.cpp -lX11

#ifdef __cplusplus
extern "C"
#endif

std::array<unsigned int, 3>rgb(int x, int y) {
    std::array<unsigned int, 3> rgbOutput;
    Display* d = XOpenDisplay((char *)NULL);
    XColor c;
    XImage *image;
    image = XGetImage (d, XRootWindow (d, XDefaultScreen (d)), x, y, 1, 1, AllPlanes, XYPixmap);
    c.pixel = XGetPixel(image,0,0);
    XFree (image);
    XQueryColor (d, XDefaultColormap(d, XDefaultScreen (d)), &c);
    rgbOutput[0] = c.red/256;
    rgbOutput[1] = c.green/256;
    rgbOutput[2] = c.blue/256;
    std::cout << rgbOutput[2];
    return rgbOutput;
}

