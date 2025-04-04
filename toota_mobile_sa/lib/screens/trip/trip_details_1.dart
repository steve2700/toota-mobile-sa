import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

final vehicleTypeProvider = StateProvider<String?>((ref) => null);
final bidPriceProvider = StateProvider<String>((ref) => '');
final loadDescriptionProvider = StateProvider<String>((ref) => '');


class TripDetailsScreen extends ConsumerWidget {
  const TripDetailsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final selectedVehicle = ref.watch(vehicleTypeProvider);
    final bidPrice = ref.watch(bidPriceProvider);
    final loadDescription = ref.watch(loadDescriptionProvider);

    return Scaffold(
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        elevation: 0,
        leading: IconButton(
          icon: Icon(Icons.arrow_back, color: Colors.black),
          onPressed: () {},
        ),
      ),
      body: Padding(
        padding: EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              "Trip Details",
              style: TextStyle(fontSize: 22, fontWeight: FontWeight.bold),
            ),
            SizedBox(height: 8),
            Text(
              "Provide details about your trip to help match you with the best vehicle.",
              style: TextStyle(color: Colors.black54),
            ),
            SizedBox(height: 16),
            _buildSectionTitle("Load description"),
            TextField(
              maxLines: 3,
              maxLength: 150,
              onChanged: (value) => ref.read(loadDescriptionProvider.notifier).state = value,
              decoration: _inputDecoration("Describe the items you are transporting"),
            ),
            SizedBox(height: 16),
            _buildSectionTitle("Vehicle type"),
            DropdownButtonFormField<String>(
              value: selectedVehicle,
              items: ["Truck", "Van", "Bike"].map((type) {
                return DropdownMenuItem(value: type, child: Text(type));
              }).toList(),
              onChanged: (value) => ref.read(vehicleTypeProvider.notifier).state = value,
              decoration: _inputDecoration("Select your vehicle type"),
            ),
            SizedBox(height: 16),
            _buildSectionTitle("Bid price"),
            TextField(
              keyboardType: TextInputType.number,
              onChanged: (value) => ref.read(bidPriceProvider.notifier).state = value,
              decoration: _inputDecoration("Enter your bid price", prefixIcon: Icons.attach_money),
            ),
            Spacer(),
            ElevatedButton(
              onPressed: bidPrice.isEmpty ? null : () {},
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.orange,
                disabledBackgroundColor: Colors.orange.withOpacity(0.5),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(12),
                ),
                minimumSize: Size(double.infinity, 50),
              ),
              child: Text("Find a driver", style: TextStyle(color: Colors.white, fontSize: 16)),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildSectionTitle(String title) {
    return Row(
      children: [
        Text(title, style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
        SizedBox(width: 4),
        Icon(Icons.info_outline, size: 16, color: Colors.orange),
      ],
    );
  }

  InputDecoration _inputDecoration(String hint, {IconData? prefixIcon}) {
    return InputDecoration(
      hintText: hint,
      filled: true,
      fillColor: Colors.white,
      border: OutlineInputBorder(
        borderRadius: BorderRadius.circular(8),
        borderSide: BorderSide.none,
      ),
      prefixIcon: prefixIcon != null ? Icon(prefixIcon, color: Colors.orange) : null,
    );
  }
}
