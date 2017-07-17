from gesture_control import GestureControl
from socketIO_client import SocketIO


if __name__ == '__main__':
    socketIO = SocketIO('localhost', 3000)
    gc = GestureControl()
    gc.socketIO = socketIO
    gc.run()
