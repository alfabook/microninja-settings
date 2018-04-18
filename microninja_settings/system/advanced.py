#!/usr/bin/env python

# advanced.py
#
# Copyright (C) 2014, 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# Contains the advanced backend functions

# Copyright (C) 2016 Alfabook srl
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
# rebadged with microninja
# only local whitelist
# Italian translation

import os
import shutil
import hashlib
import subprocess
import signal
import urllib2
from bs4 import BeautifulSoup
import gzip
import re

from microninja.logging import logger
from microninja_settings.system.get_username import get_first_username

from microninja_settings.common import settings_dir
from microninja.utils import read_file_contents, write_file_contents, \
    read_file_contents_as_lines, read_json, write_json, ensure_dir, \
    get_user_unsudoed, chown_path
from microninja.network import set_dns, restore_dns_interfaces, \
    clear_dns_interfaces, refresh_resolvconf
from microninja_settings.config_file import get_setting

password_file = "/etc/microninja-parental-lock"
hosts_file = '/etc/hosts'
hosts_file_backup = '/etc/microninja-hosts-parental-backup'
hosts_mod_comment = '# Modified to add username'

chromium_policy_file = '/etc/chromium/policies/managed/policy.json'
sentry_config = os.path.join(settings_dir, 'sentry')

youtube_safe_cookie = '/usr/share/microninja-video/cookies/youtube_safe/cookies.db'
youtube_nosafe_cookie = '/usr/share/microninja-video/cookies/youtube_nosafe/cookies.db'
browser_safe_cookie = '/usr/share/microninja-video/cookies/browser_safe/cookies.db'
browser_nosafe_cookie = '/usr/share/microninja-video/cookies/browser_nosafe/cookies.db'
midori_cookie = '.config/midori'
youtube_cookie = '.config/midori/youtube'

username = get_user_unsudoed()

# TODO: is this needed?
if username != 'root':
    blacklist_file = os.path.join(settings_dir, 'blacklist')
    whitelist_file = os.path.join(settings_dir, 'whitelist')


def get_parental_enabled():
    enabled = os.path.exists(password_file)
    logger.debug('get_parental_enabled: {}'.format(enabled))
    return enabled


def get_parental_level():
    if not get_parental_enabled():
        return -1

    return get_setting('Parental-level')


def set_parental_enabled(setting, _password):
    logger.debug('set_parental_enabled: {}'.format(setting))

    # turning on
    if setting:
        logger.debug('enabling')

        logger.debug('setting password')
        write_file_contents(password_file, encrypt_password(_password))

        logger.debug('making the file root read-only')
        os.chmod(password_file, 0400)

        logger.debug('enabling parental controls')
        set_parental_level(get_parental_level())

        msg = "Parental control abilitato!"
        logger.debug(msg)

        return True, msg

    # turning off
    else:
        # password matches
        if read_file_contents(password_file) == encrypt_password(_password):
            logger.debug('password accepted, disabling')

            logger.debug('clearing password')
            os.remove(password_file)

            logger.debug('disabling parental controls')
            set_parental_level(-1)

            msg = "Parental control disabilitato!"
            logger.debug(msg)

            return True, msg

        # password doesn't match
        else:
            msg = "Password doesn't match\nleaving parental lock enabled!"
            logger.debug(msg)

            return False, msg


def encrypt_password(str):
    return hashlib.sha1(str).hexdigest()


def authenticate_parental_password(passwd):
    return read_file_contents(password_file) == encrypt_password(passwd)


def set_hostname_postinst():
    # when running as post install, get the existing first user and set as host name
    new_hostname = get_first_username()

    if new_hostname is None:
        logger.warn("No first user")
    else:
        set_hostname(new_hostname)


def edit_hosts_file(path, new_hostname):
    try:
        hosts = read_file_contents(path)
        hosts += '\n' + hosts_mod_comment + '\n'
        hosts += '127.0.0.1\t{}\n'.format(new_hostname)
        write_file_contents(path, hosts)
    except:
        logger.error("exception while changing change {}".format(path))


