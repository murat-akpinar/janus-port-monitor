import npyscreen
from time import sleep
from threading import Thread
import subprocess


class TrafficMonitor:
    """Monitor traffic on specific ports."""
    def __init__(self):
        self.logs = []
        self.running = True

    def fetch_traffic(self):
        """Fetch traffic for port 22."""
        while self.running:
            try:
                result = subprocess.run(
                    ["ss", "-tan"], capture_output=True, text=True
                )
                traffic = [
                    line for line in result.stdout.splitlines() if ":22" in line
                ]
                self.logs = traffic if traffic else ["No traffic on port 22"]
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
        # Açık Portlar (sola dayalı kutu)
        self.port_list = self.add(
            npyscreen.BoxTitle,
            name="Açık Portlar",
            values=["22 - SSH"],
            relx=1,  # Sol başlangıç
            rely=1,  # Üst başlangıç
            width=self.useable_space()[1] // 8,  # Genişliğin üçte biri
        )
        # Seçili Port için Akan Trafik (ekranın geri kalanını kaplayan kutu)
        self.log_box = self.add(
            npyscreen.BoxTitle,
            name="Seçili Port için Akan Trafik",
            relx=self.useable_space()[1] // 7,  # Açık Portlar kutusunun sağından başla
            rely=1,  # Üst başlangıç
        )
        # Start traffic monitoring thread
        self.monitor_thread = Thread(target=self.update_logs, daemon=True)
        self.monitor_thread.start()

    def update_logs(self):
        """Update traffic logs dynamically."""
        while self.running:
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
