from user_agents import parse
import requests
from datetime import datetime

# URL = "https://services.nvd.nist.gov/rest/json/cves/2.0?virtualMatchString=cpe:2.3:a:mozilla:firefox&versionStart=131.0&versionStartType=including&versionEnd=131.0.3&versionEndType=excluding"
# URL = "https://services.nvd.nist.gov/rest/json/cves/2.0?virtualMatchString=cpe:2.3:a:mozilla:firefox&versionStart=131.0&versionStartType=including&noRejected"
URL = "https://services.nvd.nist.gov/rest/json/cves/2.0?cpeName={-{CPE}-}&noRejected"
API_KEY = "a48ad05d-f5a4-4517-bdbe-aec6683c53a7"  # Replace with your actual API key
HEADERS = {'apiKey': API_KEY}


def get_url(cpe):
    return URL.replace("{-{CPE}-}", cpe)


def extract_cve_data(cve):
    cve_id = ""
    description = ""
    highest_score = 0
    highest_severity = ""
    try:
        cve_id = cve['id']
        all_description = cve['descriptions']
        description = ""
        for desc in all_description:
            if desc['lang'] == 'en':
                description = desc['value']
                break

        # print(f"CVE ID: {cve_id}")
        # print(f"Description: {description}")

        all_metrics = cve['metrics']
        highest_score = 0
        highest_severity = ""
        for metric in all_metrics:
            for elem in all_metrics[metric]:
                if 'cvssData' in elem:
                    try:
                        if 'baseScore' in elem['cvssData'] and 'baseSeverity' in elem['cvssData']:
                            if elem['cvssData']['baseScore'] > highest_score:
                                highest_score = elem['cvssData']['baseScore']
                                highest_severity = elem['cvssData']['baseSeverity']
                        else:
                            if elem['cvssData']['baseScore'] > highest_score:
                                highest_score = elem['cvssData']['baseScore']
                                highest_severity = elem['baseSeverity']
                    except Exception as e:
                        print(f"Error extracting CVSS data: {e}")
                        print(f"Element: {elem}")
    except Exception as e:
        print(f"Error processing CVE data: {e}")
        return cve_id, description, highest_score, highest_severity
    return cve_id, description, highest_score, highest_severity


def cpe_start(cpe):
    return ':'.join(cpe.split(':')[:5])


def under_cpe_version(cpe1, cpe2):
    """
    Compare CPE versions to check if cpe1 is under cpe2, including the version. cpe1 <= cpe2
    """
    # Compare CPE versions
    version1 = cpe1.split(':')[5].split('.')[0]
    version2 = cpe2.split(':')[5].split('.')[0]
    return version1 <= version2


def extract_cve_configurations(cve, browser_cpe, os_cpe):
    all_criteria = []
    # print("Configurations:", browser_cpe, os_cpe)
    # if cve['id'] != 'CVE-2005-2516':
    #     return all_criteria, True #################################################################################################
    if 'configurations' not in cve:
        print("No configurations found")
        return all_criteria, True
    # print(cve['configurations'])
    try:
        configurations = cve['configurations']
        config_corresponds = True
        for config in configurations:
            if 'operator' in config:
                operator = config['operator']
                if operator == 'AND':
                    # print("Operator: AND")
                    criteria = []
                    for node in config['nodes']:
                        try:
                            criterion = node['cpeMatch'][0]['criteria']
                            # criterion = [e['criteria'] for e in node['cpeMatch'] if cpe_start(e['criteria']) == cpe_start(browser_cpe) or cpe_start(e['criteria']) == cpe_start(os_cpe)][0]
                            # print(criterion)
                            
                            # print("Node:", node['cpeMatch'])
                            for match in node['cpeMatch']:
                                if cpe_start(browser_cpe) == cpe_start(match['criteria']) or cpe_start(os_cpe) == cpe_start(match['criteria']):
                                    criterion = match['criteria']
                                    # print("Criterion:", criterion)
                                    if 'versionEndIncluding' in match:
                                        criterion = cpe_start(match['criteria']) + ':' + match['versionEndIncluding'] + ':*:*:*:*:*:*:*'
                                        # print("Criterion with versionEndIncluding:", criterion)
                            
                            criteria.append(criterion)
                        except Exception as e:
                            print(f"Error extracting criteria: {e}")
                    for criterion in criteria:
                        # print('Checking criterion:', criterion)
                        if cpe_start(browser_cpe) == cpe_start(criterion) or cpe_start(os_cpe) == cpe_start(criterion):
                            # print("Criterion matches")
                            if under_cpe_version(browser_cpe, criterion) or under_cpe_version(os_cpe, criterion):
                                # print("Criterion matches with version")
                                pass
                            else:
                                config_corresponds = False
                                # print("Criterion does not match with version")
                                break
                        else:
                            config_corresponds = False
                            # print("Criterion does not match")
                            break
                    all_criteria.append(criteria)
            # print('~~~~~~~~')
    except Exception as e:
        print(f"Error processing configurations: {e}")
        return all_criteria, config_corresponds
    return all_criteria, config_corresponds


