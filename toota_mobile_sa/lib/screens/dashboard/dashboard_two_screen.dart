import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';


class DashboardTwoScreen extends ConsumerWidget {
  const DashboardTwoScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Scaffold(
      appBar: AppBar(
        backgroundColor: Colors.white,
        elevation: 0,
        title: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: const [
            Text('Welcome Thabo', style: TextStyle(color: Colors.black, fontSize: 18, fontWeight: FontWeight.bold)),
            Text('Current Location: Sandton', style: TextStyle(color: Colors.orange, fontSize: 14)),
          ],
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.notifications, color: Colors.black),
            onPressed: () {},
          ),
        ],
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            TextField(
              decoration: InputDecoration(
                hintText: "What's your pickup location...",
                prefixIcon: const Icon(Icons.search, color: Colors.orange),
                suffixIcon: const Icon(Icons.account_circle, color: Colors.orange),
                filled: true,
                fillColor: Colors.grey[200],
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(12),
                  borderSide: BorderSide.none,
                ),
              ),
            ),
            const SizedBox(height: 20),
            const Text('Quick actions', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
            const SizedBox(height: 10),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                quickActionButton('Request trip', Icons.directions_car),
                quickActionButton('Schedule trip', Icons.schedule),
                quickActionButton('Track trip', Icons.location_on),
              ],
            ),
            const SizedBox(height: 20),
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: Colors.orange[50],
                borderRadius: BorderRadius.circular(12),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: const [
                  Text('Heading to Pickup point', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
                  SizedBox(height: 8),
                  Text('Your vehicle arrives in 30mins'),
                  SizedBox(height: 4),
                  Text('2024 FAW 3.5 Ton - NP 1245 MP'),
                  SizedBox(height: 10),
                  LinearProgressIndicator(value: 0.6, backgroundColor: Colors.white, color: Colors.orange),
                ],
              ),
            ),
            const SizedBox(height: 20),
            const Text('Recent trips', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
            const Text('No recent trips....'),
          ],
        ),
      ),
      bottomNavigationBar: BottomNavigationBar(
        items: const [
          BottomNavigationBarItem(icon: Icon(Icons.home), label: 'Home'),
          BottomNavigationBarItem(icon: Icon(Icons.map), label: 'Map'),
          BottomNavigationBarItem(icon: Icon(Icons.directions_car), label: 'Trips'),
          BottomNavigationBarItem(icon: Icon(Icons.person), label: 'Profile'),
        ],
        selectedItemColor: Colors.orange,
        unselectedItemColor: Colors.grey,
      ),
    );
  }

  Widget quickActionButton(String title, IconData icon) {
    return Column(
      children: [
        Container(
          padding: const EdgeInsets.all(12),
          decoration: BoxDecoration(
            color: Colors.orange,
            borderRadius: BorderRadius.circular(10),
          ),
          child: Icon(icon, color: Colors.white),
        ),
        const SizedBox(height: 5),
        Text(title, style: const TextStyle(fontSize: 12)),
      ],
    );
  }
}
