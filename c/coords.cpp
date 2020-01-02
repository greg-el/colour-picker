#include <X11/Xlib.h>
#include <X11/cursorfont.h>
#include <iostream>
#include <array>
//Compile hint: g++ -shared -Wall -fPIC -Wl,-soname,coords -o ../obj/coords.so coords.cpp -lX11

#ifdef __cplusplus
extern "C"
#endif

std::array<int, 2> coordinates (){
    std::array<int, 2> coords;
    Display* d = XOpenDisplay((char *)NULL);
    Cursor c;
    int x=-1,y=-1;
    bool rightClick;

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
                case Button3:
                     rightClick = true;
                default:
                    break;
            }
            break;
        default:
            break;
        }
        if(x>=0 && y>=0)break;
        if(rightClick)break;
    }

    XUngrabPointer(d, CurrentTime);
    XCloseDisplay(d);
    coords[0] = x;
    coords[1] = y;
    return coords;
}


