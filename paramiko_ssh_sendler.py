from project_configs.configurations import load_ssh_configs
from objects_parser.data_parser import RealtParser

        
if __name__ == '__main__':
    password_ssh, username_ssh, host_ssh, port_ssh = load_ssh_configs()
    print(host_ssh, port_ssh, username_ssh, password_ssh)
    urls = RealtParser.url_parser()
    RealtParser.send_ssh_json(host_ssh, port_ssh, username_ssh, password_ssh, urls)
