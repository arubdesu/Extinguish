#!/usr/bin/python3

# Copyright 2016 Allister Banks
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


"""
Generates a sparkle disabler profile from an app bundle id, writing a mobileconfig
to wherever this script is run from. You can then sign/distribute as you see fit.

Drag-drop an app bundle as an argument, or feed it one (or more)
bundle identifiers from the CFBundleIdentifier value in an apps Info.plist.
Add the '-g or --group' option to make one big profile for all affected apps.
Optionally specify your org and/or an identifier(like a github acct).
"""
import argparse
import os
import plistlib
import sys
import uuid
import CoreFoundation

def build_payload(bundle_id):
    """populates payload with bundle_id, returns array"""
    forced_dict = {"mcx_preference_settings": {"SUAutomaticallyUpdate": False,
                                               "SUEnableAutomaticChecks": False,
                                               "SUFeedURL": "https://127.0.0.1"}
                  }
    bundle_dict = {"Forced": [forced_dict]}
    content_dict = {bundle_id: bundle_dict}
    return content_dict


def integrate_whole(payload, org, out_uuid, group):
    """integrates payload into whole of profile, returns dict"""
    if group:
        in_uuid = str(uuid.uuid4())
        nested = {"PayloadContent": payload,
                  "PayloadEnabled": True,
                  "PayloadIdentifier": 'SparkleDisabler',
                  "PayloadType": "com.apple.ManagedClient.preferences",
                  "PayloadUUID": in_uuid,
                  "PayloadVersion": 1,
                  }
        payload = [nested]
    finished_profile = {"PayloadContent": payload,
                        "PayloadOrganization": org,
                        "PayloadRemovalDisallowed": True,
                        "PayloadScope": "System",
                        "PayloadType": "Configuration",
                        "PayloadUUID": out_uuid,
                        "PayloadVersion": 1,
                       }
    return finished_profile


def main():
    """gimme some main"""
    parser = argparse.ArgumentParser(add_help=True,
                                     description='Either drag-drop the path to '
                                     'an app bundle into the terminal window, '
                                     'or use "-a" and the CFBundleIdentifier value from an app.')
    parser.add_argument('app_bundle', type=str, help='Path to app bundle'
                        ' to make a profile for', nargs='?')
    parser.add_argument('-a', '--apps', action='append',
                        help='One or more app bundle ids to create profiles for',
                       )
    parser.add_argument('-g', '--group', type=bool, dest='group',
                        default=False,
                        help='Generates one mobileconfig for all apps specified',
                       )
    parser.add_argument('-o', type=str, dest='org',
                        default="",
                        help='Sets organization in profile, empty by default',
                       )
    parser.add_argument('-p', '--profile_id', type=str, dest='profile_id',
                        default="com.github.arubdesu.extinguish",
                        help='Used as identifier for payload id in reverse-domain format. '
                             'Uses "com.github.arubdesu.extinguish" by default',
                       )
    parser.add_argument('-v', '--version', action='version', version='0.2')
    options = parser.parse_args()
    #build_payload, handling one-off drag-drops first
    out_uuid = str(uuid.uuid4())
    group = False
    if options.app_bundle:
        if options.app_bundle.endswith('.app'):
            try:
                infoplist_path = options.app_bundle + '/Contents/Info.plist'
                bundle_id = CoreFoundation.CFPreferencesCopyAppValue("CFBundleIdentifier", infoplist_path)
                appname = bundle_id.split('.')[-1]
                in_uuid = str(uuid.uuid4())
                payload_id = "SparkleDisabler." + out_uuid + ".alacarte.customsettings." + in_uuid
                payload = build_payload(bundle_id)
                payload_dict = {"PayloadContent": payload,
                                "PayloadEnabled": True,
                                "PayloadIdentifier": payload_id,
                                "PayloadType": "com.apple.ManagedClient.preferences",
                                "PayloadUUID": in_uuid,
                                "PayloadVersion": 1,
                               }
                inside_dict = [payload_dict]
                whole = integrate_whole(inside_dict, options.org, out_uuid, group)
                extend_dict = {"PayloadDescription": "Custom settings to disable "
                               f"sparkle updates for {appname}.app",
                               "PayloadDisplayName": f"SparkleDisabler: {bundle_id}",
                               "PayloadIdentifier": options.profile_id + '.' + appname,
                              }
                whole.update(extend_dict)
                mobilecfg_path = ''.join([os.getcwd(), '/disable_autoupdates_',
                                            bundle_id.split('.')[-1], '.mobileconfig'])
                with open(mobilecfg_path, 'wb') as final:
                    plistlib.dump(whole, final)
                sys.exit(0)
            except OSError:
                print('Info.plist not found, exiting')
                sys.exit(1)
        else:
            print('Not recognized as an app bundle, exiting')
            print(parser.print_help())
            sys.exit(1)
    to_process = options.apps
    if not to_process:
        print(parser.print_help())
        sys.exit(0)
    payload_list = {}
    for bundle_id in to_process:
        #gen uuid's for containing profile and payload
        appname = bundle_id.split('.')[-1]
        payload = build_payload(bundle_id)
        if not options.group:
            in_uuid, out_uuid = str(uuid.uuid4()), str(uuid.uuid4())
            payload_id = ''.join(["SparkleDisabler.", out_uuid,
                               ".alacarte.customsettings.", in_uuid])
            payload_dict = {"PayloadContent": payload,
                            "PayloadEnabled": True,
                            "PayloadIdentifier": payload_id,
                            "PayloadType": "com.apple.ManagedClient.preferences",
                            "PayloadUUID": in_uuid,
                            "PayloadVersion": 1,
                           }
            inside_dict = [payload_dict]
            whole = integrate_whole(inside_dict, options.org, out_uuid, group)
            extend_dict = {"PayloadDescription": "Custom settings to disable "
                           f"sparkle updates for {appname}.app" % appname,
                           "PayloadDisplayName": f"SparkleDisabler: {bundle_id}",
                           "PayloadIdentifier": options.profile_id + '.' + appname,
                          }
            whole.update(extend_dict)
            mobilecfg_path = ''.join([os.getcwd(), '/disable_autoupdates_',
                                       bundle_id.split('.')[-1], '.mobileconfig'])
            with open(mobilecfg_path, 'wb') as final:
                plistlib.dump(whole, final)

        else:
            payload_list[bundle_id] = payload[bundle_id]
    if options.group:
        group = True
        mobilecfg_path = ''.join([os.getcwd(), '/disable_all_sparkle_',
                            'autoupdates.mobileconfig'])
        out_uuid = str(uuid.uuid4())
        payload_id = ''.join(["SparkleDisabler.", out_uuid,
                               ".alacarte.customsettings"])

        whole = integrate_whole(payload_list, options.org, out_uuid, group)
        extend_dict = {"PayloadDescription": "Custom settings to disable "
                       "all sparkle apps from updating over http",
                       "PayloadDisplayName": "ExtinguishGeneratedSparkleDisabler",
                       "PayloadIdentifier": payload_id
                      }
        whole.update(extend_dict)
        with open(mobilecfg_path, 'wb') as final:
            plistlib.dump(whole, final)


if __name__ == '__main__':
    main()
