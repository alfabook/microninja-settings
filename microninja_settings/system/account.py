#!/usr/bin/env python
# -*- coding: utf-8 -*-
# account.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# Contains the account screen backend functions

# Copyright (C) 2016 Alfabook srl
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
# rebadged with microninja
# Italian translation
# new add_user, delete_user

import os
import pam
import pwd
import time
from microninja.utils import get_user_unsudoed, run_cmd
#from kano_world.functions import has_token


class UserError(Exception):
    pass


# Needs sudo permission
def add_user():
    # Imported locally to avoid circular dependency
    #try:
    #    from kano_init.tasks.add_user import schedule_add_user
    #    schedule_add_user()
    #except ImportError:
    #    raise UserError("Unable to create the user. kano-init not found.")
    pass


# Needs sudo permission
def delete_user():

    cmd = "sudo microninja-userdel " +get_user_unsudoed()
    os.system(cmd)
    cmd = "sudo reboot"
    os.system(cmd)


def delete_users():
    minimum_id=1000
    interactive_users = []
    system_users = pwd.getpwall()

    # special usernames to exlude from the list
    exclude = ('nobody')

    for user in system_users:
        if user.pw_uid >= minimum_id and user.pw_name not in exclude:
            # This is an interactive user created by Kano
            interactive_users.append(user.pw_name)
    #cmd = "sudo microninja-usersdel " + " ".join(interactive_users)
    #os.system(cmd)
    msgTitle = _("Wait...");
    msgDescription = _("The system will reboot automatically")
    os.system("microninja-dialog title=\"" + msgTitle + "\" description=\"" + msgDescription + "\" background=/usr/share/microninja-settings/media/Graphics/ripristino-attesa.png no-taskbar&")
    time.sleep(5)
    os.system("sudo rm -rf /home/microninja")
    os.system("sudo rm -rf /usr/share/microninja-settings/config/*")
    os.system("sudo rm -rf /etc/microninja-parental-lock")
    os.system("sudo rm /etc/microninja-config")
    #removing scratch
    os.system("sudo apt-get remove rpi-chromium-mods scratch2 -y -q --force-yes")
    os.system("sudo cp /usr/share/microninja-scratch-flash/data/ori_links/Scratch.lnk /usr/share/microninja-desktop/kdesk/kdesktop/Scratch.lnk")
    os.system("sudo cp /usr/share/microninja-scratch-flash/data/ori_links/auto_scratch.desktop /usr/share/microninja-applications/auto_scratch.desktop")
    #removing minecraft
    os.system("sudo rm -rf /opt/mcpi")
    os.system("sudo rm -f /usr/bin/minecraft-pi")
    os.system("sudo cp /usr/share/microninja-minecraft/data/ori_links/auto_minecraft.desktop /usr/share/microninja-applications/auto_minecraft.desktop")
    os.system("sudo cp /usr/share/microninja-minecraft/data/ori_links/Minecraft.lnk /usr/share/microninja-desktop/kdesk/kdesktop/Minecraft.lnk")
    #restoring skel
    os.system("sudo cp -r /etc/skel /home/microninja")
    os.system("sudo chown -R microninja:microninja /home/microninja")
    os.system("sudo reboot")



# Returns True if password matches system password, else returns False
def verify_current_password(password):
    # Verify the current password in the first text box
    # Get current username
    username, e, num = run_cmd("echo $SUDO_USER")

    # Remove trailing newline character
    username = username.rstrip()

    if not pam.authenticate(username, password):
        # Could not verify password
        return False

    return True


# Successfully changed password is returns 0, else is successful
def change_password(new_password):
    user = get_user_unsudoed()
    out, e, cmdvalue = run_cmd("usermod --password $(echo {} | openssl passwd -1 -stdin) {}".format(new_password,user))
    return cmdvalue
