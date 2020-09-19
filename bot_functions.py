#!/usr/bin/python -tt
# Project: Dropbox (Indigo Wire Networks)
# Filename: bot_functions.py
# claudia
# PyCharm

# from __future__ import absolute_import, division, print_function

__author__ = "Claudia de Luna (claudia@indigowire.net)"
__version__ = ": 1.0 $"
__date__ = "2019-06-23"
__copyright__ = "Copyright (c) 2018 Claudia"
__license__ = "Python"

import sys
import datetime
import argparse
import os
import csv
import re
# import openpyxl
# import cat_config_utils
import difflib
import requests
import dotenv
import json


def get_time(msg):
    """
    Sample function that returns the current time for a provided timezone
    :param incoming_msg: The incoming message object from Teams
    :return: A Response object based reply
    """
    # Extract the message content, without the command "/time"

    # message = msg.text.split()
    message = msg.split()
    timezone = message[2]
    print(timezone)
    # timezone = app.extract_message("SparkBot /time", incoming_msg.text).strip()

    # Craft REST API URL to retrieve current time
    #   Using API from http://worldclockapi.com
    base_url = "http://worldtimeapi.org/api/timezone/"

    url = f"{base_url}{timezone}"

    r = requests.get(url)

    print(r)
    print(r.text)
    print(dir(r))
    print(json.dumps(r.json(), indent=4))
    print(r.ok)

    # If an invalid timezone is provided, the serviceResponse will include
    # error message
    # if r["serviceResponse"]:
    #     return "Error: " + r["serviceResponse"]
    #
    # # Format of returned data is "YYYY-MM-DDTHH:MM<OFFSET>"
    # #   Example "2018-11-11T22:09-05:00"
    # returned_data = r["currentDateTime"].split("T")
    # cur_date = returned_data[0]
    # cur_time = returned_data[1][:5]
    # timezone_name = r["timeZoneName"]
    #
    # # Craft a reply string.
    # reply = "In {TZ} it is currently {TIME} on {DATE}.".format(
    #     TZ=timezone_name, TIME=cur_time, DATE=cur_date
    # )

    if r.ok:
        resp_json = r.json()
        # Format of returned data is "YYYY-MM-DDTHH:MM<OFFSET>"
        #   Example "2018-11-11T22:09-05:00"
        returned_data = resp_json["datetime"].split("T")
        cur_date = returned_data[0]
        cur_time = returned_data[1][:5]

        # Craft a reply string.
        reply = f"Timezone: {resp_json['timezone']} \n\tCurrent time is {cur_time} \n\tCurrent date is {cur_date} " \
                f"\n\tUTC Offset is {resp_json['utc_offset']}" \
                f"\n\tWeek Number is {resp_json['week_number']}"
    else:
        reply = f"ERROR! Response: {r}\n"

    print(reply)

    return reply


def rest_api_call(url, payload={}, cookie="", type="GET", content_type="text/plain" ):
    """

    :return:
    """

    headers = {
        'Content-Type': content_type,
        'Cookie': cookie
    }

    response = requests.request(type, url, headers=headers, data = payload, verify=False)

    # print(response)
    # print(dir(response))
    # print(response.json())

    return response


