import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';


final locationProvider = StateProvider<String>((ref) => 'Sandton');
final vehicleArrivalProvider = StateProvider<int>((ref) => 30);

class DashboardThreeScreen extends ConsumerWidget {
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final location = ref.watch(locationProvider);
    final arrivalTime = ref.watch(vehicleArrivalProvider);

    return Scaffold(
      backgroundColor: Colors.white,
      appBar: AppBar(
        elevation: 0,
        backgroundColor: Colors.white,
        title: Text('Welcome Thabo', style: TextStyle(color: Colors.black)),
        actions: [
          IconButton(
            icon: Icon(Icons.notifications_none, color: Colors.black),
            onPressed: () {},
          )
        ],
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Current Location: $location', style: TextStyle(color: Colors.orange)),
            SizedBox(height: 10),
            TextField(
              decoration: InputDecoration(
                hintText: "What's your pickup location...",
                prefixIcon: Icon(Icons.search),
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(10),
                  borderSide: BorderSide(color: Colors.grey.shade300),
                ),
              ),
            ),
            SizedBox(height: 20),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceAround,
              children: [
                QuickActionButton(icon: Icons.directions_car, label: 'Request trip'),
                QuickActionButton(icon: Icons.schedule, label: 'Schedule trip'),
                QuickActionButton(icon: Icons.track_changes, label: 'Track trip'),
              ],
            ),
            SizedBox(height: 20),
            Card(
              elevation: 2,
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
              child: Padding(
                padding: const EdgeInsets.all(12.0),
                child: Row(
                  children: [
                    Image.asset('assets/images/truck_2.png', width: 50, height: 50),
                    SizedBox(width: 10),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text('Heading to Pickup Point', style: TextStyle(fontWeight: FontWeight.bold)),
                          SizedBox(height: 5),
                          Text('Your vehicle arrives in $arrivalTime mins'),
                          Text('2024 FAW 3.5 Ton - NP 1245 MP'),
                        ],
                      ),
                    ),
                    Icon(Icons.close, color: Colors.grey),
                  ],
                ),
              ),
            ),
            SizedBox(height: 20),
            Text('Recent Trips', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
            ListTile(
              leading: Icon(Icons.location_on, color: Colors.orange),
              title: Text('15 Fox Street → 48 William Street'),
              subtitle: Text('R1000.00 · 24th Oct 24 · 21:00'),
              trailing: Icon(Icons.refresh, color: Colors.grey),
            ),
          ],
        ),
      ),
      bottomNavigationBar: BottomNavigationBar(
        selectedItemColor: Colors.orange,
        unselectedItemColor: Colors.grey,
        items: [
          BottomNavigationBarItem(icon: Icon(Icons.home), label: 'Home'),
          BottomNavigationBarItem(icon: Icon(Icons.map), label: 'Map'),
          BottomNavigationBarItem(icon: Icon(Icons.directions_car), label: 'Trips'),
          BottomNavigationBarItem(icon: Icon(Icons.person), label: 'Profile'),
        ],
      ),
    );
  }
}

class QuickActionButton extends StatelessWidget {
  final IconData icon;
  final String label;

  QuickActionButton({required this.icon, required this.label});

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        CircleAvatar(
          backgroundColor: Colors.orange.shade100,
          child: Icon(icon, color: Colors.orange),
        ),
        SizedBox(height: 5),
        Text(label, style: TextStyle(fontSize: 12)),
      ],
    );
  }
}
