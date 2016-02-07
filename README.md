# Extinguish
Generates configuration profiles to set Sparkle-updater-enabled apps off by default. Inspired by Ben Toms [post on the Sparkle fiasco](https://macmule.com/2016/01/31/sparkle-updater-framework-http-man-in-the-middle-vulnerability/), [Nate Walck's Chef-driven version](https://github.com/natewalck/ChefExamples2016/blob/master/cookbooks/disablesparkle/recipes/default.rb), and [Greg Neagle's profiles](https://github.com/gregneagle/profiles/tree/master/autoupdate_disablers)

### Usage
Download from releases, unpack, and use it on the command line in any of these three ways:

1. `~/Downloads/Extinguish-0.2/extinguish.py /Applications/VLC.app`

By dragging the path to any affected app into the terminal window, this will generate a single profile in the root of your home folder (or whatever the current directory is you're working in) called `disable_autoupdates_VLC.app`.

2. `~/Downloads/Extinguish-0.2/extinguish.py -a com.mactrackerapp.Mactracker -a com.fluidapp.Fluid`

This will generate two separate profiles with naming like the VLC example above.

3. `~/Downloads/Extinguish-0.2/extinguish.py -g True -a com.mactrackerapp.Mactracker -a com.fluidapp.Fluid`

This will generate a single profile called `disable_all_sparkle_autoupdates.mobileconfig` containing payloads which will disable all apps specified in one shot.

#### NOTICE - **You still need to test the effectiveness of the profiles created!** In many cases, this _will not be enough_!
Please see a tool like Tim Sutton's [mcxToProfile](https://github.com/timsutton/mcxToProfile) and follow the workflow that tool provides to collect the appropriate keys for an app that does not work with Extinguish out-of-the-box, or edit the profile generated on your own.
