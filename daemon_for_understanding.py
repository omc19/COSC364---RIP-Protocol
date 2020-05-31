from config_parser import *
import socket
import select
import time
import random

#TODO update every 30 seconds + or - 0.3 seconds
#TODO add flag for where the node "learnt" this information"
#outputs 3011-7-2
#discovers nodes via other routers "next-hop". If it sees a next hop that isn't in its database it will update its table to reach this node

ROUTER_ID = int
INPUT_PORTS = []
OUTPUT_PORTS = {}

infinity = 16

TIMER = 0
update = 3 #30 usually
router_unusable = 15
trash_timer = 12


def create_routing_table(id, output_dict):

    table = {}
    # add itself as a link
    

    table[id] = [None, None, False, 0, 0]
    

    for entry in range(0, len(output_dict["ID"])):
        dest_id = output_dict["ID"][entry]
        cost = output_dict["Cost"][entry]
        next_hop = dest_id
        flag = False
        TTL = 0
        trash_timer = 0 #None
        table[dest_id] = [cost, next_hop, flag, TTL, trash_timer]

    return table

#### table = {"Dest_id": [cost, next_hop, flag, TTL, trash_timer]}


def print_routing_table(table):

    print(">> Router {} Routing Table".format(ROUTER_ID))
    print("||Dest||Cost||Next Hop||Flag ||TTL ||Trash_Timer||")
    print("||----||----||--------||-----||----||-----------||")
    for x, y in sorted(table.items()):
        if y[0] == None:
            print("||--{}-||{}||--{}--||{}||{}||----{}---||".format(x, y[0], y[1], y[2], y[3], y[4]))
        else:
            
            print("||--{}-||--{}-||----{}---||{}||-{:2.0f}-||------{}----||".format(x, y[0], y[1], y[2], y[3], y[4]))


def update_table(table, neighbours, src_router, entries):
    """Adding new entries to a routing table"""
    table_id = []

    for key in table:
        table_id.append(key)
        
    if entries != None:

        new_entries = entries[1:-1]
        print(new_entries)
        for i in new_entries:

            print(i)
            listed_entry = i.split(',') #turn the entry back into list form
            destination = i.split('[')
            dest = int(destination[0].strip()) #single router id of directly attached # next hop id of the entry
            f = i.split(',')
            flag = f[2].strip()


            if flag == 'False':
                flag = False
            elif flag == 'True':
                flag = True
            #For adding new entires
            if dest not in table_id:
                before_cost = listed_entry[0].split('[')
                cost = int(before_cost[1])
                next_hop = int(src_router)
                previous_cost = table[next_hop][0]
                total_cost = cost + previous_cost
                flag = False
                TTL = 0
                trash = 0
                if trash == '0':
                    trash = 0
                #### table = {"Dest_id": [cost, next_hop, flag, TTL, trash_timer]}
                table[dest] = [total_cost, next_hop, flag, TTL, trash]  # [cost,



            #Updating existing entries
            #table[r_id][0] != None for if the entry is the router-id. can't compare none to int
            elif dest in table_id and table[dest][0] != None: #and table[int(src_router)][0] != None # Check to see if there is a bette r cost Also can't get better than None value. Sometimes hears itself..
                

                table[dest][3] = 0
                table[dest][4] = 0

                before_cost = listed_entry[0].split('[')
                cost = int(before_cost[1]) # cost of entry
                next_hop = int(src_router)
                origin_cost = table[next_hop][0]   
                total_cost = cost + origin_cost     # cost of entry + cost to get to originating router
                table_cost = table[dest][0]
                if total_cost < table_cost:
                    table[dest][0] = total_cost
                    table[dest][1] = next_hop
                    difference = table_cost - total_cost
                    for key, value in table.items():
                        next_link_cost = value[0] #e.g 7 
                        table_hop = value[1] # next hop for e a sepcific entry in the routing table
                        if dest in neighbours and table_hop != None and dest == table_hop:#if is neighbour cost and nexthop (e.g. 5) has changed. Has any entry with that destination (e.g. 3) as its next hop. If so change the next hop to the 5
                            table[key][0] = next_link_cost - difference 
                            table[key][1] = next_hop
    
    
    print_routing_table(table)
    return table
    