def diff_config_processing(dev_action, site_id):

    response_text = ''
    found_files = True
    dev_action = dev_action.strip().lower()

    region_dict = {
        "ea" : "EAME",
        "ap" : "APAC",
        "na" : "NA_LA",
        "la" : "NA_LA"
    }

    if re.search('all', dev_action):
        # Generate comprehensive config diff file for all configs
        pass
        response_text = "Future Function"

    elif re.search(r'\w{2}-\w{2}-\d{1,4}-\w+-\w{2,3}\d\d', dev_action):
        # Function was passed a valid device name
        siteid = re.search(r'\d{1,4}', dev_action)
        reg = re.search(r'^\w{2}', dev_action)
        print(reg)
        print(reg.group())
        region = region_dict[reg.group()]
        # site_id = siteid.group()
        device_name = dev_action

    else:
        response_text = f"ERROR! Bad parameter {dev_action}"

    print(f"==== device is {dev_action} calculated siteid is {siteid.group()}, passed site_id is {site_id}and region is {region}")

    # Base Path
    base_path = cat_config_utils.set_base_by_user()
    print(f"Base path is {base_path}")

    # Set Base Path for Staging Configs
    dd_path = os.path.join(base_path, "DimensionData", "Staging", "Phase_3_Staging")
    print(f"DD path is {dd_path}")
    dd_site_path = cat_config_utils.find_site_root(dd_path, region, site_id)
    print(f"DD Site path is {dd_site_path}")
    dd_cfg_dir = os.path.join(dd_site_path, 'Configs')
    print(f"DD Config DIR path is {dd_cfg_dir}")

    # Set Base Path for Final Configs
    site_path = cat_config_utils.find_site_root(base_path, region, site_id)
    final_cfg_dir = os.path.join(site_path, '04_Design_Engineering', 'Staging', 'Configs')
    print(f"Final Config DIR path is {final_cfg_dir}")


    #########
    #########
    ##
    #
    # Look for Staging Config File
    staging_file = "Staging Config File Not Found"
    sel_path, file_list = cat_config_utils.read_files_in_dir(dd_cfg_dir, ".txt")
    for a_file in file_list:
        if re.search(dev_action, a_file):
            staging_file = a_file


    # Look for Final Config File
    final_file = "Final Config File Not Found"
    sel_path, file_list = cat_config_utils.read_files_in_dir(final_cfg_dir, ".txt")
    for a_file in file_list:
        if re.search(dev_action, a_file):
            final_file = a_file

    staging_file_fp = os.path.join(dd_cfg_dir,staging_file)
    final_file_fp = os.path.join(final_cfg_dir,final_file)

    print(f"Staging file is {staging_file} \n and Final File is {final_file}")
    print(f"FULLPATH \nStaging file is {staging_file_fp} \n and Final File is {final_file_fp}")

    if re.search('File Not Found', staging_file):
        response_text = f"ERROR! STAGING Config File {device_name} was not found in \n\r\t{dd_cfg_dir}"
        found_files = False

    if re.search('File Not Found', final_file):
        response_text += f"\n\rERROR! FINAL Config File {device_name} was not found in \n\r\t{final_cfg_dir}"
        found_files = False

    if found_files:
        response_text = diff_config(staging_file_fp, final_file_fp)

        diff_config_http_report(staging_file_fp, final_file_fp)

    print(response_text)

    return response_text


def diff_config(f1, f2):

    staging_file = open(f1).readlines()
    latest_file = open(f2).readlines()

    diff_text = ''

    staging_fn = cat_config_utils.get_filename_from_fp(f1)
    latest_fn = cat_config_utils.get_filename_from_fp(f2)

    with open("diff_report.txt", "w") as df:

        diff_text = f"\n\r===== Differences between Staging File \n\r\t{staging_fn} " \
            f"\n\r===== and Approved File \n\r\t{latest_fn}\n\r"
        df.write(diff_text)
        for line in difflib.unified_diff(staging_file, latest_file):
            df.write(line)
            diff_text += line

    return diff_text


def diff_config_http_report(f1, f2):

    staging_file = open(f1).readlines()
    latest_file = open(f2).readlines()

    staging_fn = cat_config_utils.get_filename_from_fp(f1)
    latest_fn = cat_config_utils.get_filename_from_fp(f2)

    # diff = difflib.HtmlDiff().make_file(staging_file, latest_file, fromdesc=staging_fn, todesc=latest_fn, context=False, numlines=5)
    diff = difflib.HtmlDiff().make_file(staging_file, latest_file, fromdesc=staging_fn, todesc=latest_fn)
    with open("diff_report.html", "w") as df:
        df.write(diff)


def read_nsrfile_payload(path, debug=False):
    """
    Open and read the New Subnet Request
    """

    rows_w_data = []

    book = openpyxl.load_workbook(path, data_only=True)

    # print all tabs in workbook
    # print(book.sheetnames)


    # Data from BoM Tab of Implementation Workbook
    newsubnet_sheet = book['Sheet1']

    if debug:
        print(f"From rread_nsrfile_payload function \nPath: {path}")

    for row in range(1, newsubnet_sheet.max_row + 1):
        # print("row: {}".format(row))
        a_row=[]

        ## At the line that begins with "SUBTOTALS" end processing
        # end_processing_at_subtotal = equipment_sheet.cell(row=row, column=1)
        # end_proc = end_processing_at_subtotal.value

        # # Break out of for look when you hit the subtotal line
        # if end_proc and re.search('SUBTOTAL', end_proc):
        #     break

        # if there is a value in replace, strip off any white space
        # otherwise set to empty/false

        for col in range(1,15):
            val = newsubnet_sheet.cell(row=row, column=col)
            if type(val.value) == str:
                cell_value = val.value.strip()
            else:
                cell_value = val.value
            a_row.append(cell_value)

        rows_w_data.append(a_row)

    if debug:
        for line in rows_w_data:
            print(f"==== {line}")

    return rows_w_data