def set_hostname(new_hostname):
    if os.environ['LOGNAME'] != 'root':
        logger.error("Error: Settings must be executed with root privileges")

    # Check username chars
    new_hostname = re.sub('[^a-zA-Z0-9]', '', new_hostname).lower()

    if new_hostname == '':
        logger.error('no letters left in username after removing illegal ones')
        return

    if new_hostname == 'microninja':
        logger.info(' not tryng to set hostname as it is the same as the default')
        return

    # check for missing hosts file
    if not os.path.exists(hosts_file):
        create_empty_hosts()

    # check if already done
    curr_hosts = read_file_contents_as_lines(hosts_file)
    if hosts_mod_comment in curr_hosts:
        logger.warn('/etc/hosts already modified, not changing')
        return

    # actually edit the hosts file
    edit_hosts_file(hosts_file, new_hostname)

    # edit the backup file.
    if os.path.exists(hosts_file_backup):
        edit_hosts_file(hosts_file_backup, new_hostname)

    try:
        write_file_contents('/etc/hostname', new_hostname + '\n')
    except:
        logger.error("exception while changing change /etc/hostname")


def create_empty_hosts():
    import platform
    hostname = platform.node()
    new_hosts = '127.0.0.1   localhost\n127.0.1.1   {}\n'.format(hostname)

    logger.debug('writing new hosts file')
    write_file_contents(hosts_file, new_hosts)

    logger.debug('restoring original hosts permission')
    os.chmod(hosts_file, 0644)


def add_blacklist_host(hosts, site_url):
    '''
    Add a site url to the hosts blacklist
    Both direct, and with "www." prefix
    '''
    url_pattern = '127.0.0.1\t{}\n'
    www_pattern = '127.0.0.1\twww.{}\n'

    hosts.append(url_pattern.format(site_url))
    hosts.append(www_pattern.format(site_url))
    return hosts


def add_safesearch_blacklist(hosts):
    '''
    Prevents surfing to generic search engine sites by adding them to the blacklist
    '''

    # import pycountry here as it takes a long time to import. 
    import pycountry
    logger.debug('Applying safesearch settings')
    # Block search sites
    search_sites = [
        'google.com',
        'google.it',
        'bing.com',
        'bing.it',
        'it.yahoo.com',
        'search.yahoo.com',
        'uk.search.yahoo.com',
        'it.search.yahoo.com',
        'it.ask.com',
        'ask.com',
        'uk.ask.com',  # pycountry does not return "uk", but "gb"
        'search.aol.com',
        'aolsearch.com',
        'search.com',
        'uk.search.com',
        'wow.com',
        'webcrawler.com',
        'zoo.com',  # Webcrawler sometimes redirects to zoo.com
        'mywebsearch.com',
        'home.mywebsearch.com',
        'infospace.com',
        'info.com',
        'duckduckgo.com',
        'blekko.com',
        'contenko.com',
        'dogpile.com',
        'alhea.com',
        'uk.alhea.com']

    # Blacklist major search engines
    for site in search_sites:
        add_blacklist_host(hosts, site)

    # Add subdomains only to those search engines that need it
    for country in pycountry.countries:

        add_blacklist_host(hosts, 'google.{}'.format(country.alpha2.lower()))
        add_blacklist_host(hosts, '{}.ask.com'.format(country.alpha2.lower()))
        add_blacklist_host(hosts, '{}.search.yahoo.com'.format(country.alpha2.lower()))
        add_blacklist_host(hosts, 'search.yahoo.{}'.format(country.alpha2.lower()))
        add_blacklist_host(hosts, '{}.search.com'.format(country.alpha2.lower()))
        add_blacklist_host(hosts, '{}.wow.com'.format(country.alpha2.lower()))
        add_blacklist_host(hosts, '{}.webcrawler.com'.format(country.alpha2.lower()))

        # Some search engines are redirecting to zoo.com and possibly [country]
        add_blacklist_host(hosts, 'zoo.{}'.format(country.alpha2.lower()))

        add_blacklist_host(hosts, '{}.info.com'.format(country.alpha2.lower()))
        add_blacklist_host(hosts, '{}.alhea.com'.format(country.alpha2.lower()))

    # Google: Add extra seconday-level domains not covered in ISO 3166
    # http://en.wikipedia.org/wiki/Second-level_domain
    # http://en.wikipedia.org/wiki/List_of_Google_domains
    second_level_domains = [
        'com.af', 'com.af', 'com.ag', 'com.ai', 'co.ao', 'com.ar', 'com.au', 'com.bd', 'com.bh', 'com.bn', 'com.bo', 'com.br',
        'co.bw', 'com.bz', 'com.kh', 'co.ck', 'g.cn', 'com.co', 'co.cr', 'com.cu', 'com.cy', 'com.do', 'com.ec', 'com.eg',
        'com.et', 'com.fj', 'com.gh', 'com.gi', 'com.gt', 'com.hk', 'co.id', 'co.il', 'co.in', 'com.jm', 'co.jp',
        'co.ke', 'co.kr', 'com.kw', 'com.lb', 'com.lc', 'co.ls', 'com.ly', 'co.ma', 'com.mm', 'com.mt', 'com.mx',
        'com.my', 'com.mz', 'com.na', 'com.nf', 'com.ng', 'com.ni', 'com.np', 'co.nz', 'com.om', 'com.pa', 'com.pe',
        'com.ph', 'com.pk', 'com.pg', 'com.pr', 'com.py', 'com.qa', 'com.sa', 'com.sb', 'com.sg', 'com.sl', 'com.sv',
        'co.th', 'com.tj', 'com.tn', 'com.tr', 'com.tw', 'co.tz', 'com.ua', 'co.ug', 'co.uk', 'com.uy', 'co.uz',
        'com.vc', 'co.ve', 'co.vi', 'com.vn', 'co.za', 'co.zm', 'co.zw', 'fr', 'es', 'de', 'pt']

    for subdomain in second_level_domains:
        add_blacklist_host(hosts, 'google.{}'.format(subdomain))

    return hosts


