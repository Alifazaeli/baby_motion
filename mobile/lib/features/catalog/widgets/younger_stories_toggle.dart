import 'package:flutter/material.dart';

/// FR-A12: Toggle to include stories from younger age groups.
class YoungerStoriesToggle extends StatelessWidget {
  const YoungerStoriesToggle({super.key, required this.value, required this.onChanged});

  final bool value;
  final void Function(bool) onChanged;

  @override
  Widget build(BuildContext context) {
    return SwitchListTile.adaptive(
      title: const Text('Show younger stories'),
      subtitle: const Text('Include stories from earlier stages'),
      value: value,
      onChanged: onChanged,
    );
  }
}
