#include <X11/Xlib.h>
#include <iostream>
#include <array>
//Compile hint: ++ -shared -Wall -fPIC -Wl,-soname,coords -o soords.so coords.cpp -lX11

#ifdef __cplusplus
extern "C"
#endif

std::array<int, 2> coordinates (){
    std::array<int, 2> coords;
    Display* d = XOpenDisplay((char *)NULL);
    int x=-1,y=-1;

    XEvent event;


    if (d == NULL) {
        fprintf(stderr, "Cannot connect to X server!\n");
        exit (EXIT_FAILURE);
    }

    Window root = XDefaultRootWindow(d);
    ::XGrabPointer(d, root, False, ButtonPressMask, GrabModeAsync,
         GrabModeAsync, None, None, CurrentTime);

    while(1){
        XNextEvent(d,&event);
        switch(event.type){
        case ButtonPress:
            switch(event.xbutton.button){
                case Button1:
                    x=event.xbutton.x;
                    y=event.xbutton.y;
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


    coords[0] = x;
    coords[1] = y;
    return coords;
}


