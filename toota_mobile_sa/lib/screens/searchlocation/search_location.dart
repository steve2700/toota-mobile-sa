import 'package:flutter/material.dart';
import 'package:google_maps_flutter/google_maps_flutter.dart';
import 'package:geolocator/geolocator.dart';
import 'package:google_maps_flutter_platform_interface/google_maps_flutter_platform_interface.dart';



class RouteSelectionScreen extends StatefulWidget {
  const RouteSelectionScreen({super.key});

  @override
  _RouteSelectionScreenState createState() => _RouteSelectionScreenState();
}

class _RouteSelectionScreenState extends State<RouteSelectionScreen> {
  TextEditingController currentLocationController = TextEditingController();
  TextEditingController dropOffController = TextEditingController();
  bool isMapSelected = false;
  LatLng? currentLocation;
  LatLng? selectedLocation;

  Future<void> _selectOnMap(BuildContext context) async {
    final Map<String, LatLng>? result = await Navigator.push(
      context,
      MaterialPageRoute(builder: (context) => MapSelectionScreen()),
    );

    if (result != null) {
      setState(() {
        currentLocation = result['current'];
        selectedLocation = result['destination'];
        isMapSelected = true;
        currentLocationController.text = "Current Location: (${currentLocation!.latitude}, ${currentLocation!.longitude})";
        dropOffController.text = "Destination: (${selectedLocation!.latitude}, ${selectedLocation!.longitude})";
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text("Select your route")),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text("Select your route", style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
            SizedBox(height: 10),
            TextField(
              controller: currentLocationController,
              enabled: false,
              decoration: InputDecoration(
                hintText: "Fetching current location...",
                filled: true,
                fillColor: Colors.orange.shade100,
                prefixIcon: Icon(Icons.my_location, color: Colors.orange),
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(10),
                ),
              ),
            ),
            SizedBox(height: 10),
            TextField(
              controller: dropOffController,
              enabled: false,
              decoration: InputDecoration(
                hintText: "Select destination on map",
                filled: true,
                fillColor: Colors.orange.shade100,
                prefixIcon: Icon(Icons.search, color: Colors.orange),
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(10),
                ),
              ),
            ),
            SizedBox(height: 10),
            ElevatedButton(
              onPressed: () => _selectOnMap(context),
              style: ElevatedButton.styleFrom(backgroundColor: Colors.orange),
              child: Text("Select on map"),
            ),
            Spacer(),
            ElevatedButton(
              onPressed: isMapSelected ? () {} : null,
              style: ElevatedButton.styleFrom(
                backgroundColor: isMapSelected ? Colors.orange : Colors.grey,
              ),
              child: Text("Confirm route"),
            ),
          ],
        ),
      ),
    );
  }
}

class MapSelectionScreen extends StatefulWidget {
  @override
  _MapSelectionScreenState createState() => _MapSelectionScreenState();
}

class _MapSelectionScreenState extends State<MapSelectionScreen> {
  GoogleMapController? mapController;
  LatLng currentPosition = LatLng(-26.1076, 28.0567); // Sandton default location
  LatLng? selectedPosition;

  void _onMapCreated(GoogleMapController controller) {
    mapController = controller;
  }

  Future<void> _getCurrentLocation() async {
    Position position = await Geolocator.getCurrentPosition(desiredAccuracy: LocationAccuracy.high);
    setState(() {
      currentPosition = LatLng(position.latitude, position.longitude);
    });
  }

  @override
  void initState() {
    super.initState();
    _getCurrentLocation();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text("Select Location")),
      body: GoogleMap(
        onMapCreated: _onMapCreated,
        initialCameraPosition: CameraPosition(
          target: currentPosition,
          zoom: 15,
        ),
        onTap: (LatLng latLng) {
          setState(() {
            selectedPosition = latLng;
          });
        },
        markers: {
          Marker(
            markerId: MarkerId("current"),
            position: currentPosition,
            infoWindow: InfoWindow(title: "Current Location"),
          ),
          if (selectedPosition != null)
            Marker(
              markerId: MarkerId("destination"),
              position: selectedPosition!,
              infoWindow: InfoWindow(title: "Selected Destination"),
            ),
        },
      ),
      floatingActionButton: FloatingActionButton(
        backgroundColor: Colors.orange,
        child: Icon(Icons.check),
        onPressed: () {
          if (selectedPosition != null) {
            Navigator.pop(context, {
              'current': currentPosition,
              'destination': selectedPosition!,
            });
          }
        },
      ),
    );
  }
}