def input_sockets():
    """creates sockets and binds one socket to each input port"""

    sockets = []
    for port in INPUT_PORTS:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #create
        sock.bind(("", port))
        sockets.append(sock)
        
    print("Bound ports " + str(INPUT_PORTS) + '\n')
    return sockets




def format_message(routing_table): #format a message to be sent UDP

    output = ""
    output_ports = OUTPUT_PORTS['Port']
    command = 2
    version = 2
    router_id = ROUTER_ID
    
    header = str(command) + ',' + str(version) + ',' + str(router_id)
    output += header + " |"
    
    poison_output = ""
        
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # create socket to send out of
    for port in output_ports:
        index = output_ports.index(port)
        
        neighbour_port = OUTPUT_PORTS['ID'][index] # the neighbour port being sent
        for key, value in routing_table.items():
            dest = key
            first_hop = value[1]
            change_back = value[0]
            if dest == first_hop and neighbour_port == dest:
                value[0] = 16
                
            poison_output += str(dest) + " " + str(value) + "| "
            value[0] = change_back

        output_bytes = (header + ' |' + poison_output).encode('utf-8')
        poison_output = ""
            
        sock.sendto(output_bytes, ("127.0.0.1", int(port)))    
        

         
def readable_data(data):
    """From the recieved data make it more readable for the user"""
    data = data.replace('b','')

    data = data.split('|')
    print(data)

    head = data[0].split(',') #header of the packet
    router = head[2]

    entries = data[1:]

    return head, entries

    
def receiver(table, sockets):
    route_table = table
    
    read, write, exception = select.select(sockets,[],[], 3) #input array must be socket [0]
    if read != []:
        data, server = read[0].recvfrom(1024)
        print('Data received')
        header, entries = readable_data(str(data))
        # after this need to update table because differnec trouters come online at different times
        return header[2], entries
    else:
        return None, None
        

def periodic_update(previous):
    ## If it is greater than 30 an update is needed
    if time.time() - previous >= update:
        return True
    else:
        False

def update_timers(table, time):

    for key in sorted(table.keys()):
        if table[key] == table[ROUTER_ID]:
            print('')
        else:
            if table[key][2]:
                table[key][4] += time
                if table[key][4] > trash_timer:
                    del table[key]

            else:
                table[key][3] += time
                if table[key][3] > router_unusable:
                    table[key][0] = 16
                    table[key][2] = True
                    print('############ should be 16##################')
                    print_routing_table(table)

                    for router in first_hop(key, table):
                        table[router][0] = 16


def first_hop(frouter, table):

    routers = []
    for router in sorted(table.keys()):
        if table[router][1] == frouter:
            routers.append(router)
    return routers


def main():
    global ROUTER_ID 
    global INPUT_PORTS
    global OUTPUT_PORTS
    
    ####  ####
    startup_time = time.time()
    
    configfile = read_config()
    
    ### Create global variables ###
    ROUTER_ID = get_router_id(configfile)
    INPUT_PORTS = get_input_ports(configfile)
    OUTPUT_PORTS = get_output_ports(configfile)
    
    print("Router ID: " + str(ROUTER_ID) + '\n')
    print("Input ports: " + str(INPUT_PORTS) + '\n')
    print("Output ports: " + str(OUTPUT_PORTS) + '\n')
    
    ### Create sockets ###
    sockets = input_sockets()
    
    print(sockets)
    print("")
  
    ##### Create routing table ###########
    routing_table = create_routing_table(ROUTER_ID, OUTPUT_PORTS)
    print(routing_table)
    print('above')
    print("")
    print_routing_table(routing_table)    
    
    ### Neighbour list for the router ###
    neighbour_list = OUTPUT_PORTS['ID']
    
    ### Create packet to send on start up ###
    
    
    counter = 0
    
    last_update = startup_time

    time1 = time.time()
    time2 = 0
    
    ##### Loop #####
    while 1:
        
         #Time of last update
        
        header, entries = receiver(routing_table, sockets)
        print('Header')
        print(header)

        
        routing_table = update_table(routing_table, neighbour_list, header, entries)

        time2 = time.time() - time1
        time1 = time.time()
        update_timers(routing_table, time2)
        
        ## Sending ##
        
        #Check if it a periodic update is needed
        
        update_required = periodic_update(last_update)
        
        if update_required == True: #then update neighbours with a message
            format_message(routing_table)
            last_update = time.time() + random.randint(-1,5)
            update_required = False
            
        

    
    
main()

