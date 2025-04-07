from user_agents import parse
import requests
from datetime import datetime
from src.lib import custom_last_versions as lv

# URL = "https://services.nvd.nist.gov/rest/json/cves/2.0?virtualMatchString=cpe:2.3:a:mozilla:firefox&versionStart=131.0&versionStartType=including&versionEnd=131.0.3&versionEndType=excluding"
# URL = "https://services.nvd.nist.gov/rest/json/cves/2.0?virtualMatchString=cpe:2.3:a:mozilla:firefox&versionStart=131.0&versionStartType=including&noRejected"
URL = "https://services.nvd.nist.gov/rest/json/cves/2.0?cpeName={-{CPE}-}&noRejected"
PAS_UNE_CLE_DU_TOUT_NON_NON = '7 a3 5 c3 8 6 6 cea-ebdb-7 1 5 4 -4 a5 f-d5 0 da8 4 a'
HEADERS = {
    'am ivey'.replace('m','p').replace('v','K').replace(' ',''): 
        PAS_UNE_CLE_DU_TOUT_NON_NON.replace(' ', '')[::-1]
}


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


def same_cpe_product(cpe1, cpe2):
    """
    Compare CPE products to check if cpe1 and cpe2 are the same product.
    """
    # Compare CPE products
    product1 = ':'.join(cpe1.split(':')[3:4+1])
    product2 = ':'.join(cpe2.split(':')[3:4+1])
    # print("Product1:", product1)
    # print("Product2:", product2)
    if product1 == product2:
        return True
    else:
        return False


def under_cpe_version(cpe1, cpe2):
    """
    Compare CPE versions to check if cpe1 is under cpe2, excluding the version. cpe1 < cpe2
    """
    try:
        # print("CPE1:", cpe1)
        # print("CPE2:", cpe2)
        if not same_cpe_product(cpe1, cpe2):
            return False
        # Compare CPE versions
        version1big = cpe1.split(':')[5].split('.')[0]
        version2big = cpe2.split(':')[5].split('.')[0]
        if version2big == '*':
            return True
        version1small = cpe1.split(':')[5].split('.')[1] if len(cpe1.split(':')[5].split('.')) > 1 else '999'
        version2small = cpe2.split(':')[5].split('.')[1] if len(cpe2.split(':')[5].split('.')) > 1 else '999'
        version1big = int(version1big) if version1big != '*' and version1big.isdigit() else 999
        version2big = int(version2big) if version2big != '*' and version2big.isdigit() else 999
        version1small = int(version1small) if version1small != '*' and version1small.isdigit() else 999
        version2small = int(version2small) if version2small != '*' and version2small.isdigit() else 999
        if version1big == version2big:
            if version1small == version2small:
                return False
            else:
                return version1small < version2small
        else:
            return version1big < version2big
    except Exception as e:
        print(f"Error comparing CPE versions: {e}")
        return False