def read_nsrequestfile_payload(path, debug=False):
    """
    Open and read the New Subnet Request
    """

    rows_w_data = []

    book = openpyxl.load_workbook(path, data_only=True)

    # print all tabs in workbook
    # print(book.sheetnames)


    # Data from BoM Tab of Implementation Workbook
    newsubnet_sheet = book['Sheet1']

    if debug:
        print(f"From rread_nsrfile_payload function \nPath: {path}")

    for row in range(1, newsubnet_sheet.max_row + 1):
        # print("row: {}".format(row))
        a_row=[]

        site = newsubnet_sheet.cell(row=row, column=1)
        regexp = r"^\d{3,4}"
        # print(f"site {site.value}")

        if site.value is not None:
            # print(site.value)
            if re.search(regexp,site.value) or re.search("EISMS", site.value):

                for col in range(1,15):
                    status = newsubnet_sheet.cell(row=row, column=14)

                    # print(f"status {status.value} of type {type(status.value)}")
                    if status.value is not None:
                        val = newsubnet_sheet.cell(row=row, column=col)
                        if type(val.value) == str:
                            cell_value = val.value.strip()
                        else:
                            cell_value = val.value
                        a_row.append(cell_value)

                if a_row:
                    rows_w_data.append(a_row)
    if debug:
        for line in rows_w_data:
            print(f"==== {line}")

    return rows_w_data



def new_subnets(siteid):

    # Initialize summary string
    summary_string = ''
    print(f"SiteID provided is {siteid}")

    # Get Site Region so we can build path to subnet response
    with open('nt3_sites.csv') as csvfile:
        readCSV = csv.reader(csvfile, delimiter=',')
        for row in readCSV:

            if re.search(siteid, row[2]):
                print(f"SiteID provided is {siteid} in region {row[0]} and record found is {row}")
                region = row[0]
                break

    # Start of script execution
    start_time = datetime.datetime.now()

    base_path = cat_config_utils.set_base_by_user()
    site_path = cat_config_utils.find_site_root(base_path, region, siteid)
    lan_design_dir = os.path.join(site_path, '04_Design_Engineering', 'LAN_WAN')

    #########
    #########
    ## Load New Subnet Response (NSR)
    #
    print(f"Base Path is {base_path}\nSite Path is {site_path}")

    # Look for New Subnet Response File (Expecting one consolidated file)
    nsr_file = ''
    sel_path, file_list = cat_config_utils.read_files_in_dir(lan_design_dir, ".xlsx")
    for a_file in file_list:
        if re.search(r'subnets?[_|-]response', a_file):
            nsr_file = a_file

    # Abort if a subnet response file cannot be found.
    if not nsr_file:
        print(f"ERROR! New Subnet Response file could not be found!\nFile List searched is:\n{file_list}")
        # sys.exit("Aborting Program Execution - New Subnet Response File not found. Note: Script is searching for "
        #          "one file with subnets- or subnets_response.")
        summary_string += f"New Subnet Response file could not be found!\n\nFile List searched is:\n{file_list}" \
            f"\n\nThis means we have no response from IPDMIN or the response file has a non-standard name. "

    else:
        # Build the full path to the New Subnet Response file
        nsr_fp = os.path.join(lan_design_dir, nsr_file)

        # Get all valid rows in  New Subnet Response file
        rows_w_data = read_nsrfile_payload(nsr_fp, debug=False)

        header_row = rows_w_data.pop(0)

        # Initialize list to hold rows
        list_of_dict =[]

        for row in rows_w_data:
            if row[0]:
                # print(row)
                list_of_dict.append(cat_config_utils.list_row_to_dict(header_row, row))

        print()

        summary_string += f"======= New Subnet Requested for site {siteid} {start_time.ctime()}=======\r"

        for row in list_of_dict:
            #print(row)
            # print(f"New Subnet {row['Subnet']}/{row['Subnetmask']} on device {row['Device']}.\n\tNotes: {row['Justification']}")

            summary_string += f"\n\rNew {row['Subnet Type']} Subnet {row['Subnet']}/{row['Subnetmask']} on {row['Interface']} on device {row['Device']}."
            if row['Helper Address (Returned by IPAdmin)']:
                summary_string += f"\n\r\tHelpers provided by IPAdmin: {row['Helper Address (Returned by IPAdmin)']}"
            if row['Justification']:
                summary_string += f"\n\r\tNotes: {row['Justification']}"
            summary_string += f"\n\r"

        print(summary_string)

        fn = f"{siteid}_new_subnets.txt"

        with open(fn, "w") as f:
            f.write(summary_string)

    return summary_string


