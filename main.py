import json
import os
import time

import requests
from bs4 import BeautifulSoup
import re

previous_ip = None


def get_current_ip():
    try:
        response = requests.get("https://api.ipify.org?format=json")
        data = response.json()
        return data['ip']  # Extract IP address from JSON response
    except Exception as e:
        print(f"Error fetching IP address: {e}")
        return None


def extract_form_data(html):
    soup = BeautifulSoup(html, 'html.parser')

    form = soup.find('form', {'id': 'frmconfig'})

    form_data = {}

    for input_tag in form.find_all('input'):
        name = input_tag.get('name')
        value = input_tag.get('value', '')
        if name:
            form_data[name] = value

    for select_tag in form.find_all('select'):
        name = select_tag.get('name')
        selected_option = select_tag.find('option', selected=True)
        value = selected_option['value'] if selected_option else ''
        if name:
            form_data[name] = value

    return form_data


def get_page_html(url, session):
    response = session.get(url)
    if response.status_code == 200:
        return response.text
    else:
        print(f'Failed to get page: {url}')
        return None


def login_to_pa_vietnam(session, domain, password):
    login_url = "https://access.pavietnam.vn/checklogin.php"
    login_data = {
        'domain': domain,
        'password': password,
    }

    response = session.post(login_url, data=login_data)
    if response.status_code == 200 and "index.php" in response.url:
        print("Login successful!")
        return True
    else:
        print("Login failed!")
        return False


def submit_update_form(session, data):
    url = "https://access.pavietnam.vn/index.php?view=1"
    response = session.post(url, data=data)
    if response.status_code == 200 and "index.php" in response.url:
        print("Send update successful!")
        return True
    else:
        print("Update failed!")
        return False


def on_ip_change(domain, password, entries, ip):
    # Start a session
    with requests.Session() as session:
        # Login to maintain the session
        if login_to_pa_vietnam(session, domain, password):
            # Get the domain configuration HTML
            config_url = "https://access.pavietnam.vn/index.php?view=1"
            html = get_page_html(config_url, session)
            if html:
                # Extract form data
                form_data = extract_form_data(html)

                # Print the extracted form data
                form = form_data.items()
                for key, value in form:
                    # print(f"{key}: {value}")
                    if value in entries:
                        # update IP
                        match = re.search(r'\d+$', key)
                        index = int(match.group())
                        data = {
                            "TTL": form_data["TTL"],
                            f"IDdns{index}": form_data.get(f"IDdns{index}"),
                            f"delete{index}": form_data.get(f"delete{index}"),
                            f"host{index}": form_data.get(f"host{index}"),
                            f"type{index}": form_data.get(f"type{index}"),
                            f"title{index}": form_data.get(f"title{index}"),
                            f"protocol{index}": form_data.get(f"protocol{index}"),
                            f"weight{index}": form_data.get(f"weight{index}"),
                            f"portnumber{index}": form_data.get(f"portnumber{index}"),
                            f"address{index}": ip,
                            f"ttl{index}": form_data.get(f"ttl{index}"),
                            f"flags{index}": form_data.get(f"flags{index}"),
                            f"tag{index}": form_data.get(f"tag{index}"),
                            f"priority{index}": form_data.get(f"priority{index}"),
                            "listdelete": "",
                            "numhost": form_data["numhost"],
                            "domain": form_data["domain"],
                            "domainidn": form_data["domainidn"],
                            "UpdateDns": "Save+Configuration",
                            "command": "0",
                            "ipaddress": ""
                        }
                        if submit_update_form(session, data):
                            print(f"Success update DNS for {value}.{domain} to value {ip}!")
    print("Done!")

def read_config(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)


home_dir = os.path.expanduser("~")
config_file =  os.path.join(home_dir, ".paddns")


if __name__ == "__main__":
    if not os.path.exists(config_file):
        print("Config file not exists")
    else:
        config = read_config(config_file)
        while True:
            try:
                current_ip = get_current_ip()
                print(f"Current IP: {current_ip}, previous IP: {previous_ip}")
                time.sleep(1)
                if current_ip != previous_ip:
                    for entry in config:
                        on_ip_change(entry["domain"], entry["password"], entry["entries"], current_ip)
                    previous_ip = current_ip
                else:
                    print("No change")
            except Exception as e:
                print(f"Error: {e}. Retrying in 30 seconds...")
                time.sleep(30)
                continue
            time.sleep(180)
