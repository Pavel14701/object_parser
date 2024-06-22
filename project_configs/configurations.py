import os
from dotenv import load_dotenv


def load_bd_configs():
    load_dotenv()
    username_bd = str(os.getenv("USERNAME_BD"))
    password_bd = str(os.getenv("PASSWORD_BD"))
    host_bd = str(os.getenv("HOST_BD"))
    port_bd = str(os.getenv("PORT_BD"))
    database_bd = str(os.getenv("DATABASE_BD"))
    return username_bd, password_bd, host_bd, port_bd, database_bd


def load_ssh_configs():
    load_dotenv()
    password_ssh = str(os.getenv("PASSWORD_SSH"))
    username_ssh = str(os.getenv("USER_SSH"))
    host_ssh = str(os.getenv("HOST_SSH"))
    port_ssh = str(os.getenv("PORT_SSH"))
    return password_ssh, username_ssh, host_ssh, port_ssh


def load_woo_configs():
    load_dotenv()
    consumer_key = str(os.getenv("CONSUMER_KEY"))
    consumer_secret = str(os.getenv("CONSUMER_SECRET"))
    wp_url = str(os.getenv("WP_URL"))
    return consumer_key, consumer_secret, wp_url