def read_cmufile_payload(path, debug=False):
    """
    Open and read the Updated Connectivity Matrix File
    """

    rows_w_data = []

    book = openpyxl.load_workbook(path, data_only=True)

    # print all tabs in workbook
    # print(book.sheetnames)


    # Data from BoM Tab of Implementation Workbook
    cm_sheet = book['ConnMatrix']

    if debug:
        print(f"From read_cmufile_payload function \nPath: {path}")

    for row in range(1, cm_sheet.max_row + 1):
        # print("row: {}".format(row))
        a_row=[]

        for col in range(1,41):
            val = cm_sheet.cell(row=row, column=col)
            if type(val.value) == str:
                cell_value = val.value.strip()
            else:
                cell_value = val.value
            a_row.append(cell_value)

        rows_w_data.append(a_row)

    if debug:
        for line in rows_w_data:
            print(f"==== {line}")

    return rows_w_data


def conn_matrix(siteid):

    # Start of script execution
    start_time = datetime.datetime.now()

    # Initialize summary string
    summary_string = ''
    region = f"No Region match for site: {siteid}"
    print(f"SiteID provided is {siteid}")

    # Get Site Region so we can build path to subnet response
    with open('nt3_sites.csv') as csvfile:
        readCSV = csv.reader(csvfile, delimiter=',')
        for row in readCSV:

            if re.search(siteid, row[2]):
                print(f"SiteID provided is {siteid} in region {row[0]} and record found is {row}")
                region = row[0]
                break

    base_path = cat_config_utils.set_base_by_user()
    site_path = cat_config_utils.find_site_root(base_path, region, siteid)
    lan_design_dir = os.path.join(site_path, '04_Design_Engineering', 'LAN_WAN')

    #########
    #########
    ## Load New Subnet Response (NSR)
    #
    print(f"Base Path is {base_path}\nSite Path is {site_path}")

    # Look for Connectivity Matrix Updated file
    cmu_file = ''
    cmu_working = False
    sel_path, file_list = cat_config_utils.read_files_in_dir(lan_design_dir, ".xlsx")
    for a_file in file_list:
        if re.search(r'connectivity_matrix[_|-]update', a_file):
            cmu_file = a_file

        if re.search(r'connectivity_matrix.xlsx', a_file):
            cmu_working = True

    # Abort if a subnet response file cannot be found.
    if not cmu_file:

        if cmu_working:

            print(f"WARNING! Updated Connectivity Matrix file could not be found!\nFile List searched is:\n{file_list}")
            # sys.exit("Aborting Program Execution - New Subnet Response File not found. Note: Script is searching for "
            #          "one file with subnets- or subnets_response.")
            summary_string += f"A final Updated Connectivity Matrix file could not be found however a Connectivity Matrix " \
                f"file (*not updated*) was found." \
                f"\n\nThis means the site is far enough along in the design so that the file can be generated but " \
                f"has not been updated and finalized and so its premature to share.  " \
                f"Please check with the Engineering Team for confirmation."
        else:

            print(f"ERROR! Updated Connectivity Matrix file could not be found!\nFile List searched is:\n{file_list}")
            # sys.exit("Aborting Program Execution - New Subnet Response File not found. Note: Script is searching for "
            #          "one file with subnets- or subnets_response.")
            summary_string += f"Updated Connectivity Matrix file could not be found!\n\nFile List searched is:\n{file_list}" \
                f"\n\nThis means we do not have an Updated Connectivity Matrix file available for this site or it has a " \
                f"non-standard name. File name should be xxxx_connectivity_matrix-updated.xlsx once the design is complete."

    else:
        # Build the full path to the Updated Connectivity Matrix file
        cmu_fp = os.path.join(lan_design_dir, cmu_file)

        # Get all valid rows in Updated ConnMatrix
        rows_w_data = read_cmufile_payload(cmu_fp, debug=False)
        # for r in rows_w_data:
        #     print()
        #     print(r)

        # Pop off the first row as it contains the header values which will be used as keys
        header_row = rows_w_data.pop(0)

        # print(f"header row of keys: {header_row}")

        list_of_dict =[]

        for row in rows_w_data:
            # if there is data in the New Device Name Column
            #  If cds or ds is int the new Device Name column and Port Type is True and IPAddress is not "None"
            new_dev_name = str(row[4])
            print(new_dev_name)
            if row[4] and re.search(r'c?d?s01', row[4]) and row[13] and row[15] is not None:
                print(row)
                list_of_dict.append(cat_config_utils.list_row_to_dict(header_row, row))

        if not list_of_dict:
            for row in rows_w_data:
                # if there is data in the New Device Name Column
                if row[4] and (re.search(r'ar01', row[4]) or re.search(r'sp01', row[4])) and row[13] and row[15] is not None:
                    # print(row)
                    list_of_dict.append(cat_config_utils.list_row_to_dict(header_row, row))

        print()

        summary_string += f"\n\r========================= Updated Connectivity Matrix for site {siteid} generated on {start_time.ctime()} =======\r\n"
        summary_string += f"\n\rNew Hostname                     Interface                    IP/Mask                         " \
                          f"CIDR Network      Vlan  Description         Helper(s)\r\n"

        for row in list_of_dict:
            #print(row)
            # print(f"New Subnet {row['Subnet']}/{row['Subnetmask']} on device {row['Device']}.\n\tNotes: {row['Justification']}")

            for key,value in row.items():
                if value is None:
                    row[key] = " "

            summary_string += f"\n\r{row['New_Device_Hostname']:<32}{row['Local_Port']:<25}" \
                f"{row['IP_Address']:>18}/{row['Subnet_Mask']:<18}{row['CIDR_network']:<18}" \
                f"{row['VLAN']:<6}{row['New_Description']:<20}{row['Helper_Address_csv']}"
            # if row['Helper_Address_csv']:
            #     summary_string += f"\n\r\tHelpers: {row['Helper_Address_csv']}"

            summary_string += f"\n\r"

    print(summary_string)

    fn = f"{siteid}_sdwan_report.txt"

    with open(fn, "w") as f:
        f.write(summary_string)

    return summary_string


