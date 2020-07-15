import subprocess
from io import open
from six import iteritems

GET_COMMAND = "caget TE:NDADETF1:CAEN"
CRATES = {"hv0": "ZOOM", "hv1": "LARMOR", "hv2": "SANS2D", "hv3": "MUSR"}

from xml.etree import ElementTree as etree
import xml.dom.minidom as xd

# Set up blocks and groups element trees
groups = etree.Element('groups')
groups.set("xmlns", "http://epics.isis.rl.ac.uk/schema/groups/1.0")
groups.set("xmlns:grp", "http://epics.isis.rl.ac.uk/schema/groups/1.0")
groups.set("xmlns:xi", "http://www.w3.org/2001/XInclude")
blocks = etree.Element('blocks')
blocks.set("xmlns", "http://epics.isis.rl.ac.uk/schema/blocks/1.0")
blocks.set("xmlns:blk", "http://epics.isis.rl.ac.uk/schema/blocks/1.0")
blocks.set("xmlns:xi", "http://www.w3.org/2001/XInclude")
for (crate_hv, crate_instrument) in iteritems(CRATES):
        for boardnum in range(0,30):
            for channum in range(0,25):
                command = "{}:{}:{}:{}:status".format(GET_COMMAND, crate_hv, boardnum, channum)
                try:
                    subprocess.check_call(command)
                    # If the call returns without error a status this is a channel we wish to monitor
                    # Create the relevant groups for each block
                    group = etree.SubElement(groups, 'group', attrib={"name": "{}hv0{}{}".format(crate_instrument, boardnum, channum)})
                    for pv in ["vmon", "imon", "status", "name", "v0set", "i0set"]:
                        # Add the block to the group
                        etree.SubElement(group, 'block', attrib={"name": "{}hv0{}{}{}".format(crate_instrument, boardnum, channum, pv)})
                        # Create the block
                        block = etree.SubElement(blocks, 'block')
                        etree.SubElement(block, 'name').text = "{}hv0{}{}{}".format(crate_instrument, boardnum, channum, pv)
                        etree.SubElement(block, 'read_pv').text = "CAEN:{}:{}:{}:{}".format(crate_hv, boardnum, channum, pv)
                        etree.SubElement(block, 'local').text = "True"
                        etree.SubElement(block, 'visible').text = "False"
                        etree.SubElement(block, 'rc_enabled').text = "False"
                        etree.SubElement(block, 'rc_lowlimit').text = "0.0"
                        etree.SubElement(block, 'rc_highlimit').text = "0.0"
                        etree.SubElement(block, 'log_periodic').text = "False"
                        etree.SubElement(block, 'log_rate').text = "30"
                        if pv == "vmon":
                            deadband = "1.0" # Log any variation >= +- 1V
                        elif pv == "imon":
                            deadband = "2.0" # Log any variation >= +- 2muA
                        else:
                            deadband = "0.0" # Log any variation at all
                        etree.SubElement(block, 'log_deadband').text = deadband
                except subprocess.CalledProcessError as e:
                    # If the call returns with error there is no channel to monitor here and it is unlikely that channum continues
                    # You may want to check this manually after running this script
                    break

# Write groups to file
groupsxmldom = xd.parseString(etree.tostring(groups))
groupsxmlfile = open("groups.xml", mode="w+")
groupsxmlfile.write(groupsxmldom.toprettyxml())

# Write blocks to file
blocksxmldom = xd.parseString(etree.tostring(blocks))
blocksxmlfile = open("blocks.xml", mode="w+")
blocksxmlfile.write(blocksxmldom.toprettyxml())
