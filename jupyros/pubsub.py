import threading
import time
import ipywidgets as widgets
import sys
try:
    import rclpy
except:
    pass

import inspect

output_registry = {}
subscriber_registry = {}

def callback_active():
    return threading.currentThread().name in active_callbacks

class OutputRedirector:
    def __init__(self, original):
        self.original = original

    def write(self, msg):
        thread_name = threading.currentThread().name
        if thread_name != 'MainThread' and output_registry.get(threading.currentThread().getName()) is not None:
            output_registry[threading.currentThread().getName()].append_stdout(msg)
        else:
            self.original.write(msg)

    def flush(self):
        self.original.flush()

    # necessary for ipython, but **not** for xeus-python!
    def set_parent(self, parent):
        self.original.set_parent(parent)

sys.stdout = OutputRedirector(sys.stdout)

def subscribe(node, topic, msg_type, callback):
    """
    Subscribes to a specific topic in another thread, but redirects output!

    @param node An rclpy node class
    @param topic The topic
    @param msg_type The message type
    @param callback The callback

    @return Jupyter output widget
    """

    if subscriber_registry.get(topic):
        raise RuntimeError("Already registerd...")

    out = widgets.Output(layout={'border': '1px solid gray'})
    subscriber_registry[topic] = node.create_subscription(msg_type, topic, callback, 10)
    output_registry[topic] = out

    btn = widgets.Button(description='Stop')

    def stop_start_subscriber(x):
        if output_registry.get(topic) is not None:
            subscriber_registry[topic].unregister()
            del output_registry[topic]
            btn.description = 'Start'
        else:
            output_registry[topic] = out
            subscriber_registry[topic] = node.create_subscription(msg_type, topic, callback, 10)
            btn.description = 'Stop'

    btn.on_click(stop_start_subscriber)
    btns = widgets.HBox((btn, ))
    vbox = widgets.VBox((btns, out))
    return vbox
