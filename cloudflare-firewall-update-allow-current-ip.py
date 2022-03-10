
# standard libraries
import requests

# project specific libraries
# data file to process
import zones
# zones_list = [
# {'zoneid':'<zoneid1>',
# 'email':'<email1>',
# 'api_key':'<api_key1>'},
# {'zoneid':'<zoneid2>',
# 'email':'<email2>',
# 'api_key':'<api_key2>'}
# ]


# function to update firewall rules
def update_firewall_rules(zones_list):

    # get the current external ip address for this computer
    current_ip = requests.get('https://api.ipify.org').text
    print('My public IP address is: {}'.format(current_ip))

    for zone in zones_list:
        # get the list of firewall rules
        url = 'https://api.cloudflare.com/client/v4/zones/{}/firewall/rules'.format(zone['zoneid'])
        # set the headers for the email and the api_key
        headers = {'X-Auth-Email': zone['email'], 'X-Auth-Key': zone['api_key']}
        # get the list of firewall rules
        response = requests.get(url, headers=headers)
        # check for errors
        if response.status_code != 200:
            print('Error: {}'.format(response.json()['errors'][0]['message']))
            continue
        # get the list of firewall rules
        firewall_rules = response.json()['result']

        # find the firewall rule with the description of "allow office pcs", case insensitive
        for rule in firewall_rules:
            if rule['description'].lower() == 'allow office pcs':
                # get the id of the rule
                rule_id = rule['id']                
                # if there is wrong
                if len(rule['filter']) != 3:
                    print('Error: firewall rule {} has {} filters, expected 3'.format(rule_id, len(rule['filter'])))
                    continue
                else:
                    filter_id = rule['filter']['id']

                    # edit the first filter with a PUT to update it to allow the current ip
                    url = 'https://api.cloudflare.com/client/v4/zones/{}/filters/{}'.format(zone['zoneid'], filter_id)
                    # data = {'filter': {'expression': '(ip.src eq "{}")'.format(current_ip)}}
                    data = {  "id": "{}".format(filter_id),  "expression": "(ip.src eq {})".format(current_ip)}
                    response = requests.put(url, headers=headers, json=data)
                    # check for errors
                    if response.status_code != 200:
                        print('Error: {}'.format(response.json()['errors'][0]['message']))
                        continue
                    else:
                        print('Updated firewall rule {} for {}'.format(rule['description'], zone['domain']))
                        break
                    

# use as a module
if __name__ == '__main__':

    update_firewall_rules(zones.zones_list)

    print('Done')