def set_hosts_blacklist(enable, block_search,
                        blacklist_file='/usr/share/microninja-settings/media/Parental/parental-hosts-blacklist.gz',
                        blocked_sites=None, allowed_sites=None):
    logger.debug('set_hosts_blacklist: {}'.format(enable))

    if not os.path.exists(hosts_file):
        create_empty_hosts()

    if enable:
        logger.debug('enabling blacklist')

        # sanity check: this is a big file, looks like the blacklist is already in place
        #if os.path.getsize(hosts_file) > 10000:
        if os.path.getsize(hosts_file) > 10000 and not ('www.google.com' not in open(hosts_file).read() and block_search) and not ('www.google.com' in open(hosts_file).read() and not block_search):
            logger.debug('skipping, hosts file is already too big')
        else:
            logger.debug('making a backup of the original hosts file')
            if not os.path.getsize(hosts_file) > 10000:
                shutil.copyfile(hosts_file, hosts_file_backup)
            else:
                shutil.copy(hosts_file_backup, hosts_file)

            logger.debug('appending the blacklist file')
            zipped_blacklist = gzip.GzipFile(blacklist_file)
            blacklist = zipped_blacklist.readlines()

            if block_search:
                blacklist = add_safesearch_blacklist(blacklist)

            # Append list of blacklisted hosts to system hostnames file
            with open(hosts_file, 'a') as f:
                for host_entry in blacklist:
                    f.write(host_entry)

            logger.debug('making the file root read-only')
            os.chmod(hosts_file, 0644)

        logger.debug('Removing allowed websites')
        if allowed_sites:
            for site in allowed_sites:
                os.system('sed -i /{}/d {}'.format(site, hosts_file))

        logger.debug('Adding user-specified blacklist websites')
        if blocked_sites:
            for site in blocked_sites:
                blocked_str = ('127.0.0.1    www.{site}\n'
                               '127.0.0.1    {site}'.format(site=site))

                os.system('grep -q -F "{str}" {file} || echo "{str}" >> {file}'
                          .format(str=blocked_str, file=hosts_file))

    else:
        logger.debug('disabling blacklist')

        if os.path.exists(hosts_file_backup):
            logger.debug('restoring original backup file')
            shutil.copy(hosts_file_backup, hosts_file)

        else:
            logger.debug('cannot restore original backup file, creating new file')
            create_empty_hosts()


# Ultimate parental lock functions
####################################################

