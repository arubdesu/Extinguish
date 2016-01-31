#!/usr/bin/python
"""
Generates a sparkle disabler profile from an app bundle id, writing a mobileconfig
to wherever this script is run from.

Drag-drop an app bundle as an argument, or feed it one (or more)
bundle identifiers from the CFBundleIdentifier value in an apps Info.plist.

Optionally specify your org and/or github acct, and it'll spit out profiles you can distribute.
"""
import argparse
import CoreFoundation
import os
import plistlib
import sys
import uuid


def build_payload(bundle_id, payload_id, in_uuid):
    """populates payload with bundle_id, returns array"""
    once_dict = {"mcx_preference_settings": {"SUAutomaticallyUpdate": False,
                                             "SUEnableAutomaticChecks": False}
                }
    bundle_dict = {"Set-Once": [once_dict]}
    content_dict = {bundle_id: bundle_dict}
    payload_dict = {"PayloadContent": content_dict,
                    "PayloadEnabled": True,
                    "PayloadIdentifier": payload_id,
                    "PayloadType": "com.apple.ManagedClient.preferences",
                    "PayloadUUID": in_uuid,
                    "PayloadVersion": 1,
                   }
    content_array = [payload_dict]
    return content_array


def integrate_whole(payload, bundle_id, github_acct, org, out_uuid):
    """integrates payload into whole of profile, returns dict"""
    appname = bundle_id.split('.')[-1]
    finished_profile = {"PayloadContent": payload,
                        "PayloadDescription": "Custom settings to disable sparkle updates "
                                              "for %s.app" % appname,
                        "PayloadDisplayName": "SparkleDisabler: %s" % bundle_id,
                        "PayloadIdentifier": github_acct + '.' + appname,
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
                        #default=['com.github.GitHub'],
                        help='One or more app bundle ids to create profiles for',
                       )
    parser.add_argument('-g', type=str, dest='github_acct',
                        default="com.github.arubdesu.extinguish",
                        help='Used as identifier for payload id, '
                             'uses "com.github.arubdesu.extinguish" by default',
                       )
    parser.add_argument('-o', type=str, dest='org',
                        default="",
                        help='Sets organization in profile, empty by default',
                       )
    options = parser.parse_args()
    #build_payload
    if options.app_bundle:
        if options.app_bundle.endswith('.app'):
            try:
                infoplist_path = (options.app_bundle + '/Contents/Info.plist')
                bundle_id = CoreFoundation.CFPreferencesCopyAppValue("CFBundleIdentifier", infoplist_path)
                in_uuid, out_uuid = str(uuid.uuid4()), str(uuid.uuid4())
                payload_id = "SparkleDisabler." + out_uuid + ".alacarte.customsettings." + in_uuid
                payload = build_payload(bundle_id, payload_id, in_uuid)
                whole = integrate_whole(payload, bundle_id, options.github_acct,
                                        options.org, out_uuid)
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
    for bundle_id in to_process:
        #gen uuid's for containing profile and payload
        in_uuid, out_uuid = str(uuid.uuid4()), str(uuid.uuid4())
        payload_id = "SparkleDisabler." + out_uuid + ".alacarte.customsettings." + in_uuid
        payload = build_payload(bundle_id, payload_id, in_uuid)
        whole = integrate_whole(payload, bundle_id, options.github_acct,
                                options.org, out_uuid)
        mobilecfg_path = ('').join([os.getcwd(), '/disable_autoupdates_',
                                   bundle_id.split('.')[-1], '.mobileconfig'])
        with open(mobilecfg_path, 'w') as final:
            plistlib.writePlist(whole, final)


if __name__ == '__main__':
    main()