def subnets_requested(siteid):

    # Initialize summary string
    summary_string = ''
    print(f"SiteID provided is {siteid}")

    # Get Site Region so we can build path to subnet response
    with open('nt3_sites.csv') as csvfile:
        readCSV = csv.reader(csvfile, delimiter=',')
        for row in readCSV:

            if re.search(siteid, row[2]):
                print(f"SiteID provided is {siteid} in region {row[0]} and record found is {row}")
                region = row[0]
                break

    # Start of script execution
    start_time = datetime.datetime.now()

    base_path = cat_config_utils.set_base_by_user()
    site_path = cat_config_utils.find_site_root(base_path, region, siteid)
    lan_design_dir = os.path.join(site_path, '04_Design_Engineering', 'LAN_WAN')

    #########
    #########
    ## Load New Subnet Response (NSR)
    #
    print(f"Base Path is {base_path}\nSite Path is {site_path}")

    # Look for New Subnet Response File (Expecting one consolidated file)
    nsr_file = ''
    # Look for a response file
    response_file = ''
    response_file_exists = False

    sel_path, file_list = cat_config_utils.read_files_in_dir(lan_design_dir, ".xlsx")
    for a_file in file_list:
        print(a_file)
        if re.search(r'NewSubnetRequest.xlsx', a_file) or re.search(r'NewSubnetRequest_FlexConnect.xlsx', a_file):
            nsr_file = a_file

        if re.search(r'subnets?[_|-]response', a_file):
            response_file = a_file

    if response_file:
        response_file_exists = True


    # Abort if a subnet response file cannot be found.
    if not nsr_file:
        print(f"ERROR! New Subnet Request file could not be found!\nFile List searched is:\n{file_list}")
        # sys.exit("Aborting Program Execution - New Subnet Response File not found. Note: Script is searching for "
        #          "one file with subnets- or subnets_response.")
        summary_string += f"New Subnet REQUEST file could not be found!\n\nFile List searched is:\n{file_list}" \
            f"\n\nThis means a new subnet request has not been generated for the site or the file has a non-standard name. "

    else:
        # Build the full path to the New Subnet Response file
        nsr_fp = os.path.join(lan_design_dir, nsr_file)

        # Get all valid rows in  New Subnet Response file
        rows_w_data = read_nsrequestfile_payload(nsr_fp, debug=False)

        header_row = rows_w_data.pop(0)

        # Initialize list to hold rows
        list_of_dict =[]

        for row in rows_w_data:
            if row[0]:
                # print(row)
                list_of_dict.append(cat_config_utils.list_row_to_dict(header_row, row))

        print()

        summary_string += f"======= New Subnet Requested for site {siteid} {start_time.ctime()}=======\r"

        for row in list_of_dict:
            #print(row)
            # print(f"New Subnet {row['Subnet']}/{row['Subnetmask']} on device {row['Device']}.\n\tNotes: {row['Justification']}")

            summary_string += f"\n\rNew {row['Subnet Type']} Risk Domain {row['Risk Domain']} " \
                f"Requested Size {row['Requested']} on {row['Interface']} on device {row['Device']}."

            if row['Justification']:
                summary_string += f"\n\r\tNotes: {row['Justification']}"

            summary_string += f"\n\r\tStatus: {row['Status/Notes']}"

            summary_string += f"\n\r"


        print(summary_string)

        fn = f"{siteid}_new_subnets_requested.txt"

        if response_file_exists:
            summary_string += f"\n\r**Tip**: It looks like we have a response file from IPADMIN ({response_file})!" \
                f"\n\r\t Use the Bot function /new_subnetinfo for the response details."
        else:
            summary_string += f"\n\r**Tip**: It does not look like there is a response file from IPADMIN ({response_file})!" \
                f"\n\r\t  Check again later or check the ENG 100% Board for status on the response."

        summary_string += f"\n\r"

        with open(fn, "w") as f:
            f.write(summary_string)



    return summary_string