def set_ultimate_parental(enable):
    if enable:
        # if server is running, kill it and restart it
        kill_server()

        # this is to get the most up to date whitelist
        restore_dns_interfaces()
        redirect_traffic_to_google()
        parse_whitelist_to_config_file(sentry_config)

        # Now set resolv.conf to point to localhost
        clear_dns_interfaces()
        redirect_traffic_to_localhost()
        launch_sentry_server(sentry_config)

    else:
        restore_dns_interfaces()
        redirect_traffic_to_google()
        kill_server()


def redirect_traffic_to_google():
    google_servers = [
        '8.8.8.8',
        '8.8.4.4'
    ]
    set_dns(google_servers)
    refresh_resolvconf()


def parse_whitelist_to_config_file(config):
    whitelist = get_whitelist()

    new_config = (
        '{\n'
        '    \"port\": 53,\n'
        '    \"host\": \"127.0.0.1\",\n'
        '    \"rules\": [\n'
    )
    lines = whitelist.split('\n')
    for line in lines:
        # Add line to whitelist if is non empty and doesn't start with a #
        line = line.strip()
        if line and not line.startswith('#'):
            allowed_url = (
                "        \"resolve ^(.*){} using 8.8.8.8, 8.8.4.4\",\n".format(line)
            )
            new_config += allowed_url
            logger.debug("url {} being allowed in ultimate parental control".format(allowed_url))

    block_everything_else = (
        "        \"block ^(.*)\"\n"
        "    ]\n"
        "}"
    )
    new_config += block_everything_else

    logger.debug('new ultimate parental control config: {}'.format(new_config))
    g = open(config, 'w+')
    g.write(new_config)
    g.close()
    logger.debug("finished writing new ultimate parental control to {}".format(config))


def get_whitelist():
    # Try and get the whitelist from online.  If this fails,
    # get it locally.
    #try:
    #    online_whitelist = (
    #        "https://raw.githubusercontent.com/KanoComputing/kano-settings/"
    #        "master/WHITELIST"
    #    )
    #    html = urllib2.urlopen(online_whitelist).read()
    #    text = BeautifulSoup(html).get_text().encode('ascii', 'ignore')
    #    logger.debug('Using online whitelist')
    #    return text
    #except:
        # If there's an exception, possibly because there is no internet.
	whitelist = os.path.join(settings_dir, 'WHITELIST')
	f = open(whitelist, 'r')
	text = f.read()
	f.close()
	logger.debug('Using local whitelist')
	return text


def redirect_traffic_to_localhost():
    set_dns(['127.0.0.1'])
    refresh_resolvconf()


def launch_sentry_server(filename):
    subprocess.Popen(["sentry -c {}".format(filename)], shell=True)


def kill_server():
    # Search for "sentry -c /home/$USERNAME/.kano-settings/CONFIG"
    # in "ps aux | grep -r sentry" output
    ps_cmd = ["ps", "-A"]
    search_string = "sentry"

    ps_process = subprocess.Popen(ps_cmd, stdout=subprocess.PIPE)
    output, err = ps_process.communicate()
    lines = output.split('\n')

    # Could be very intensive
    for line in lines:
        # If the line contains the output we're looking for (i.e. is running
        # the process we're interested in)
        if search_string in line:
            pid = int(filter(None, line.split(" "))[0])
            os.kill(pid, signal.SIGKILL)
            break

####################################################


def set_chromium_policies(policies):
    if not os.path.exists(chromium_policy_file):
        ensure_dir(os.path.dirname(chromium_policy_file))
        policy_config = {}
    else:
        policy_config = read_json(chromium_policy_file)

    for policy in policies:
        policy_config[policy[0]] = policy[1]

    write_json(chromium_policy_file, policy_config)


def set_chromium_parental(enabled):
    # Policy keys and values can be found at:
    #     www.chromium.org/administrators/policy-list-3
    policies = {
        # Chromium_setting: (disabled_value, enabled_value),
        'IncognitoModeAvailability': (0, 1)
    }
    # Set incognito mode availability for Chromium
    new_policy = [(key, policies[key][enabled]) for key in policies]
    set_chromium_policies(new_policy)


