import pyrosm
from pyrosm import get_data, OSM

def main():
    fp = get_data("alberta", directory="../data")
    print(fp)

    # Initialize OSM parser
    osm = OSM(fp)
    print(type(osm))
    
    # Generate chart for drivable roads
    drive_net = osm.get_network(network_type="driving")
    drive_net.plot()
    
    # End
    return 0

if __name__ == '__main__':
    main()