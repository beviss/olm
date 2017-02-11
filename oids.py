# possible values ->
# http://www.monfox.com/dsnmp/mibs/IANAifType-MIB.html#type.IANAifType
ifTypeOid =        "1.3.6.1.2.1.2.2.1.3"
ifOperStatusOid =  "1.3.6.1.2.1.2.2.1.8"  # 2 when up, 1 when down
ifAdminStatusOid = "1.3.6.1.2.1.2.2.1.7"
ifNameOid =        "1.3.6.1.2.1.31.1.1.1.1"
ifDescrOid =       "1.3.6.1.2.1.31.1.1.1.18"
ifPhysAddress =    '1.3.6.1.2.1.2.2.1.6'

# returns a set of objects, where the suffixes of OIDs are learned mac addresses
# and the (integer) values are indexes of the interfaces on which the mac
# address has been learned
macAddrPortMappings = ".1.3.6.1.2.1.17.4.3.1.2"

# RFC 2674 - VLANS
# Q-BRIDGE-MIB RFC 4363

dot1qVlanCurrentEgressPorts = '.1.3.6.1.2.1.17.7.1.4.2.1.4'
dot1qVlanCurrentUntaggedPorts = '.1.3.6.1.2.1.17.7.1.4.2.1.5'
dot1qVlanStaticName = '.1.3.6.1.2.1.17.7.1.4.3.1.1'
# returns dot1qTpFdbTable.<vlan_tag>.<mac_address> = interface ifIndex
dot1qTpFdbPort = '.1.3.6.1.2.1.17.7.1.2.2.1.2'
# returns dot1qTpFdbTable.<vlan_tag>.<mac_address> = status??
dot1qTpFdbStatus = '.1.3.6.1.2.1.17.7.1.2.2.1.3'


dot1qVlanFdbId = '.1.3.6.1.2.1.17.7.1.4.2.1.3.0'

dot1dBasePortIfIndex = '.1.3.6.1.2.1.17.1.4.1.2'

##############
# JUNIPER
##############

# <internal_port_id> below is not ifIndex, nor internal ID, but dot1dBasePortIfIndex
# those ids relate to logical "units 0", not physical ports

# returns (..).<internal_vlan_id> = <vlan_name>
jnxExVlanName = ".1.3.6.1.4.1.2636.3.40.1.5.1.5.1.2"

# returns: (..).<internal_vlan_id> = <vlan_tag>
jnxExVlanTag = ".1.3.6.1.4.1.2636.3.40.1.5.1.5.1.5"

# returns: (..).<internal_vlan_id>.<internal_port_id> = {
# 1 autoActive: The port is part of the VLAN because the switch has automatically added the port
# 2 allowed: The port has been configured to be part of the VLAN, and is allowed to be part of the VLAN, if the port meets all other requirements
# 3 allowedActive: The port has been configured to be part of the VLAN, and is allowed to be part of the VLAN, if the port meets all other requirements. However, unlike the case of allowed ports, this port has a device that is participating in the VLAN associated with the port
# 4 allowedNotAvail: The port is active on some other VLAN, and is not available currently. This value applies to devices that do not allow a port to be part of more than one VLAN at the same time
# 5 notAssociated: The port is part of a port group that is not associated
# with the VLAN }
jnxExVlanPortStatus = ""

# returns (..).<internal_vlan_id>.<internal_port_id> = { 1 (tagged), 2
# (untagged) }
jnxExVlanPortTagness = ""

# returns: (..).<internal_vlan_id>.<internal_port_id> = { 1 (access), 2
# (trunk) }
jnxExVlanPortAccessMode = ""

###############
# BROCADE
###############
brcdIp = ".1.3.6.1.4.1.1991"

# works on ICX, doesnt work on MLX
snVLanByPortTable = ".1.3.6.1.4.1.1991.1.1.3.2.1"
snVLanByPortVLanId = ".1.3.6.1.4.1.1991.1.1.3.2.1.1.2"
snVLanByPortVLanName = ".1.3.6.1.4.1.1991.1.1.3.2.1.1.25"

# works on all brocade devices
snVLanByPortCfgVLanId = ".1.3.6.1.4.1.1991.1.1.3.2.7.1.1"
snVLanByPortCfgVLanName = ".1.3.6.1.4.1.1991.1.1.3.2.7.1.21"
snVLanByPortMemberTable = ".1.3.6.1.4.1.1991.1.1.3.2.6"
snVLanByPortMemberTagMode = ".1.3.6.1.4.1.1991.1.1.3.2.6.1.4"

# MPLS
# LDP Label Switching Router ID in HEX STRING
mplsLdpLsrId = '1.3.6.1.2.1.10.166.4.1.1.1.0'

# VPLS
vplsConfigName = '.1.3.6.1.4.1.1991.3.4.1.1.2.1.2'  # name of the VPLS
vplsStatusPeerCount = '.1.3.6.1.4.1.1991.3.4.1.1.3.1.2'  # peer count for the VPLS

# ID of the VPLS (~VLAN tag)
fdryVplsVcId = '.1.3.6.1.4.1.1991.1.2.15.2.2.2.1.4'
# egress ports. retunrs <internal VPLS ID>.<VPLS ID>.1.0.<IfIndex>.{1 -
# tagged 2 - untagged}
fdryVplsEndPoint2VlanTagMode = '.1.3.6.1.4.1.1991.1.2.15.2.2.3.1.5'

# pwStdMIB - Pseudowire MIB
# last oid part -> pseudowire "internal" id, value -> VPLS ID
pwID = '.1.3.6.1.4.1.1991.3.1.2.1.2.1.12'
# last oid part -> pseudowire "internal" id, value -> peer address in hex
# string format
pwPeerAddr = '.1.3.6.1.4.1.1991.3.1.2.1.2.1.9'

# MAC-TABLE
# returns all macs in mac table - the value is interface ifIndex. See
# dot1qTpFdbTable for mac-to-vlan mappings
dot1dTpFdbPort = ".1.3.6.1.2.1.17.4.3.1.2"

sysDescr = ".1.3.6.1.2.1.1.1"

# TRAPEZE WIFI (JUNIPER WLC)
wlanApName = ".1.3.6.1.4.1.14525.4.5.1.1.3.1.8"
wlanApLocation = ".1.3.6.1.4.1.14525.4.14.1.2.1.11"
wlanApSerial = ".1.3.6.1.4.1.14525.4.14.1.2.1.4"
wlanApModel = ".1.3.6.1.4.1.14525.4.14.1.2.1.5"
wlanApIp = ".1.3.6.1.4.1.14525.4.5.1.1.3.1.10"
wlanApUsers = ".1.3.6.1.4.1.14525.4.5.1.1.3.1.16"
wlanApNum = ".1.3.6.1.4.1.14525.4.5.1.1.3.1.19"
wlanApService = ".1.3.6.1.4.1.14525.4.5.1.1.6.1.5"

# OPTICAL LEVELS (DOM)

# http://www.oidview.com/mibs/2636/JUNIPER-DOM-MIB.html
jnxDomMib = "1.3.6.1.4.1.2636.3.60.1"
# index -> interface id (same as ifNameOid)
jnxDomCurrentRxLaserPower = "1.3.6.1.4.1.2636.3.60.1.1.1.1.5"

# BROCADE NetIron
snIfOpticalMonitoringInfoTable = "1.3.6.1.4.1.1991.1.1.3.3.6"
snIfOpticalMonitoringRxPower = "1.3.6.1.4.1.1991.1.1.3.3.6.1.3"

# BGP

jnxBgpM2 = "1.3.6.1.4.1.2636.5.1.1"
