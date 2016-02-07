#!/usr/bin/python
"""
Generates a sparkle disabler profile from an app bundle id, writing a mobileconfig
to wherever this script is run from. You can then sign/distribute as you see fit.

Drag-drop an app bundle as an argument, or feed it one (or more)
bundle identifiers from the CFBundleIdentifier value in an apps Info.plist.
Add the '-g or --group' option to make one big profile for all affected apps.
Optionally specify your org and/or an identifier(like a github acct).
"""
import argparse
import CoreFoundation
import os
import plistlib
import sys
import uuid


def build_payload(bundle_id, payload_id, in_uuid):
    """populates payload with bundle_id, returns array"""
    forced_dict = {"mcx_preference_settings": {"SUAutomaticallyUpdate": False,
                                               "SUEnableAutomaticChecks": False,
                                               "SUFeedURL": "https://127.0.0.1"}
                  }
    bundle_dict = {"Forced": [forced_dict]}
    content_dict = {bundle_id: bundle_dict}
    payload_dict = {"PayloadContent": content_dict,
                    "PayloadEnabled": True,
                    "PayloadIdentifier": payload_id,
                    "PayloadType": "com.apple.ManagedClient.preferences",
                    "PayloadUUID": in_uuid,
                    "PayloadVersion": 1,
                   }
    return payload_dict


def integrate_whole(payload, github_acct, org, out_uuid):
    """integrates payload into whole of profile, returns dict"""
    if type(payload) != list:
        payload = [payload]
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
    parser = argparse.ArgumentParser(add_help=True, version='0.1',
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
    options = parser.parse_args()
    #build_payload, handling one-off drag-drops first
    out_uuid = str(uuid.uuid4())
    if options.app_bundle:
        if options.app_bundle.endswith('.app'):
            try:
                infoplist_path = (options.app_bundle + '/Contents/Info.plist')
                bundle_id = CoreFoundation.CFPreferencesCopyAppValue("CFBundleIdentifier", infoplist_path)
                appname = bundle_id.split('.')[-1]
                in_uuid = str(uuid.uuid4())
                payload_id = "SparkleDisabler." + out_uuid + ".alacarte.customsettings." + in_uuid
                payload = build_payload(bundle_id, payload_id, in_uuid)
                whole = integrate_whole(payload, options.profile_id,
                                        options.org, out_uuid)
                extend_dict = {"PayloadDescription": "Custom settings to disable "
                               "sparkle updates for %s.app" % appname,
                               "PayloadDisplayName": "SparkleDisabler: %s" % bundle_id,
                               "PayloadIdentifier": options.profile_id + '.' + appname,
                              }
                whole.update(extend_dict)

                mobilecfg_path = ('').join([os.getcwd(), '/disable_autoupdates_',
                                            bundle_id.split('.')[-1], '.mobileconfig'])
                with open(mobilecfg_path, 'w') as final:
                    plistlib.writePlist(whole, final)
                sys.exit(0)
            except OSError:
                print 'Info.plist not found, exiting'
                sys.exit(1)
        else:
            print 'Not recognized as an app bundle, exiting'
            print parser.print_help()
            sys.exit(1)
    to_process = options.apps
    if not to_process:
        print parser.print_help()
        sys.exit(0)
    mobilecfg_path, whole = '', ''
    if options.group:
        mobilecfg_path = ('').join([os.getcwd(), '/disable_all_sparkle_',
                                    'autoupdates.mobileconfig'])
        payload_list = []
    for bundle_id in to_process:
        #gen uuid's for containing profile and payload
        appname = bundle_id.split('.')[-1]
        if options.group:
            in_uuid = str(uuid.uuid4())
            payload_id = ('').join(["SparkleDisabler.", out_uuid,
                                   ".alacarte.customsettings.", in_uuid])
            payload = build_payload(bundle_id, payload_id, in_uuid)
            payload_list.append(payload)
        else:
            in_uuid, out_uuid = str(uuid.uuid4()), str(uuid.uuid4())
            payload_id = ('').join(["SparkleDisabler.", out_uuid,
                               ".alacarte.customsettings.", in_uuid])
            payload = build_payload(bundle_id, payload_id, in_uuid)
            whole = integrate_whole(payload, options.profile_id,
                                    options.org, out_uuid)
            extend_dict = {"PayloadDescription": "Custom settings to disable "
                           "sparkle updates for %s.app" % appname,
                           "PayloadDisplayName": "SparkleDisabler: %s" % bundle_id,
                           "PayloadIdentifier": options.profile_id + '.' + appname,
                          }
            whole.update(extend_dict)
            mobilecfg_path = ('').join([os.getcwd(), '/disable_autoupdates_',
                                       bundle_id.split('.')[-1], '.mobileconfig'])
            with open(mobilecfg_path, 'w') as final:
                plistlib.writePlist(whole, final)
    if options.group:
        whole = integrate_whole(payload_list, options.profile_id,
                                options.org, out_uuid)
        extend_dict = {"PayloadDescription": "Custom settings to disable "
                       "all sparkle apps from updating over http",
                       "PayloadDisplayName": "ExtinguishGeneratedSparkleDisabler",
                       "PayloadIdentifier": options.profile_id
                      }
        whole.update(extend_dict)
        with open(mobilecfg_path, 'w') as final:
            plistlib.writePlist(whole, final)


if __name__ == '__main__':
    main()
