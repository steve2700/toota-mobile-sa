import 'package:flutter/material.dart';
import 'package:google_maps_flutter/google_maps_flutter.dart';
import 'package:geolocator/geolocator.dart';
import 'package:google_places_flutter/google_places_flutter.dart';

class RouteSelectionScreen extends StatefulWidget {
  const RouteSelectionScreen({super.key});

  @override
  _RouteSelectionScreenState createState() => _RouteSelectionScreenState();
}

class _RouteSelectionScreenState extends State<RouteSelectionScreen> {
  GoogleMapController? mapController;
  LatLng? currentLocation;
  String? destination;

  @override
  void initState() {
    super.initState();
    _getCurrentLocation();
  }

  Future<void> _getCurrentLocation() async {
    Position position = await Geolocator.getCurrentPosition(desiredAccuracy: LocationAccuracy.high);
    setState(() {
      currentLocation = LatLng(position.latitude, position.longitude);
    });
  }

  void _onMapCreated(GoogleMapController controller) {
    mapController = controller;
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SafeArea(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Padding(
              padding: const EdgeInsets.all(16.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  IconButton(
                    icon: Icon(Icons.arrow_back),
                    onPressed: () {},
                  ),
                  SizedBox(height: 10),
                  Text("Select your route", style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
                  SizedBox(height: 10),
                  _buildLocationInput("15 West Road South, Sandton", Icons.location_on, isCurrent: true),
                  _buildLocationInput(destination ?? "Select Destination", Icons.place),
                  SizedBox(height: 10),
                  ElevatedButton(
                    onPressed: () {},
                    child: Text("Select on map"),
                  ),
                ],
              ),
            ),
            Expanded(
              child: currentLocation == null
                  ? Center(child: CircularProgressIndicator())
                  : GoogleMap(
                      onMapCreated: _onMapCreated,
                      initialCameraPosition: CameraPosition(
                        target: currentLocation!,
                        zoom: 14.0,
                      ),
                      myLocationEnabled: true,
                    ),
            ),
            _buildResultsList(),
            _buildConfirmButton(),
          ],
        ),
      ),
    );
  }

  Widget _buildLocationInput(String text, IconData icon, {bool isCurrent = false}) {
    return Container(
      padding: EdgeInsets.symmetric(horizontal: 12, vertical: 10),
      decoration: BoxDecoration(
        color: Colors.orange.shade100,
        borderRadius: BorderRadius.circular(10),
      ),
      child: Row(
        children: [
          Icon(icon, color: Colors.orange),
          SizedBox(width: 10),
          Expanded(
            child: TextField(
              decoration: InputDecoration(
                hintText: text,
                border: InputBorder.none,
              ),
              readOnly: !isCurrent,
              onTap: () async {
                // Handle destination search
                showDialog(
                  context: context,
                  builder: (context) => AlertDialog(
                    title: Text("Select Destination"),
                    content: GooglePlaceAutoCompleteTextField(
                      textEditingController: TextEditingController(),
                      googleAPIKey: "AIzaSyBvVtzDCLzkO9LDjlwCCpBUVmW98JexLLw",
                      inputDecoration: InputDecoration(
                        hintText: "Enter destination",
                        border: OutlineInputBorder(),
                      ),
                      debounceTime: 800,
                      countries: ["za"],
                      isLatLngRequired: true,
                      getPlaceDetailWithLatLng: (prediction) {
                        setState(() {
                          destination = prediction.description;
                        });
                      },
                      itemClick: (prediction) {
                        setState(() {
                          destination = prediction.description;
                        });
                        Navigator.pop(context);
                      },
                    ),
                  ),
                );
              },
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildResultsList() {
    List<Map<String, String>> results = [
      {"name": "Sandton City Mall", "distance": "2km away"},
      {"name": "Sandton Train Station", "distance": "3km away"},
      {"name": "Sandton Hotel", "distance": "5km away"},
      {"name": "Sandton Hospital", "distance": "4km away"},
    ];

    return Padding(
      padding: const EdgeInsets.all(16.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text("Results", style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
          SizedBox(height: 10),
          Column(
            children: results.map((result) {
              return ListTile(
                title: Text(result["name"]!),
                subtitle: Text(result["distance"]!),
                trailing: Icon(Icons.bookmark_border, color: Colors.orange),
              );
            }).toList(),
          ),
        ],
      ),
    );
  }

  Widget _buildConfirmButton() {
    return Padding(
      padding: const EdgeInsets.all(16.0),
      child: ElevatedButton(
        onPressed: () {},
        style: ElevatedButton.styleFrom(
          backgroundColor: Colors.orange,
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
          minimumSize: Size(double.infinity, 50),
        ),
        child: Text("Confirm route", style: TextStyle(fontSize: 16, color: Colors.white)),
      ),
    );
  }
}