def get_cpe(user_agent):
    user_agent = parse(user_agent)
    
    # Parse browser information
    browser_family = user_agent.browser.family.lower()
    if 'mobile' in browser_family.split():
        browser_family = [part for part in browser_family.split() if part != 'mobile'][0]
    if 'ios' in browser_family.split():
        browser_family = [part for part in browser_family.split() if part != 'ios'][0]
    if browser_family == "opera":
        browser_family = "opera_browser"
    browser_version = user_agent.browser.version_string.split('.')[0]
    # print(browser_family, browser_version)
    
    browser_vendor_list = {
        'chrome': 'google',
        'firefox': 'mozilla',
        'safari': 'apple',
        'edge': 'microsoft',
        'opera_browser': 'opera',
    }
    browser_vendor = browser_vendor_list.get(browser_family, '*')
    browser_cpe = f"cpe:2.3:a:{browser_vendor}:{browser_family}:{browser_version}"#:*:*:*:*:*:*:*:*"
    # print(browser_cpe)
    
    # Parse OS information
    os_family = user_agent.os.family.lower()
    if "mac os x" in os_family:
        os_family = "mac_os_x"
    elif "mac os" in os_family:
        os_family = "macos"
    if os_family == "chrome os":
        os_family = "chrome_os"
    if os_family == "linux":
        os_family = "linux_kernel"
    if os_family == "ios":
        os_family = "iphone_os"
    if os_family == "ubuntu":
        os_family = "ubuntu_linux"
    os_version = user_agent.os.version_string.split('.')[0]
    # print(os_family, os_version)
    
    os_vendors_list = {
        'windows': 'microsoft',
        'mac_os_x': 'apple',
        'macos': 'apple',
        'linux_kernel': 'linux',
        'android': 'google',
        'iphone_os': 'apple',
        'chrome_os': 'google',
        'ubuntu_linux': 'canonical',
    }
    
    os_vendor = os_vendors_list.get(os_family, '*')
    os_cpe = f"cpe:2.3:o:{os_vendor}:{os_family}:{os_version}"#:*:*:*:*:*:*:*:*"
    # print(cpe_os)
    return browser_cpe, os_cpe


def search_cve_by_cpe(browser_cpe, os_cpe):
    print(f"Browser CPE : {browser_cpe}")
    print(f"OS CPE      : {os_cpe}")
    response = requests.get(get_url(browser_cpe), headers=HEADERS)
    if response.status_code == 200:
        data = response.json()
        # print(data)
        try:
            for vuln in data['vulnerabilities']:
                vuln = vuln['cve']
                # print(vuln)
                # input("Press Enter to continue...")
                # print("Vuln Status: ", vuln['vulnStatus'], vuln['id'])
                
                # published : ex "2003-12-31T05:00:00.000"
                published_date = datetime.strptime(vuln['published'], "%Y-%m-%dT%H:%M:%S.%f")
                
                days_since_published = (datetime.now() - published_date).days
                if days_since_published < 90 or True: # pas un bon critère
                    all_criteria, config_corresponds = extract_cve_configurations(vuln, browser_cpe, os_cpe)
                    if config_corresponds:
                        specific_match = config_corresponds and len(all_criteria) > 0
                        cve_id, description, highest_score, highest_severity = extract_cve_data(vuln)
                        if highest_score > 8 or highest_severity in ['HIGH', 'CRITICAL'] or (specific_match and highest_score > 6.5):
                            # print(f"Published Date: {published_date.strftime('%Y-%m-%d')}")
                            specific_match_str = " - >>> Specific match" if specific_match else ""
                            print(f"{cve_id} {published_date.strftime('%Y-%m-%d')} - Score: {highest_score}, Severity: {highest_severity}{specific_match_str}")
                            # print(f"Config corresponds: {config_corresponds}")
                            # print(f"Configurations: {all_criteria}")
                # # quit()
                # print("#" * 40)
        except Exception as e:
            print(f"Error processing vulnerabilities: {e}")
    else:
        print(f"Error: {response.status_code}")


def search_cpe_release_date(cpe):
    URL = f"https://services.nvd.nist.gov/rest/json/cpes/2.0?cpeMatchString={cpe}.0"
    print(f"URL: {URL}")
    response = requests.get(URL, headers=HEADERS)
    if response.status_code == 200:
        data = response.json()
        try:
            for product in data['products']:
                product = product['cpe']
                # print(product)
                if 'created' in product:
                    release_date = datetime.strptime(product['created'], "%Y-%m-%dT%H:%M:%S.%f")
                    days_since_release = (datetime.now() - release_date).days
                    print(f"Release Date: {release_date.strftime('%Y-%m-%d')} - Days since release: {days_since_release}")
        except Exception as e:
            print(f"Error processing release date: {e}")
    else:
        print(f"Error: {response.status_code}")


if __name__ == "__main__":
    # Load user agents from file
    with open("user-agents-samples.txt", "r") as f:
        user_agents = f.readlines()
    user_agents = [ua.strip() for ua in user_agents if not ua.startswith('---')]
    
    # Print cpe strings for each user agent
    print("-" * 50)
    for user_agent_string in user_agents:
        browser_cpe, os_cpe = get_cpe(user_agent_string)
        # print(f"Browser CPE : {browser_cpe}")
        # print(f"OS CPE      : {os_cpe}")
        search_cpe_release_date(browser_cpe)
        search_cve_by_cpe(browser_cpe, os_cpe)
        input("Press Enter to continue...")
        print('\n'*5)
        print("-" * 50)
    
    quit()
    
    