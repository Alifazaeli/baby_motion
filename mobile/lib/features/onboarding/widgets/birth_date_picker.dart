import 'package:flutter/material.dart';

/// Year + month dropdown picker for child birth date (FR-A3).
class BirthDatePicker extends StatefulWidget {
  const BirthDatePicker({
    super.key,
    required this.initialYear,
    required this.initialMonth,
    required this.onChanged,
  });

  final int initialYear;
  final int initialMonth;
  final void Function(int year, int month) onChanged;

  @override
  State<BirthDatePicker> createState() => _BirthDatePickerState();
}

class _BirthDatePickerState extends State<BirthDatePicker> {
  late int _year;
  late int _month;

  static const _months = [
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December',
  ];

  @override
  void initState() {
    super.initState();
    _year = widget.initialYear;
    _month = widget.initialMonth;
  }

  @override
  Widget build(BuildContext context) {
    final currentYear = DateTime.now().year;
    final years = List.generate(7, (i) => currentYear - 6 + i);

    return Row(
      children: [
        Expanded(
          child: DropdownButtonFormField<int>(
            value: _year,
            decoration: const InputDecoration(labelText: 'Year', border: OutlineInputBorder()),
            items: years
                .map((y) => DropdownMenuItem(value: y, child: Text('$y')))
                .toList(),
            onChanged: (y) {
              if (y != null) {
                setState(() => _year = y);
                widget.onChanged(_year, _month);
              }
            },
          ),
        ),
        const SizedBox(width: 16),
        Expanded(
          child: DropdownButtonFormField<int>(
            value: _month,
            decoration: const InputDecoration(labelText: 'Month', border: OutlineInputBorder()),
            items: List.generate(12, (i) => i + 1)
                .map((m) => DropdownMenuItem(value: m, child: Text(_months[m - 1])))
                .toList(),
            onChanged: (m) {
              if (m != null) {
                setState(() => _month = m);
                widget.onChanged(_year, _month);
              }
            },
          ),
        ),
      ],
    );
  }
}