def set_dns_parental(enabled):
    open_dns_servers = [
        '208.67.222.123',
        '208.67.220.123'
    ]

    google_servers = [
        '8.8.8.8',
        '8.8.4.4'
    ]

    if enabled:
        logger.debug('Enabling parental DNS servers (OpenDNS servers)')
        set_dns(open_dns_servers)
        clear_dns_interfaces()
    else:
        logger.debug('Disabling parental DNS servers (Google servers)')
        set_dns(google_servers)
        restore_dns_interfaces()

    refresh_resolvconf()


def set_everyone_cookies(enabled=None):
    if enabled is None:
        enabled = get_parental_level() >= 2

    username = []
    try:
        for username in os.listdir("/home/"):
            set_user_cookies(enabled, username)
    except:
        logger.error('Error applying Midori security to users ({})'.format(','.join(username)))


def set_user_cookies(enabled=None, username=None):
    if enabled is None:
        enabled = get_parental_level() >= 2
    if username is None:
        return

    # The cookie enables/disables safety mode in YouTube (Midori)
    # The .db files are located in /usr/share/kano-video
    homedir = "/home/{}".format(username)
    if not os.path.isdir(homedir):
        logger.error("Could not access user home dir: {}".format(homedir))
        return

    # Browser: Cookie needs to be copied to /home/USERNAME/.config/midori
    midori_cookie_path = '{}/{}'.format(homedir, midori_cookie)
    if os.path.exists(browser_safe_cookie) and \
            os.path.exists(browser_nosafe_cookie) and \
            os.path.exists(midori_cookie_path):

        if enabled:
            logger.debug('Enabling Browser Safety mode for browser on user {}'.format(username))
            browser_cookie = browser_safe_cookie
        else:
            logger.debug('Disabling Browser Safety mode for browser on user {}'.format(username))
            browser_cookie = browser_nosafe_cookie

        # Copy cookie for this user
        shutil.copy(browser_cookie, midori_cookie_path)

        # Set correct permissions on file
        chown_path('{}/cookies.db'.format(midori_cookie_path), username, username)

    # YT: copy yo /home/USERNAME/.config/midori/youtube (kano-video-browser)
    youtube_cookie_path = '{}/{}'.format(homedir, youtube_cookie)
    if os.path.exists(youtube_safe_cookie) and \
       os.path.exists(youtube_nosafe_cookie) and \
       os.path.exists(youtube_cookie_path):

        if enabled:
            logger.debug('Enabling YouTube Safety mode for kano-video-browser on user {}'.format(username))
            yt_cookie = youtube_safe_cookie
        else:
            logger.debug('Disabling YT Safety mode for kano-video-browser on user {}'.format(username))
            yt_cookie = youtube_nosafe_cookie

        # Copy cookie for this user
        shutil.copy(yt_cookie, youtube_cookie_path)

        # Set correct permissions on file
        chown_path('{}/cookies.db'.format(youtube_cookie_path), username, username)


def read_listed_sites():
    return (
        read_file_contents_as_lines(blacklist_file),
        read_file_contents_as_lines(whitelist_file)
    )


def write_whitelisted_sites(whitelist):
    write_file_contents(whitelist_file, '\n'.join(whitelist))


def write_blacklisted_sites(blacklist):
    write_file_contents(blacklist_file, '\n'.join(blacklist))


def set_parental_level(level_setting):
    # NB, we pass -1 to disable all
    feature_levels = [
        # Low
        ['blacklist', 'cookies'],
        # Medium
        ['dns'],
        # High
        ['chromium', 'search_engines'],
        # Ultimate
        ['ultimate']
    ]

    enabled = []

    for level, features in enumerate(feature_levels):
        if level <= level_setting:
            enabled = enabled + features

    logger.debug('Setting parental control to level {}'.format(level_setting))

    if 'ultimate' in enabled:
        set_ultimate_parental('ultimate' in enabled)
    else:
        set_ultimate_parental(False)
        set_chromium_parental('chromium' in enabled)
        set_dns_parental('dns' in enabled)
        set_everyone_cookies('cookies' in enabled)

    # Blacklist setup
    blacklist, whitelist = read_listed_sites()

    set_hosts_blacklist('blacklist' in enabled, 'search_engines' in enabled,
                        blocked_sites=blacklist, allowed_sites=whitelist)
