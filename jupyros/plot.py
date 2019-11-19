"""
Live Plot class for jupyter-ros2 Project

Author: zmk5 (Zahi Kakish)

"""
import numpy as np
import bqplot as bq
from jupyros.subscription import Subscription

try:
    import rclpy
except ModuleNotFoundError:
    print("The rclpy package is not found in your $PYTHONPATH. " +
          "Subscribe and publish are not going to work.")
    print("Do you need to activate your ros2 environment?")

class LivePlot(Subscription):
    """
    LivePlot Class
    """
    def __init__(self, node, msg_type, topic):
        # Check if a ros2 node is provided.
        if (not isinstance(node, rclpy.node.Node)
                or not issubclass(type(node), rclpy.node.Node)):
            raise TypeError(
                "Input argument 'node' is not of type rclpy.node.Node!")

        self.fields = {
            "xlabel": "x",
            "ylabel": "y",
            "title": "LivePlot",
            }
        self.data_fields = ["x", "y"]
        self.plot_data = []
        self.scale = {
            "x": bq.LinearScale(),
            "y": bq.LinearScale(),
            }
        self.axis = {
            "x": None,
            "y": None,
            }
        self.lines = None
        self.figure = None

        # Initialize the Subscription class
        super().__init__(node, msg_type, topic, self.plot_callback)

    def display(self):
        """ Displays the plot figure on the jupyter notebook cell """
        # Create figure to display plot data.
        self.axis["x"] = bq.Axis(
            label=self.fields["xlabel"], scale=self.scale["x"],
            grid_lines="solid")
        self.axis["y"] = bq.Axis(
            label=self.fields["ylabel"], scale=self.scale["y"],
            orientation="vertical", grid_lines="solid")
        self.lines = bq.Lines(x=np.array([]), y=np.array([]), scales=self.scale)
        self.figure = bq.Figure(
            axes=[self.axis["x"], self.axis["y"]], marks=[self.lines],
            labels=[self.fields["xlabel"], self.fields["ylabel"]],
            display_legend=True, title=self.fields["title"])

        # Start subscription to begin rclpy.spin()
        self._start_subscription(None)

        return self.figure

    def plot_callback(self, msg):
        """ default callback for LivePlot class """
        incoming_data = []
        history = 100
        for i in self.data_fields:
            incoming_data.append(getattr(msg, i))

        self.plot_data.append(incoming_data)
        self.plot_data = self.plot_data[-history:]
        self.lines.x = np.arange(len(self.plot_data))
        self.lines.y = np.asarray(self.plot_data).T

    def change_title(self, new_title: str):
        """ Change title of live plot """
        self.fields["title"] = new_title

    def change_xlabel(self, new_xlabel: str):
        """ Change x-axis label of live plot """
        self.fields["xlabel"] = new_xlabel

    def change_ylabel(self, new_ylabel: str):
        """ Change y-axis label of live plot """
        self.fields["ylabel"] = new_ylabel
