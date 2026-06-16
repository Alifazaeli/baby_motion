import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../auth/providers/auth_provider.dart';
import '../providers/settings_provider.dart';

/// FR-A7: Settings screen — child profile edit, UI language, sign out.
class SettingsScreen extends StatelessWidget {
  const SettingsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final auth = context.watch<AuthProvider>();
    final settings = context.watch<SettingsProvider>();
    final child = auth.child;
    final theme = Theme.of(context);

    return Scaffold(
      appBar: AppBar(title: const Text('Settings')),
      body: ListView(
        children: [
          if (child != null) ...[
            _SectionHeader(title: 'Child Profile'),
            ListTile(
              title: const Text('Name'),
              subtitle: Text(child.name),
              trailing: const Icon(Icons.edit),
              onTap: () => _editName(context, child.id, child.name),
            ),
            ListTile(
              title: const Text('Content language'),
              subtitle: Text(child.language == 'fa' ? 'Persian' : 'English'),
              trailing: const Icon(Icons.edit),
              onTap: () => _editContentLanguage(context, child.id, child.language),
            ),
          ],
          _SectionHeader(title: 'App Language'),
          for (final (code, label) in [('fa', 'فارسی'), ('en', 'English')])
            RadioListTile<String>(
              title: Text(label),
              value: code,
              groupValue: settings.uiLanguage,
              onChanged: (v) => v != null ? settings.setUiLanguage(v) : null,
            ),
          const Divider(),
          ListTile(
            leading: Icon(Icons.logout, color: theme.colorScheme.error),
            title: Text('Sign out', style: TextStyle(color: theme.colorScheme.error)),
            onTap: () => auth.signOut(),
          ),
        ],
      ),
    );
  }

  void _editName(BuildContext context, String childId, String current) {
    final ctrl = TextEditingController(text: current);
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text("Child's name"),
        content: TextField(controller: ctrl, autofocus: true),
        actions: [
          TextButton(onPressed: () => Navigator.pop(ctx), child: const Text('Cancel')),
          FilledButton(
            onPressed: () async {
              await context.read<SettingsProvider>().updateChild(childId, name: ctrl.text.trim());
              if (ctx.mounted) Navigator.pop(ctx);
            },
            child: const Text('Save'),
          ),
        ],
      ),
    );
  }

  void _editContentLanguage(BuildContext context, String childId, String current) {
    showDialog(
      context: context,
      builder: (ctx) => SimpleDialog(
        title: const Text('Content language'),
        children: [
          for (final (code, label) in [('fa', 'فارسی'), ('en', 'English')])
            SimpleDialogOption(
              onPressed: () async {
                await context.read<SettingsProvider>().updateChild(childId, language: code);
                if (ctx.mounted) Navigator.pop(ctx);
              },
              child: Text(label),
            ),
        ],
      ),
    );
  }
}

class _SectionHeader extends StatelessWidget {
  const _SectionHeader({required this.title});
  final String title;

  @override
  Widget build(BuildContext context) => Padding(
        padding: const EdgeInsets.fromLTRB(16, 20, 16, 4),
        child: Text(title,
            style: Theme.of(context).textTheme.labelLarge?.copyWith(
                  color: Theme.of(context).colorScheme.primary,
                )),
      );
}
