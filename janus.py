import npyscreen
from time import sleep
from threading import Thread
import subprocess


class TrafficMonitor:
    """Monitor traffic on listening ports."""
    def __init__(self):
        self.logs = []
        self.running = True
        self.listening_ports = []
        self.selected_port = None

    def fetch_listening_ports(self):
        """Fetch all listening ports dynamically."""
        try:
            result = subprocess.run(
                ["ss", "-tuln"], capture_output=True, text=True
            )
            # Extract only the port numbers
            listening_ports = []
            for line in result.stdout.splitlines():
                if "LISTEN" in line:  # Check for "LISTEN" state
                    parts = line.split()
                    local_address = parts[-2]  # Extract local address
                    port = local_address.split(":")[-1]  # Extract port number
                    if port.isdigit():  # Ensure it's a port number
                        listening_ports.append(port)
            self.listening_ports = sorted(set(listening_ports))
        except Exception as e:
            self.listening_ports = [f"Error fetching ports: {str(e)}"]

    def fetch_traffic(self):
        """Fetch traffic for the selected port."""
        while self.running:
            if not self.selected_port:
                self.logs = ["No port selected"]
            else:
                try:
                    result = subprocess.run(
                        ["ss", "-tan"], capture_output=True, text=True
                    )
                    traffic = [
                        line for line in result.stdout.splitlines()
                        if f":{self.selected_port}" in line
                    ]
                    self.logs = traffic if traffic else [f"No traffic on port {self.selected_port}"]
                except Exception as e:
                    self.logs = [f"Error: {str(e)}"]
            sleep(1)


class TrafficMonitorApp(npyscreen.NPSAppManaged):
    def __init__(self, traffic_monitor):
        super().__init__()
        self.traffic_monitor = traffic_monitor

    def onStart(self):
        self.addForm("MAIN", MainForm, traffic_monitor=self.traffic_monitor)


class MainForm(npyscreen.FormBaseNew):
    def __init__(self, *args, **kwargs):
        self.traffic_monitor = kwargs.pop("traffic_monitor")
        self.running = True
        super().__init__(*args, **kwargs)

    def create(self):
        # Listening Ports (left-aligned box)
        self.port_list = self.add(
            npyscreen.BoxTitle,
            name="Açık Portlar",
            values=[],
            relx=1,  # Left start
            rely=1,  # Top start
            width=self.useable_space()[1] // 8,  # One-eighth of the width
        )
        # Traffic logs for selected port (rest of the screen)
        self.log_box = self.add(
            npyscreen.BoxTitle,
            name="Seçili Port için Akan Trafik",
            relx=self.useable_space()[1] // 7,  # Start to the right of Açık Portlar
            rely=1,  # Top start
        )
        # Start monitoring threads
        self.monitor_thread = Thread(target=self.update_logs, daemon=True)
        self.monitor_thread.start()

    def update_logs(self):
        """Update traffic logs dynamically."""
        while self.running:
            # Update listening ports dynamically
            self.traffic_monitor.fetch_listening_ports()
            self.port_list.values = self.traffic_monitor.listening_ports
            self.port_list.display()

            # Update selected port
            selected_port_index = self.port_list.value
            if selected_port_index is not None and selected_port_index < len(self.traffic_monitor.listening_ports):
                self.traffic_monitor.selected_port = self.traffic_monitor.listening_ports[selected_port_index]

            # Update traffic logs dynamically
            self.log_box.values = self.traffic_monitor.logs
            self.log_box.display()
            sleep(1)

    def exit_application(self, *args, **keywords):
        """Stop all running threads and exit."""
        self.running = False
        self.traffic_monitor.running = False
        self.parentApp.setNextForm(None)
        self.editing = False


if __name__ == "__main__":
    monitor = TrafficMonitor()
    traffic_thread = Thread(target=monitor.fetch_traffic, daemon=True)
    traffic_thread.start()

    try:
        app = TrafficMonitorApp(monitor)
        app.run()
    except KeyboardInterrupt:
        monitor.running = False
