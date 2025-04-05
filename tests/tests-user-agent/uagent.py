from user_agents import parse

# user_agent = parse(user_agent_string)


# print(user_agent.browser)
# print(user_agent.device)
# print(user_agent.os)
# print(user_agent.is_mobile)
# print(user_agent.is_tablet)
# print(user_agent.is_pc)
# print(user_agent.is_email_client)

import requests

URL = "https://services.nvd.nist.gov/rest/json/cves/2.0?virtualMatchString=cpe:2.3:a:mozilla:firefox&versionStart=131.0&versionStartType=including&versionEnd=131.0.3&versionEndType=excluding"
# URL = "https://services.nvd.nist.gov/rest/json/cves/2.0?virtualMatchString=cpe:2.3:a:mozilla:firefox&versionStart=131.0&versionStartType=including&noRejected"
URL = "https://services.nvd.nist.gov/rest/json/cves/2.0?cpeName=cpe:2.3:a:mozilla:firefox:131&noRejected"

API_KEY = "a48ad05d-f5a4-4517-bdbe-aec6683c53a7"  # Replace with your actual API key

HEADERS = {'apiKey': API_KEY}


def extract_cve_configurations(cve):
    criteria = []
    if 'configurations' not in cve:
        return criteria
    try:
        configurations = cve['configurations']
        for config in configurations:
            if 'operator' in config:
                operator = config['operator']
                if operator == 'AND':
                    for node in config['nodes']:
                        try:
                            # print(node['cpeMatch'][0]['criteria'])
                            criteria.append(node['cpeMatch'][0]['criteria'])
                        except Exception as e:
                            print(f"Error extracting criteria: {e}")
    except Exception as e:
        print(f"Error processing configurations: {e}")
        return criteria
    return criteria


def extract_cve_data(cve):
    try:
        cve_id = cve['id']
        all_description = cve['descriptions']
        description = ""
        for desc in all_description:
            if desc['lang'] == 'en':
                description = desc['value']
                break

        print(f"CVE ID: {cve_id}")
        print(f"Description: {description}")

        all_metrics = cve['metrics']
        highest_severity = ""
        highest_score = 0
        for metric in all_metrics:
            for elem in all_metrics[metric]:
                if 'cvssData' in elem:
                    try:
                        if elem['cvssData']['baseScore'] > highest_score:
                            highest_score = elem['cvssData']['baseScore']
                            highest_severity = elem['cvssData']['baseSeverity']
                    except Exception as e:
                        print(f"Error extracting CVSS data: {e}")
    except Exception as e:
        print(f"Error processing CVE data: {e}")
        return
    print(f"Metrics: Score: {highest_score}, Severity: {highest_severity}")


def search_cve_by_user_agent(user_agent):
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
    cpe = f"cpe:2.3:a:{browser_vendor}:{browser_family}:{browser_version}:*:*:*:*:*:*:*:*"
    print(cpe)
    
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
    cpe_os = f"cpe:2.3:o:{os_vendor}:{os_family}:{os_version}:*:*:*:*:*:*:*:*"
    print(cpe_os)
    
    # cpe:2.3:a:mozilla:firefox:*:*:*:*:*:*:*:*
    
    pass


def get_cpe_from_browser(user_agent):
    pass


