#!/usr/bin/python3

# Written by sam.k.tan@oracle.com
# 13-AUG-2024


import os
import time
import datetime
import re
import getpass
import requests


def timer_decorator(inner_function):
    """
    decorator to time a function
    """
    def outer_function(*args, **kwargs):
        start_time = time.perf_counter()
        a_result = inner_function(*args, **kwargs)
        end_time = time.perf_counter()
        elapsed_time = end_time - start_time
        elapsed_minutes, elapsed_seconds = divmod(elapsed_time, 60)
        print(f"  ... {inner_function.__name__} : {elapsed_minutes:02.0f} minutes {elapsed_seconds:02.2f} seconds")
        return a_result
    return outer_function


def get_support_bundles(sourcedir):
    support_bundles = []
    for f_name in os.listdir(sourcedir):
        f_path = os.path.join(sourcedir, f_name)
        f_is_dir = os.path.isdir(f_path)
        f_size = os.path.getsize(f_path)
        f_modified = os.path.getmtime(f_path)

        bundle_entry = {
            'name': f_name,
            'path': f_path,
            'is_dir': f_is_dir,
            'size': f_size if not f_is_dir else -1,
            'modified': time.localtime(f_modified),
            'timestamp': parse_for_date(f_name),
            'sr': parse_for_sr(f_name),
        }
        support_bundles += [bundle_entry]

    support_bundles = sorted(support_bundles, key=lambda k: (k['timestamp'] or 0))
    return(support_bundles)


def parse_for_date(a_string):
    DATE_FORMAT_REGEX = "[^0-9]([0-9]{8}T[0-9]{9})[^0-9]?"
    DATE_FORMAT_STRING = "%Y%m%dT%H%M%S%f"

    date_object = None
    date_regex = re.compile(DATE_FORMAT_REGEX, re.IGNORECASE)
    date_search = date_regex.search(a_string)
    if date_search:
        date_string = date_search.group(1)
        date_object = datetime.datetime.strptime(date_string, DATE_FORMAT_STRING)
    return date_object


def parse_for_sr(a_string):
    SR_FORMAT_REGEX = "(3-[0-9]{11})[^0-9]"

    sr_string = None
    sr_regex = re.compile(SR_FORMAT_REGEX, re.IGNORECASE)
    sr_search = sr_regex.search(a_string)
    if sr_search:
        sr_string = sr_search.group(1)
    return sr_string


def format_size_to_string(a_size):
    units = [" B", "KB", "MB", "GB", "TB"]
    scale = 1000

    for u in units:
        if a_size < scale:
            break
        a_size, _ = divmod(a_size, scale)

    size_string = f"{a_size:,d} {u}"
    return size_string


def prompt_for_support_bundle(support_bundles):
    DATE_OUTPUT_STRING = "%Y-%m-%d %H:%M:%S"

    print(f'{"#": >2}   {"Filename": <64}   {"Size": >8}   {"Timestamp": <20}   {"SR #":13s}')
    for i, support_bundle_entry in enumerate(support_bundles, start=1):
        f_name = support_bundle_entry['name']
        f_size = support_bundle_entry['size']
        f_is_dir = support_bundle_entry['is_dir']
        f_timestamp = support_bundle_entry['timestamp']
        f_sr = support_bundle_entry['sr'] or ""

        index_string = f"{i:02d}" if not f_is_dir else "--"
        size_string = format_size_to_string(f_size) if not f_is_dir else "<DIR>"
        timestamp_string = f_timestamp.strftime(DATE_OUTPUT_STRING) if f_timestamp is not None else ""
        print(f"{index_string:2s} : {f_name:64s} : {size_string:>8s} : {timestamp_string:20s} : {f_sr:13s}")
    choice_input = input(f"Enter support bundle #: (1 - {len(support_bundles)}, 0 to exit): ")

    choice = None
    try:
        choice_number = int(choice_input)-1
        choice = support_bundles[choice_number] if choice_number >= 0 else None
        if choice['is_dir']:
            choice = None
    except:
        pass
    return choice


def get_upload_details(support_entry):
    bundle_path = support_entry['path']
    bundle_sr = support_entry['sr']

    print(f"Support bundle path: {bundle_path}")

    if bundle_sr is None:
        bundle_sr = input("Enter SR #: ")
    else:
        print(f"SR #: {bundle_sr}")

    bundle_login = input("Enter MOS login: ")
    bundle_password = getpass.getpass("Enter MOS password: ")
    upload_details = {
	    'bundle': os.path.basename(bundle_path),
        'path': bundle_path,
        'sr': bundle_sr,
        'login': bundle_login,
        'password': bundle_password,
    }
    return upload_details


@timer_decorator
def perform_upload(upload_details):
    https_proxy = os.environ.get('https_proxy')
    proxies = {
        'https': https_proxy,
    } if https_proxy is not None else None

    mos_login = upload_details['login']
    mos_password = upload_details['password']
    bundle_name = upload_details['bundle']
    bundle_path = upload_details['path']
    bundle_sr = upload_details['sr']

    mos_url = f"https://transport.oracle.com/upload/issue/{bundle_sr}/{bundle_name}"

    CURL_CLI = f'curl \
	--verbose \
	--proxy "{https_proxy}" \
	--user "{mos_login}" \
	--upload-file "{bundle_path}" \
    "https://transport.oracle.com/upload/issue/{bundle_sr}/"'

    print(f"Uploading {bundle_path}")
    print(f"... to {mos_url}")
    print(f"... via proxies {proxies}")
    print(f"... for user {mos_login}")

    with open(bundle_path, "rb") as bundle_file:
        response = requests.put(mos_url, data=bundle_file, auth=(mos_login, mos_password), proxies=proxies)
    if response.status_code == 200:
        print(f"{response.status_code} OK - upload successful.")
    elif response.status_code == 401:
        print(f"{response.status_code} Unauthorized - please check your login and password.")
    elif response.status_code == 403:
        print(f"{response.status_code} Forbidden - please check the SR # is valid and that you have access to it.")
    else:
        print(f"{response.status_code} Error - please check your network settings and your proxy server.")
        print("If you want to test using `curl`, here is the CLI equivalent:")
        print(f"{CURL_CLI}")
    return response.status_code


def main():
    SUPPORT_BUNDLES_FOLDER="/nfs/shared_storage/support_bundles/"

    support_bundles = get_support_bundles(SUPPORT_BUNDLES_FOLDER)
    if len(support_bundles) == 0:
        print(f"No support bundles found in {SUPPORT_BUNDLES_FOLDER}. Generate some support bundles first then run this command again.")
        exit(0)
    selected_support_bundle = prompt_for_support_bundle(support_bundles)
    if selected_support_bundle is None:
        exit(0)
    upload_details = get_upload_details(selected_support_bundle)
    result = perform_upload(upload_details)
    return 0 if result == 200 else result


if __name__ == '__main__':
    main()
