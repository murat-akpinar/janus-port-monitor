import npyscreen
from time import sleep
from threading import Thread
import subprocess

class TrafficMonitor:
    """Monitor traffic on listening ports using tcpdump."""
    def __init__(self):
        self.logs = []
        self.running = True
        self.listening_ports = []
        self.selected_port = None
        self.current_process = None

    def fetch_listening_ports(self):
        """Fetch all listening ports dynamically using ss."""
        try:
            result = subprocess.run(
                ["ss", "-tuln"], capture_output=True, text=True
            )
            listening_ports = []
            for line in result.stdout.splitlines():
                if "LISTEN" in line:
                    parts = line.split()
                    local_address = parts[-2]
                    port = local_address.split(":")[-1]
                    if port.isdigit():
                        listening_ports.append(port)
            self.listening_ports = sorted(set(listening_ports))
        except Exception as e:
            self.listening_ports = [f"Error fetching ports: {str(e)}"]

    def fetch_traffic(self):
        """Fetch traffic for the selected port using tcpdump."""
        while self.running:
            if not self.selected_port:
                self.logs = ["No port selected"]
                sleep(1)
                continue

            try:
                # Stop the current process if a new port is selected
                if self.current_process:
                    self.current_process.terminate()

                # Clear logs when switching to a new port
                self.logs = []

                # Start tcpdump for the selected port
                self.current_process = subprocess.Popen(
                    ["tcpdump", "-n", "-l", "-i", "any", f"port {self.selected_port}"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )

                for line in self.current_process.stdout:
                    if not self.running:
                        self.current_process.terminate()
                        break
                    self.logs.append(line.strip())
                    if len(self.logs) > 63:  # Limit log size
                        self.logs.pop(0)
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
        self.port_list = self.add(
            npyscreen.BoxTitle,
            name="Açık Portlar",
            values=[],
            relx=1,
            rely=1,
            width=self.useable_space()[1] // 8,
        )
        self.log_box = self.add(
            npyscreen.BoxTitle,
            name="Seçili Port için Akan Trafik",
            relx=self.useable_space()[1] // 7,
            rely=1,
        )
        self.monitor_thread = Thread(target=self.update_logs, daemon=True)
        self.monitor_thread.start()

    def update_logs(self):
        """Update traffic logs dynamically."""
        while self.running:
            self.traffic_monitor.fetch_listening_ports()
            self.port_list.values = self.traffic_monitor.listening_ports
            self.port_list.display()

            selected_port_index = self.port_list.value
            if selected_port_index is not None and selected_port_index < len(self.traffic_monitor.listening_ports):
                new_selected_port = self.traffic_monitor.listening_ports[selected_port_index]
                if new_selected_port != self.traffic_monitor.selected_port:
                    self.traffic_monitor.selected_port = new_selected_port
                    # Force a restart of the fetch_traffic thread
                    if self.traffic_monitor.current_process:
                        self.traffic_monitor.current_process.terminate()

            self.log_box.values = self.traffic_monitor.logs
            self.log_box.display()
            sleep(1)

    def exit_application(self, *args, **keywords):
        """Stop all running threads and exit."""
        self.running = False
        self.traffic_monitor.running = False
        if self.traffic_monitor.current_process:
            self.traffic_monitor.current_process.terminate()
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
        if monitor.current_process:
            monitor.current_process.terminate()
            