if __name__ == "__main__":
    # # Edge on Windows 10
    # user_agents = []
    # user_agents.append("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36 Edg/134.0.0.0")
    # user_agents.append("Mozilla/5.0 (Linux; Android 13; Pixel 6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Mobile Safari/537.36")
    # # iPhone 14 Pro
    # user_agents.append("Mozilla/5.0 (iPhone14,3; U; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/602.1.50 (KHTML, like Gecko) Version/10.0 Mobile/19A346 Safari/602.1")
    # user_agents.append("Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Mobile Safari/537.36 OPR/88.0.0.0")
    # user_agents.append("Mozilla/5.0 (Macintosh; Intel Mac OS X 14_7_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.3 Safari/605.1.15")
    
    with open("user-agents-samples.txt", "r") as f:
        user_agents = f.readlines()
    user_agents = [ua.strip() for ua in user_agents if not ua.startswith('---')]
    
    print("-" * 50)
    for user_agent_string in user_agents:
        search_cve_by_user_agent(user_agent_string)
        input("Press Enter to continue...")
        print("-" * 50)
    
    quit()
    
    response = requests.get(URL, headers=HEADERS)
    if response.status_code == 200:
        data = response.json()
        # print(data)
        for vuln in data['vulnerabilities']:
            vuln = vuln['cve']
            cve_id = vuln['id']
            # print(vuln.keys())
            # # CVE ID
            # print(f"CVE ID: {cve_id}")
            # # vulnStatus
            # print(f"vulnStatus: {vuln['vulnStatus']}")
            # # weaknesses
            # print(f"weaknesses: {vuln['weaknesses']}")
            # # descriptions
            # print(f"descriptions: {vuln['descriptions']}")
            # # metrics
            # print(f"metrics: {vuln['metrics']}")
            
            # for key, value in vuln.items():
            #     print(f"{key}: {value}")
            #     print("-" * 40)
            
            # cve_id = vuln['id']
            # all_description = vuln['descriptions']
            # description = ""
            # for desc in all_description:
            #     if desc['lang'] == 'en':
            #         description = desc['value']
            #         break
                
            # print(f"CVE ID: {cve_id}")
            # print(f"Description: {description}")    
            
            # all_metrics = vuln['metrics']
            # highest_severity = ""
            # highest_score = 0
            # for metric in all_metrics:
            #     # if metric == 'cvssMetricV31':
            #     #     metrics = all_metrics[metric]
            #     #     break
            #     for elem in all_metrics[metric]:
            #         # print(metric, elem, end=' | ')
            #         # print(">>>>", elem)
            #         if 'cvssData' in elem:
            #             # print(elem['cvssData']['baseScore'], elem['cvssData']['baseSeverity'])
            #             if elem['cvssData']['baseScore'] > highest_score:
            #                 highest_score = elem['cvssData']['baseScore']
            #                 highest_severity = elem['cvssData']['baseSeverity']
            #         else:
            #             # print()
            #             pass
            #         # print("-" * 20)
            
            # # print(f"Metrics: Score: {highest_score}, Severity: {highest_severity}")
            
            extract_cve_data(vuln)
            
            # # configurations: [{'operator': 'AND', 'nodes': [{'operator': 'OR', 'negate': False, 'cpeMatch': [{'vulnerable': True, 'criteria': 'cpe:2.3:a:mozilla:firefox:*:*:*:*:*:*:*:*', 'versionEndExcluding': '136.0', 'matchCriteriaId': '7DB4CDD0-EC54-43D0-ACB2-F159ABA53D2C'}]}, {'operator': 'OR', 'negate': False, 'cpeMatch': [{'vulnerable': False, 'criteria': 'cpe:2.3:o:apple:iphone_os:-:*:*:*:*:*:*:*', 'matchCriteriaId': 'B5415705-33E5-46D5-8E4D-9EBADC8C5705'}]}]}]
            # if 'configurations' in vuln:
            #     configurations = vuln['configurations']
            #     # configuration = ""
            #     for config in configurations:
            #         # print(config)
            #         if 'operator' in config:
            #             operator = config['operator']
            #             if operator == 'AND':
            #                 for node in config['nodes']:
            #                     print(node['cpeMatch'][0]['criteria'])
            
            criteria = extract_cve_configurations(vuln)
            print(f"Configurations: {criteria}")
                        
            
            # for key, value in vuln.items():
            #     print(f"{key}: {value}")
            #     print("-" * 40)
            
            # quit()
            print("#" * 40)
    else:
        print(f"Error: {response.status_code}")