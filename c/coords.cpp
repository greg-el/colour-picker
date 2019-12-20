#include <X11/Xlib.h>
#include <iostream>
#include <array>
#ifdef __cplusplus
extern "C"
#endif

std::array<int, 2> getClickCoordinates (){
    std::array<int, 2> coords;
    Display* d = XOpenDisplay((char *)NULL);
    int clickX=-1,clickY=-1;
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
                    coords[0] = event.xbutton.x;
                    coords[1] = event.xbutton.y;
                    break;
                default:
                    break;
            }
            break;
        default:
            break;
        }
        if(clickX>=0 && clickY>=0) {
            break;
        }
    }
    return coords;
}


int main() {
    return 0;
}