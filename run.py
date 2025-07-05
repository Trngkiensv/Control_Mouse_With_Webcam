import multiprocessing as mp
import keyboard
from app import main as app_main
from ControlMouseWithCam import MouseController
# from test_queue import main as test_main 

if __name__ == '__main__':
    # create queue
    queue = mp.Queue(maxsize=1000)
    # create process of app.py and ControlMouseWithCam.py
    app_process = mp.Process(target=app_main, args=(queue,))
    mouse_process = mp.Process(target=MouseController(queue).main, args=())
    # test_process = mp.Process(target=test_main, args=(queue,))
    try:
        # start processes
        app_process.start()
        mouse_process.start()
        # test_process.start()
        while True:
            if keyboard.is_pressed('ctrl+shift+b'):
                print("Ctrl+Shift+B pressed, terminating processes...")
                app_process.terminate()
                mouse_process.terminate()
                # test_process.terminate()
                break
    except KeyboardInterrupt:
        print("Terminating processes...")
        app_process.terminate()
        mouse_process.terminate()
        # test_process.terminate()