#include <iostream>
#include <string>
#include <X11/Xlib.h>
#include <X11/Xutil.h>

Display* d = XOpenDisplay((char *)NULL);
int s = DefaultScreen(d);
Window win = XCreateSimpleWindow(d, DefaultRootWindow(d), 0, 0, 320, 200, 1, WhitePixel(d, s), WhitePixel(d, s));

struct ClickCoordinates {
    int x;
    int y;
};

struct PalletColor { //TODO
    GC gc_color;
    XGCValues gc_values;
    int createColor() {
        gc_values.function = GXcopy;
        gc_values.plane_mask = AllPlanes;
        gc_values.foreground = hex;
        gc_color = XCreateGC(d, win, GCFunction | GCPlaneMask | GCForeground, &gc_values);
    }
};

unsigned long rgbToHex(int r, int g, int b) {
        return ((r & 0xff) << 16) + ((g & 0xff) << 8) + (b & 0xff);
}

ClickCoordinates coordinates (){
    int x=-1,y=-1;
    int button;
    ClickCoordinates click;
    XEvent event;


    if (d == NULL) {
        fprintf(stderr, "Cannot connect to X server!\n");
        exit (EXIT_FAILURE);
    }

    Window root = XDefaultRootWindow(d);
    XGrabPointer(d, root, False, ButtonPressMask, GrabModeAsync,
         GrabModeAsync, None, None, CurrentTime);

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


    click.x = x;
    click.y = y;
    XCloseDisplay(d);
    return click;
}

int main(int, char**) {
    ClickCoordinates click;
    XColor c;
    Window w;
    GC gc;
    XEvent event;

    Window root = XDefaultRootWindow(d);
    XGCValues gc_values;
    GC gc_box;

    
    click = coordinates();
    int x=click.x;  // Pixel x 
    int y=click.y;  // Pixel y

    XImage *image;
    image = XGetImage (d, XRootWindow (d, XDefaultScreen (d)), x, y, 1, 1, AllPlanes, XYPixmap);
    c.pixel = XGetPixel (image, 0, 0);
    XFree (image);
    XQueryColor (d, XDefaultColormap(d, XDefaultScreen (d)), &c);
    unsigned long hex = rgbToHex(c.red/256, c.green/256, c.blue/256);

    XSelectInput(d, root, ButtonReleaseMask | ExposureMask);
    XSelectInput(d, win, ButtonReleaseMask | ExposureMask);
    gc = XCreateGC(d, win, 0, 0);

    gc_values.function = GXcopy;
    gc_values.plane_mask = AllPlanes;
    gc_values.foreground = hex;
    gc_box = XCreateGC(d, win, GCFunction | GCPlaneMask | GCForeground, &gc_values);
    
    XClearWindow(d, win);
    XMapRaised(d, win);
    XMapWindow(d, win);
    std::cout << "#" << std::hex << hex;
    std::cout << "\n";
    
    while (1) {
        XNextEvent(d, &event);
        switch(event.type){
            case Expose:
                XFillRectangle(d, win, gc_box, 20, 20, 30, 30);
                break;
            case ButtonPress:
                switch(event.xbutton.button){
                    case Button1:
                        XCloseDisplay(d);
                        XFreeGC(d, gc);
                        XDestroyWindow(d, win);
                        return 0;
                        break;
                    default:
                        break;
                }
                break;
            default:
                break;
        }
    }


}



