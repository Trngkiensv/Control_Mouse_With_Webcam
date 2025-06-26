import multiprocessing as mp
from app import main as app_main
from ControlMouseWithCam import MouseController

if __name__ == '__main__':
    # create queue
    queue = mp.Queue()
    # create process of app.py and ControlMouseWithCam.py
    app_process = mp.Process(target=app_main, args=(queue,))
    mouse_process = mp.Process(target=MouseController.main, args=(queue,))

    # start processes
    app_process.start()
    mouse_process.start()

    # wait for process end
    app_process.join()
    mouse_process.join()
