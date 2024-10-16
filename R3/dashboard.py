import collectd
# import psutil (removed as it is not used directly in this script)
import paramiko

# Configurações SSH
REMOTE_HOSTS = [
    {'hostname': '192.168.1.2', 'username': 'user', 'password': 'password'},
    {'hostname': '192.168.1.3', 'username': 'user', 'password': 'password'}
]

def configure_callback():
    collectd.info('Configuring collectd plugin')

def init_callback():
    collectd.info('Initializing collectd plugin')

def read_callback():
    for host in REMOTE_HOSTS:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(host['hostname'], username=host['username'], password=host['password'])

        # Collecting CPU usage
        cpu_usage = get_remote_cpu_usage(ssh)
        val = collectd.Values(plugin='cpu', host=host['hostname'])
        val.type = 'gauge'
        val.values = [cpu_usage]
        val.dispatch()

        # Collecting RAM usage
        ram_usage = get_remote_ram_usage(ssh)
        val = collectd.Values(plugin='memory', host=host['hostname'])
        val.type = 'gauge'
        val.values = [ram_usage]
        val.dispatch()

        # Collecting Disk usage
        disk_usage = get_remote_disk_usage(ssh)
        val = collectd.Values(plugin='disk', host=host['hostname'])
        val.type = 'gauge'
        val.values = [disk_usage]
        val.dispatch()

        # Collecting CPU temperature
        cpu_temp = get_remote_cpu_temperature(ssh)
        val = collectd.Values(plugin='temperature', host=host['hostname'])
        val.type = 'gauge'
        val.values = [cpu_temp]
        val.dispatch()

        ssh.close()

def get_remote_cpu_usage(ssh):
    _, stdout, _ = ssh.exec_command("python3 -c 'import psutil; print(psutil.cpu_percent(interval=1))'")
    output = stdout.read().strip()
    return float(output) if output else 0.0

def get_remote_ram_usage(ssh):
    _, stdout, _ = ssh.exec_command("python3 -c 'import psutil; print(psutil.virtual_memory().percent)'")
    return float(stdout.read().strip())

def get_remote_disk_usage(ssh):
    _, stdout, _ = ssh.exec_command("python3 -c 'import psutil; print(psutil.disk_usage(\"/\").percent)'")
    return float(stdout.read().strip())

def get_remote_cpu_temperature(ssh):
    _, stdout, _ = ssh.exec_command("python3 -c 'import psutil; temps = psutil.sensors_temperatures(); print(temps[\"coretemp\"][0].current if \"coretemp\" in temps else 0.0)'")
    return float(stdout.read().strip())

collectd.register_config(configure_callback)
collectd.register_init(init_callback)
collectd.register_read(read_callback)