def check_dropbox():

    '''
        Get Current working Directory
    '''

    db_root = '/home/sparkbot/Dropbox/CAT_NT/Network_Transformation_Phase3'
    cmd = 'dropbox filestatus -a'

    # Save the Starting directory so we can return to it
    starting_dir = os.getcwd()

    # print(starting_dir)

    # Change to root of DB directory
    os.chdir(db_root)
    curr_dir = os.getcwd()
    output = os.system(cmd)

    # print(curr_dir)
    # print(output)

    # Return to starting directory
    os.chdir(starting_dir)


def check_ips(siteid):

    # Start of script execution
    start_time = datetime.datetime.now()

    # Initialize variables
    summary_string = ''
    detail_string = ''
    region = False
    ewb_file = False
    ewb_file_fp = "Equipment Workbook Not Found!"
    arp_csv_file = False
    site_conflicts = False

    rows_w_data = []

    # print(f"SiteID provided is {siteid}")

    # Get Site Region so we can build path to subnet response
    with open('nt3_sites.csv') as csvfile:
        readCSV = csv.reader(csvfile, delimiter=',')
        for row in readCSV:

            if re.search(siteid, row[2]):
                # print(f"SiteID provided is {siteid} in region {row[0]} and record found is {row}")
                region = row[0]
                break

    base_path = cat_config_utils.set_base_by_user()
    site_path = cat_config_utils.find_site_root(base_path, region, siteid)

    # print(site_path
    sel_path, file_list = cat_config_utils.read_files_in_dir(site_path, ".xlsx")
    # print(sel_path)
    # print(file_list)
    for a_file in file_list:
        # print(a_file)
        if re.search(r'Workbook_NT3.xlsx', a_file):
            ewb_file = a_file

    # Start processing if Equipment Workbook was found
    if ewb_file:

        ewb_file_fp = os.path.join(site_path, ewb_file)
        # print(ewb_file_fp)

        rows_w_data = cat_config_utils.read_equipwkbk_payload(ewb_file_fp)

        # print(len(rows_w_data))
        ewb_device_listofdict = []
        for line in rows_w_data[0]:
            temp_dev_dict = {}
            # print(f"\n\t dev name {line[163]} label {line[164]}, data vlan {line[169]}, voice vlan {line[170]} new ip {line[172]} old ip {line[173]}")

            if line[163] is not None:

                if not re.search(r'-ap\d{1,3}', line[163]):
                    temp_dev_dict['name'] = line[163]
                    temp_dev_dict['label'] = line[164]
                    temp_dev_dict['new_ip'] = line[172]
                    temp_dev_dict['old_ip'] = line[173]

            if temp_dev_dict:
                ewb_device_listofdict.append(temp_dev_dict)

        # Get latest show commands directory
        show_cmd_dir = os.path.join(site_path, '00_Survey', 'show_cmds')
        # print(f"show command dir {show_cmd_dir}")

        latest_shw = cat_config_utils.get_latest_dir(show_cmd_dir)
        # print(latest_shw)

        # Get the mac-results.csv file in the directory
        sel_path, file_list = cat_config_utils.read_files_in_dir(latest_shw, ".csv")
        for a_file in file_list:
            # print(a_file)
            if re.search(r'mac-results.csv', a_file):
                arp_csv_file = a_file

        # Continue if ARP CSV file was found
        arp_lines = []
        if arp_csv_file:

            arp_csv_file_fp = os.path.join(latest_shw,arp_csv_file)

            with open(arp_csv_file_fp) as arp_info:
                arp_entries = csv.reader(arp_info)

                for line in arp_entries:
                    if len(line) > 3 and line[1]:
                        arp_lines.append(line)

            # print(arp_lines)

            # Process EWB Data Against ARP Report
            # For each line in the EWB Data
            # see if there is an ARP Entry
            msg = f"======= NEW IP Conflict Report for site {siteid} =======\n\r"
            detail_string += msg
            summary_string += msg

            for line in ewb_device_listofdict:
                # print(line)
                ip_conflict = False
                msg = ''
                dev = line['name']
                newip = str(line['new_ip']).strip()
                oldip = str(line['old_ip']).strip()

                msg = f"\n\r\n\r====Checking New device {dev} with new ip {newip} and old ip {oldip}..."

                # print(msg)
                detail_string += msg
                # summary_string += msg

                for arpline in arp_lines:
                    arp_entry_ip = arpline[1]
                    arp_entry_dev = arpline[0]
                    arp_entry_vlan = arpline[5]
                    arp_entry_time = arpline[2]
                    arp_entry_macvendor = arpline[6]

                    if newip == arp_entry_ip:

                        if re.search(newip, oldip):
                            msg = f"\n\rINFO ARP Entry Match Found but Expected since device is keeping previous IP." \
                                f"\n\r\tARP ip {arp_entry_ip} dev {arp_entry_dev} " \
                                f"vlan {arp_entry_vlan} time in table {arp_entry_time} MAC vendor {arp_entry_macvendor}"
                            # print(msg)
                            # summary_string += msg
                            detail_string += msg

                        else:
                            if not ip_conflict:
                                msg = f"\n\r\tAlert! Device IP is Changing!"
                                # summary_string += msg
                                detail_string += msg

                            msg = f"\n\rWARNING!! IP CONFLICT >> ARP ip {arp_entry_ip} dev {arp_entry_dev} " \
                                f"vlan {arp_entry_vlan} time in table {arp_entry_time} MAC vendor {arp_entry_macvendor}"
                            # print(msg)
                            # summary_string += msg
                            detail_string += msg
                            ip_conflict = True
                            site_conflicts = True

                            # If its a spare switch
                            if re.search('spare', dev) and re.search('cisco', arp_entry_macvendor, re.IGNORECASE):
                                msg = f"\n\r\tDevice {dev} looks to be a spare conflicting with an existing Cisco device" \
                                    f"which may be moving and so this may not actually be a conflict.  Please review " \
                                    f"and adjust IP for spare as needed. This situation is not uncommon."
                                detail_string += msg

                if not ip_conflict:
                    msg = f"\n\rNO IP CONFLICT for device {dev} with New IP {newip}"
                    # print(msg)
                    # summary_string += msg
                    detail_string += msg


        else:
            # No ARP File found

            # Initialize summary string
            msg = f"ERROR! ARP Report not found! \n\r\tLooking in: {latest_shw}"
            summary_string += msg
            detail_string += msg

    else:
        # No Equipment Workbook found

        # Initialize summary string
        msg = f"ERROR! Equipment Workbook file not found! \n\r\tLooking in: {ewb_file_fp}"
        summary_string += msg
        detail_string += msg


    # print("\n\n=========")
    # print(summary_string)

    if site_conflicts:

        msg = f"\n\n\r\r**WARNING SITE HAS Possible IP Conflicts!**"
        summary_string += msg
        detail_string += msg

        msg = f"\n\n\r\r**Tip!**  Some IP Conflicts are expected. It is important to review in detail. " \
            f"\n\rFor example, for sites with existing WLCs it is not uncommon to re-use the existing IPs if they " \
            f"fall within the new addressing standard.  Please review WARNING report entries carefully. "
        summary_string += msg
        detail_string += msg
    else:
        msg = f"\n\n\r\rSite does not seem to have any unexpected IP Conflicts.  Please review report for details."
        summary_string += msg
        detail_string += msg


    fn = f"{siteid}_ip_conflict_report.txt"

    # {site_id}_ip_conflict_report.txt
    summary_string += f"\n\r"
    detail_string += f"\n\r"

    with open(fn, "w") as f:
        f.write(detail_string)

    return summary_string

