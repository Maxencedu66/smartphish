import requests
import time
import uagent

URL = "https://fr.wikipedia.org/wiki/{-{PAGE}-}"


cpe_to_page = {
    'mozilla:firefox': 'Mozilla_Firefox',
    'apple:safari': 'Safari_(navigateur_web)',
    'google:chrome': 'Google_Chrome',
    'microsoft:edge': 'Microsoft_Edge',
    'opera:opera_browser': 'Opera',
    
    'apple:iphone_os': 'IOS',
    'apple:mac_os_x': 'MacOS',
    'apple:macos': 'MacOS',
    'google:android': 'Android',
    'microsoft:windows': 'Microsoft_Windows',
    'linux:linux_kernel': 'Linux',
    'canonical:ubuntu_linux': 'Ubuntu_(système_d%27exploitation)',
}


def get_cpe_name(cpe):
    # cpe = "cpe:2.3:a:mozilla:firefox:119"
    # Split the CPE string into its components
    # print(f"Processing CPE: {cpe}")
    parts = cpe.split(':')
    # Extract the vendor and product names
    vendor_and_product = parts[3:4+1] if len(parts) >= 4 else ''
    
    # Return the vendor and product names as a tuple
    return ':'.join(vendor_and_product).lower() if vendor_and_product else ''


def get_url(cpe):
    cpe_name = get_cpe_name(cpe)
    # print(f"Processing CPE name: {cpe_name}")
    return URL.replace('{-{PAGE}-}', cpe_to_page.get(cpe_name, ''))


def get_last_version(cpe):
    response = requests.get(get_url(cpe))
    if response.status_code != 200:
        raise Exception("Failed to fetch the page")
    with open('page.html', 'w', encoding='utf-8') as f:
        f.write(response.text)
    
    # Find the line number where there is the text "Latest version"
    lines = response.text.split('\n')
    for i, line in enumerate(lines):
        if "Dernière version" in line:
            # print(f"Found 'Dernière version' at line {i}: {line}")
            break
    else:
        raise Exception("Latest version not found")
    for j in range(i+1, i+5):
        if lines[j].strip().startswith('<span class=') or lines[j].strip().startswith('<td>'):
            # Extract the version number from the line
            version_line = lines[j]
            # Remove HTML tags and extra spaces
            # version_line = version_line.replace('<span class=', '').replace('</span>', '').strip()
            # Extract the version number
            if version_line.startswith('<td>'):
                version_line = version_line[5:] + '\n' + lines[j+1]
            version_line = version_line.replace('</td>', '').replace('</span>', '').strip()
            print(f"Version line: '{version_line}'")
            if '>' in version_line:
                # Extract the version number from the line
                version_number = version_line.split('>')[1].split('<')[0].replace('(', '').strip()
            else:
                version_number = version_line.strip().split(' ')[0].replace('(', '').strip()
            # print(f"Version line: {version_line}")
            # print(f"Version number: {version_number}")
            return version_number
        
    return None
    
    # data = response.json()
    # return data['LATEST_FIREFOX_VERSION']


if __name__ == "__main__":
    # cpes = [("cpe:/a:mozilla:firefox")]
    with open('user-agents-samples.txt', 'r') as f:
        cpes = f.readlines()
    cpes = [uagent.get_cpe(cpe.strip()) for cpe in cpes]
    
    # cpes = cpes[2:3]
    
    for cpe_tuple in cpes:
        for cpe in cpe_tuple:
            try:
                last_version = get_last_version(cpe)
                print(f"Last version for {cpe}: {last_version}")
            except Exception as e:
                print(f"Error: {e}")
            time.sleep(4)
    
    # cpe = "cpe:/a:mozilla:firefox"
    # try:
    #     last_version = get_last_version(cpe)
    #     print(f"Last version for {cpe}: {last_version}")
    #     time.sleep(4)
    # except Exception as e:
    #     print(f"Error: {e}")