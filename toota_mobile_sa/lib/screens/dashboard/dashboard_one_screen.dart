import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
//import 'package:toota_mobile_sa/constants.dart';

class DashboardOneScreen extends ConsumerWidget {
  const DashboardOneScreen({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Scaffold(
      backgroundColor: Colors.white,
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: 0,
        selectedItemColor: Colors.orange,
        unselectedItemColor: Colors.grey,
        showUnselectedLabels: true,
        items: const [
          BottomNavigationBarItem(icon: Icon(Icons.home), label: 'Home'),
          BottomNavigationBarItem(icon: Icon(Icons.map), label: 'Map'),
          BottomNavigationBarItem(icon: Icon(Icons.directions_car), label: 'Trips'),
          BottomNavigationBarItem(icon: Icon(Icons.person), label: 'Profile'),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const SizedBox(height: 40),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                const Text(
                  'Welcome Thabo',
                  style: TextStyle(fontSize: 22, fontWeight: FontWeight.bold),
                ),
                IconButton(
                  icon: const Icon(Icons.notifications_none, color: Colors.black),
                  onPressed: () {},
                ),
              ],
            ),
            const SizedBox(height: 8),
            const Text(
              'Current Location: Sandton',
              style: TextStyle(fontSize: 14, color: Colors.grey),
            ),
            const SizedBox(height: 16),
            TextField(
            //  onTap: () {
            //     Navigator.pushReplacementNamed(
            //           context, RouteNames.dashboard);
            //   },
              decoration: InputDecoration(
                filled: true,
                fillColor: Colors.grey[200],
                hintText: "What's your pickup location?",
                prefixIcon: const Icon(Icons.search),
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(10),
                  borderSide: BorderSide.none,
                ),
              ),
            ),
            const SizedBox(height: 16),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceEvenly,
              children: const [
                QuickActionButton(label: 'Request trip', icon: Icons.directions_car),
                QuickActionButton(label: 'Schedule trip', icon: Icons.schedule),
                QuickActionButton(label: 'Track trip', icon: Icons.location_on),
              ],
            ),
            const SizedBox(height: 16),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: const [
                Text(
                  'Vehicles nearby',
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                ),
                Text(
                  'see all',
                  style: TextStyle(fontSize: 14, color: Colors.orange),
                ),
              ],
            ),
            const SizedBox(height: 12),
            Column(
              children: const [
                VehicleTile(
                  imagePath: "hilux.jpeg",
                  vehicle: 'Toyota Hilux',
                  type: 'Bakkie',
                  distance: '2km away',
                ),
                VehicleTile(
                  imagePath: "ud_kuzer.jpeg",
                  vehicle: '2024 UD Kuzer',
                  type: '3-ton truck',
                  distance: '3km away',
                ),
                VehicleTile(
                  imagePath: "faw_trubo.jpeg",
                  vehicle: '2024 FAW 3.5 Ton',
                  type: '5-ton truck',
                  distance: '5km away',
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}

class QuickActionButton extends StatelessWidget {
  final String label;
  final IconData icon;

  const QuickActionButton({required this.label, required this.icon, Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        CircleAvatar(
          backgroundColor: Colors.orange.shade100,
          child: Icon(icon, color: Colors.orange),
        ),
        const SizedBox(height: 4),
        Text(label, style: const TextStyle(fontSize: 14)),
      ],
    );
  }
}

class VehicleTile extends StatelessWidget {
  final String imagePath;
  final String vehicle;
  final String type;
  final String distance;

  const VehicleTile({
    required this.imagePath,
    required this.vehicle,
    required this.type,
    required this.distance,
    Key? key,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.symmetric(vertical: 8),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
      child: ListTile(
        leading: Image.asset(imagePath, width: 60, height: 60, fit: BoxFit.cover),
        title: Text(vehicle, style: const TextStyle(fontWeight: FontWeight.bold)),
        subtitle: Text(type, style: const TextStyle(color: Colors.orange)),
        trailing: Text(distance, style: const TextStyle(color: Colors.grey)),
      ),
    );
  }
}