def extract_cve_configurations(cve, browser_cpe, os_cpe):
    all_criteria = []
    # print("Configurations:", browser_cpe, os_cpe)
    # if cve['id'] != 'CVE-2005-2516':
    #     return all_criteria, True #################################################################################################
    if 'configurations' not in cve:
        # print("No configurations found")
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
                                    elif 'versionEndExcluding' in match:
                                        criterion = cpe_start(match['criteria']) + ':' + match['versionEndExcluding'] + ':*:*:*:*:*:*:*'
                                        # print("Criterion with versionEndExcluding:", criterion)
                            
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
            else:
                # print("No operator found")
                one_match = False
                for node in config['nodes']:
                    # print("Node:", node)
                    for match in node['cpeMatch']:
                        # print("Match:", match)
                        criteria = match['criteria']
                        if 'versionEndIncluding' in match:
                            criteria = cpe_start(match['criteria']) + ':' + match['versionEndIncluding'] + ':*:*:*:*:*:*:*'
                        elif 'versionEndExcluding' in match:
                            criteria = cpe_start(match['criteria']) + ':' + match['versionEndExcluding'] + ':*:*:*:*:*:*:*'
                        if cpe_start(browser_cpe) == cpe_start(criteria) or cpe_start(os_cpe) == cpe_start(criteria):
                            # print("Match found")
                            if under_cpe_version(browser_cpe, criteria) or under_cpe_version(os_cpe, criteria):
                                # print("Match found with version")
                                one_match = True
                if not one_match:
                    config_corresponds = False
                    # print("No match found")
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
    browser_version = '.'.join(user_agent.browser.version_string.split('.')[:2])
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
    os_version = '.'.join(user_agent.os.version_string.split('.')[:2])
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
    # print(f"Browser CPE : {browser_cpe}")
    # print(f"OS CPE      : {os_cpe}")
    vulnerabilities = []
    try:
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
                    
                    # days_since_published = (datetime.now() - published_date).days
                    if published_date.year < 2020:
                        # print("Published date is before 2020")
                        continue
                    if True: #  days_since_published < 90 or  pas un bon critère
                        all_criteria, config_corresponds = extract_cve_configurations(vuln, browser_cpe, os_cpe)
                        if config_corresponds:
                            specific_match = config_corresponds and len(all_criteria) > 0
                            cve_id, description, highest_score, highest_severity = extract_cve_data(vuln)
                            if highest_score > 8 or highest_severity in ['HIGH', 'CRITICAL'] or (specific_match and highest_score > 6.5):
                                # print(f"Published Date: {published_date.strftime('%Y-%m-%d')}")
                                # specific_match_str = " - >>> Specific match" if specific_match else ""
                                # print(f"{cve_id} {published_date.strftime('%Y-%m-%d')} - Score: {highest_score}, Severity: {highest_severity}{specific_match_str}")
                                vulnerabilities.append({
                                    'id': cve_id,
                                    'published_date': published_date,
                                    'description': description,
                                    'highest_score': highest_score,
                                    'highest_severity': highest_severity,
                                    'specific_match': specific_match,
                                })
                                # print(f"Config corresponds: {config_corresponds}")
                                # print(f"Configurations: {all_criteria}")
                    # # quit()
                    # print("#" * 40)
            except Exception as e:
                print(f"Error processing vulnerabilities: {e}")
                return vulnerabilities
        else:
            print(f"Error: {response.status_code}")
            return vulnerabilities
    except Exception as e:
        print(f"Error fetching CVE data: {e}")
        return vulnerabilities
    return vulnerabilities


def search_cpe_vulnerable_date(cpe):
    release_date = None
    try:
        URL = f"https://services.nvd.nist.gov/rest/json/cpes/2.0?cpeMatchString={cpe}"
        # print(f"URL: {URL}")
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
                        # print(f"Release Date: {release_date.strftime('%Y-%m-%d')} - Days since release: {days_since_release}")
                        # print(f"Vulnerable since: {release_date.strftime('%Y-%m-%d')} - Days since vulnerable: {days_since_release}")
                        return release_date
            except Exception as e:
                print(f"Error processing release date: {e}")
                return release_date
        else:
            print(f"Error: {response.status_code}")
            return release_date
    except Exception as e:
        print(f"Error fetching CPE data: {e}")
        return release_date


