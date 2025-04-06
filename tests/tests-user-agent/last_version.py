import requests
import time

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
    'google:chrome_os' : 'ChromeOS',
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
    try:
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
                    version_line = version_line[4:] + '\n' + lines[j+1]
                version_line = version_line.replace('</td>', '').replace('</span>', '').strip()
                
                # print(f"Version line: '{version_line}'")
                
                # Print everything that is not between some <>
                while '<' in version_line:
                    start = version_line.index('<')
                    end = version_line.index('>', start) + 1
                    version_line = version_line[:start] + version_line[end:]
                    # print(f"Version line: '{version_line}'")
                
                # Print everything that is not between some ()
                while '(' in version_line:
                    start = version_line.index('(')
                    end = version_line.index(')', start) + 1
                    version_line = version_line[:start] + version_line[end:]
                    # print(f"Version line: '{version_line}'")
                
                # print(f"Version line: '{version_line}'")
                
                # Get multiple versions
                versions = [b.split(';')[-1] for b in version_line.split(' ') if b.split(';')[-1]]
                # print(f"Versions: {versions}")
                
                # version = ['134.0.6998.166', '135.0.7049.42/52', '135.0.7049.53', '135.0.7049.38']
                # Get the version highest number
                try:
                    version = max(versions, key=lambda x: [int(i) for i in x.split('.')[0]])
                    if version.replace('.', '').isdigit() == False:
                        if versions[0].replace('.', '').isdigit():
                            version = versions[0]
                        version = versions[0]
                except Exception as e:
                    # print(f"Error: {e}")
                    # Take the version that starts with a number
                    version = [b.split('>')[-1] for b in versions if b.split('>')[-1][0].isdigit()][0]
                # print(f"Version: {version}")
                
                return version.strip()
    except Exception as e:
        print(f"Error: {e}")
        # print(f"Response text: {response.text}")
        return None
    return None


if __name__ == "__main__":
    import uagent
    
    with open('user-agents-samples.txt', 'r') as f:
        cpes = f.readlines()
    cpes = [uagent.get_cpe(cpe.strip()) for cpe in cpes]
    # cpes = cpes[2:3]
    
    # cpes = [uagent.get_cpe('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36')]
    
    for cpe_tuple in cpes:
        for cpe in cpe_tuple:
            # print(f"Processing CPE: {cpe}")
            print(f"Last version for '{cpe}': ", end='', flush=True)
            try:
                last_version = get_last_version(cpe)
                print(f"{last_version}")
            except Exception as e:
                print(f"Error: {e}")
            time.sleep(2)
    