#include <iostream>
#include <string>
#include <X11/Xlib.h>
#include <X11/Xutil.h>

struct ClickCoordinates {
    int x;
    int y;
};

unsigned long rgbToHex(int r, int g, int b) {
        return ((r & 0xff) << 16) + ((g & 0xff) << 8) + (b & 0xff);
}

ClickCoordinates coordinates (){
    ClickCoordinates click;
    int x=-1,y=-1;
    XEvent event;
    int button;
    Display *d = XOpenDisplay(NULL);

    if (d == NULL) {
        fprintf(stderr, "Cannot connect to X server!\n");
        exit (EXIT_FAILURE);
    }

    Window root = XDefaultRootWindow(d);
    XGrabPointer(d, root, False, ButtonPressMask, GrabModeAsync,
         GrabModeAsync, None, None, CurrentTime);

    XSelectInput(d, root, ButtonReleaseMask) ;

    while(1){
        XNextEvent(d,&event);
        switch(event.type){
        case ButtonPress:
            switch(event.xbutton.button){
                case Button1:
                    x=event.xbutton.x;
                    y=event.xbutton.y;
                    button=Button1;
                    break;
                default:
                    break;
            }
            break;
        default:
            break;
        }
        if(x>=0 && y>=0)break;
    }
    
    XCloseDisplay(d);
    click.x = x;
    click.y = y;
    return click;
}

int main(int, char**) {
    ClickCoordinates click;
    XColor c;
    Display *d = XOpenDisplay((char *) NULL);

    click = coordinates();
    int x=click.x;  // Pixel x 
    int y=click.y;  // Pixel y

    XImage *image;
    image = XGetImage (d, XRootWindow (d, XDefaultScreen (d)), x, y, 1, 1, AllPlanes, XYPixmap);
    c.pixel = XGetPixel (image, 0, 0);
    XFree (image);
    XQueryColor (d, XDefaultColormap(d, XDefaultScreen (d)), &c);
    unsigned long hex = rgbToHex(c.red/256, c.green/256, c.blue/256);
    std::cout << "#" << std::hex << hex;
    std::cout << "\n";
    return 0;
}