def search_user_agent_vulnerable(user_agent_string, verbose=False):
    browser_cpe, os_cpe = get_cpe(user_agent_string)
    if verbose: print(f"Browser CPE          : {browser_cpe}")
    if verbose: print(f"OS CPE               : {os_cpe}")
    last_version_browser = lv.get_last_version(browser_cpe)
    try:
        last_version_browser = '.'.join(last_version_browser.split('.')[:2])
    except Exception as e:
        pass
    last_version_os = lv.get_last_version(os_cpe)
    try:
        last_version_os = '.'.join(last_version_os.split('.')[:2])
    except Exception as e:
        pass
    version_browser_outdated = under_cpe_version(browser_cpe, ':'.join(browser_cpe.split(':')[:5]) + ':' + last_version_browser)
    # if last_version_browser < browser_cpe, set last_version_browser = browser_cpe
    if under_cpe_version(':'.join(browser_cpe.split(':')[:5]) + ':' + last_version_browser, browser_cpe):
        last_version_browser = '.'.join(browser_cpe.split(':')[5].split('.')[:2])
    version_os_outdated = under_cpe_version(os_cpe, ':'.join(os_cpe.split(':')[:5]) + ':' + last_version_os)
    if verbose: print(f"Last version browser : {last_version_browser} - Is outdated : {version_browser_outdated}")
    if verbose: print(f"Last version OS      : {last_version_os} - Is outdated : {version_os_outdated}")
    vulnerable_date_browser = search_cpe_vulnerable_date(browser_cpe)
    vulnerable_date_os = search_cpe_vulnerable_date(os_cpe)
    if verbose: print(f"Browser vulnerable since : {vulnerable_date_browser.strftime('%Y-%m-%d') if vulnerable_date_browser else '/'}")
    if verbose: print(f"OS vulnerable since      : {vulnerable_date_os.strftime('%Y-%m-%d') if vulnerable_date_os else '/'}")
    vulnerabilities = search_cve_by_cpe(browser_cpe, os_cpe)[::-1]
    if verbose: print(f"Vulnerabilities      :")
    i = 0
    max_vuln_print = 5
    for vuln in vulnerabilities:
        if i > max_vuln_print:
            if verbose: print(f"+ {len(vulnerabilities) - max_vuln_print} more vulnerabilities")
            break
        if verbose: print(f"  - {vuln['id']} - {vuln['published_date'].strftime('%Y-%m-%d')} - Score: {vuln['highest_score']}, Severity: {vuln['highest_severity']}")
        if vuln['specific_match']:
            if verbose: print(f"    - Specific match")
            if verbose: print(f"    - Description: {vuln['description']}")
        i += 1
    
    high_severity_count = sum(1 for vuln in vulnerabilities if vuln['highest_severity'] == 'HIGH')
    critical_severity_count = sum(1 for vuln in vulnerabilities if vuln['highest_severity'] == 'CRITICAL')
        
    # input("Press Enter to continue...")
    if verbose: print('\n'*5)
    if verbose: print("-" * 50)
    
    return {
        'browser_cpe': browser_cpe,
        'os_cpe': os_cpe,
        'last_version_browser': last_version_browser,
        'last_version_os': last_version_os,
        'version_browser_outdated': version_browser_outdated,
        'version_os_outdated': version_os_outdated,
        'vulnerable_date_browser': vulnerable_date_browser,
        'vulnerable_date_os': vulnerable_date_os,
        'vulnerabilities': vulnerabilities,
        'high_severity_count': high_severity_count,
        'critical_severity_count': critical_severity_count,
    }


if __name__ == "__main__":
    # Load user agents from file
    with open("user-agents-samples.txt", "r") as f:
        user_agents = f.readlines()
    user_agents = [ua.strip() for ua in user_agents if not ua.startswith('---')]
    
    # Print cpe strings for each user agent
    print("- " * 25)
    for user_agent_string in user_agents:
        infos = search_user_agent_vulnerable(user_agent_string, verbose=False)
        
        print(f"User agent: {user_agent_string}")
        print(f"Browser CPE: {infos['browser_cpe']}")
        print(f"OS CPE: {infos['os_cpe']}")
        print(f"Last version browser: {infos['last_version_browser']}, Is outdated: {infos['version_browser_outdated']}")
        print(f"Last version OS: {infos['last_version_os']}, Is outdated: {infos['version_os_outdated']}")
        # if infos['vulnerable_date']:
        #     print(f"Vulnerable since: {infos['vulnerable_date'].strftime('%Y-%m-%d')} ({(datetime.now() - infos['vulnerable_date']).days} days)")
        if infos['vulnerable_date_browser']:
            print(f"Browser vulnerable since: {infos['vulnerable_date_browser'].strftime('%Y-%m-%d')} ({(datetime.now() - infos['vulnerable_date_browser']).days} days)")
        if infos['vulnerable_date_os']:
            print(f"OS vulnerable since: {infos['vulnerable_date_os'].strftime('%Y-%m-%d')} ({(datetime.now() - infos['vulnerable_date_os']).days} days)")
        
        print(f"Vulnerabilities:")
        i = 0
        for vuln in infos['vulnerabilities']:
            print(f"  - {vuln['id']} - {vuln['published_date'].strftime('%Y-%m-%d')} - Score: {vuln['highest_score']}, Severity: {vuln['highest_severity']}")
            if vuln['specific_match']:
                print(f"    - Specific match")
                print(f"    - Description: {vuln['description']}")
            i += 1
            if i > 5:
                print(f"+ {len(infos['vulnerabilities']) - 5} more vulnerabilities")
                break
        print(f"High severity vulnerabilities: {infos['high_severity_count']}")
        print(f"Critical severity vulnerabilities: {infos['critical_severity_count']}")
        print("-" * 50)
        
        input("Press Enter to continue...")
    
    quit()
    
    