# def comic_strip():
#     """
#
#     :return:
#     """
#     url = "https://pnpninja-daily-comicstrips-v1.p.rapidapi.com/getComicLinks"
#
#     headers = {
#         'x-rapidapi-host': "pnpninja-daily-comicstrips-v1.p.rapidapi.com",
#         'x-rapidapi-key': "a862c6f3bemsh13a0a0ea16b0110p1ce61fjsn2fa588e94531"
#     }
#
#     response = requests.request("GET", url, headers=headers)
#
#     print(response.text)
#
#     return response


def main():

    # # rest_api_call(url, payload="", cookie="", type="GET", content_type="text/plain" ):
    # url = "https://sandboxapicdc.cisco.com/api/aaaLogin.json"
    # payload = "{\"aaaUser\": {\"attributes\": {\"name\": \"admin\", \"pwd\": \"ciscopsdt\"}}}"
    #
    # print(payload)

    #
    # c = rest_api_call(url, payload=payload, type="POST")
    # cjson = c.json()
    # print(c)
    # print(c.status_code)
    # print(cjson['imdata'][0]['aaaLogin']['attributes']['token'])

    # dotenv.load_dotenv()
    #
    # p1 = r'{"aaaUser": {"attributes": {"name": "'
    # p2 = os.getenv('APIC_USER')
    # p3 = r'", "pwd": "'
    # p4 = os.getenv('APIC_PWD')
    # p5 = r'"}}}'
    #
    # payload = p1 + p2 + p3 + p4 + p5
    # print(payload)

    # payload = '{\"aaaUser\": {\"attributes\": {\"name\": \"' + os.getenv('APIC_USER') + '\", \"pwd\": \"' + os.getenv(
    #     'APIC_PWD') + '\"}}}'
    url = "https://sandboxapicdc.cisco.com/api/aaaLogin.json"

    # payload = {
    #     "aaaUser": {
    #         "attributes": {
    #             "name": os.getenv('APIC_USER'),
    #             "pwd": os.getenv('APIC_PWD')
    #         }
    #     }
    # }

    # print(str(payload))
    #
    # c = rest_api_call(url, payload=payload, type="POST")
    # cjson = c.json()
    # print(c)
    # print(c.status_code)
    # print(cjson['imdata'][0]['aaaLogin']['attributes']['token'])

    # resp = tz()
    # print(resp)
    # print(resp.text)

    get_time("SparkBot /time EST")

# Standard call to the main() function.
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Script Description",
                                     epilog="Usage: ' python gen_access <region> <site_id> <site_type> ")

    parser.add_argument('-r', '--root', help='Optional Root Directory', action='store')
    parser.add_argument('-c','--conn_matrix_skip', help='Boolean to indicate if the ConnMatrix should be read in.'
                                                        'Default is True. To skip reading in the Conn Matrix '
                                                        'add the -c option',
                        action='store_true', default=False)

    arguments = parser.parse_args()
    # print(arguments)
    main()