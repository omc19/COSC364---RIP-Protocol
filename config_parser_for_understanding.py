import sys

def read_config():
    break_loop = False
    #filename = input("Please input the configuration filename: ")
    filename = sys.argv[1]
    file = open(filename, "r")
    run = True
    output = []
    id = []
    input_ports = []
    output_ports = []
    container = []

    for line in file:
        data = line.replace(",", " ")
        print(line)
        if line.startswith("router-id"):
            data = data.split()
            id.append(data[0])
            for n in data[1:]:
                if 64000 > int(n) > 0:
                    id.append(n)
                else:
                    print("###  ID out of range  ###")
                    run = False

        if line.startswith("input-ports"):
            data = data.split()
            input_ports.append(data[0])
            for n in data[1:]:
                if n in input_ports:
                    print('###  This input port number is already in use: ' + str(n) + "  ###")   
                    run = False
                elif 1024 <= int(n) <= 64000:
                    input_ports.append(n)
                else:
                    print('###  Input-port out of range  ###')
                    run = False

        if line.startswith('outputs'):
            data = data.split()
            print(data)
            output_ports.append(data[0])
            for n in data[1:]:
                port = n.split('-')[0]
                cost = n.split('-')[1]
                if port in output or port in input_ports:
                    print('###  This output port number is already in use: ' + str(n) + "  ###")   
                    run = False  
                if int(cost) < 0 or int(cost) > 16:
                    print('###  The cost value is too high. The port is: ' + port + ' cost is: ' + cost + '  ###')
                elif 1024 <= int(port) <= 64000:
                    output_ports.append(n)
                    output.append(port)
                else:
                    print("###  output-port out of range  ###")
                    run = False

    if len(input_ports) - len(output_ports) != 0:
        run = False

    container.append(id)
    container.append(input_ports)
    container.append(output_ports)
    #print(container)
    if run is False:
        quit()
    else:
        return container


def get_router_id(configfile):
    routerid = int(configfile[0][1])
    return routerid


def get_input_ports(configfile):
    portlist = []

    for ports in configfile[1][1:]:
        portlist.append(int(ports))

    return portlist


def get_output_ports(configfile):
    output_dict = {}
    port_list = []
    cost_list = []
    id_list = []

    for output in configfile[2][1:]:
        output_split = output.split("-")

        port_list.append(int(output_split[0]))
        cost_list.append(int(output_split[1]))
        id_list.append(int(output_split[2]))


    output_dict["Port"] = port_list
    output_dict["Cost"] = cost_list
    output_dict["ID"] = id_list


    return output_dict
