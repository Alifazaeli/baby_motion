import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../auth/providers/auth_provider.dart';
import '../providers/onboarding_provider.dart';
import '../widgets/age_group_preview.dart';
import '../widgets/birth_date_picker.dart';

/// FR-A3: 3-step onboarding (name → birth date → language).
class OnboardingScreen extends StatelessWidget {
  const OnboardingScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final ob = context.watch<OnboardingProvider>();

    return Scaffold(
      appBar: AppBar(
        leading: ob.step > 0
            ? IconButton(
                icon: const Icon(Icons.arrow_back),
                onPressed: () => context.read<OnboardingProvider>().previousStep(),
              )
            : null,
        title: Text('${ob.step + 1} / 3'),
      ),
      body: SafeArea(
        child: AnimatedSwitcher(
          duration: const Duration(milliseconds: 300),
          child: switch (ob.step) {
            0 => _NameStep(key: const ValueKey(0)),
            1 => _BirthDateStep(key: const ValueKey(1)),
            2 => _LanguageStep(key: const ValueKey(2)),
            _ => const SizedBox.shrink(),
          },
        ),
      ),
    );
  }
}

class _NameStep extends StatefulWidget {
  const _NameStep({super.key});
  @override
  State<_NameStep> createState() => _NameStepState();
}

class _NameStepState extends State<_NameStep> {
  late final TextEditingController _ctrl;

  @override
  void initState() {
    super.initState();
    _ctrl = TextEditingController(text: context.read<OnboardingProvider>().childName);
  }

  @override
  void dispose() {
    _ctrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(32),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Text("What's your child's name?", style: Theme.of(context).textTheme.headlineMedium),
          const SizedBox(height: 32),
          TextField(
            controller: _ctrl,
            autofocus: true,
            decoration: const InputDecoration(
              hintText: 'Child\'s name',
              border: OutlineInputBorder(),
            ),
            onChanged: (v) => context.read<OnboardingProvider>().setName(v),
          ),
          const Spacer(),
          FilledButton(
            onPressed: _ctrl.text.trim().isEmpty
                ? null
                : () => context.read<OnboardingProvider>().nextStep(),
            child: const Text('Continue'),
          ),
        ],
      ),
    );
  }
}

class _BirthDateStep extends StatelessWidget {
  const _BirthDateStep({super.key});

  @override
  Widget build(BuildContext context) {
    final ob = context.watch<OnboardingProvider>();
    return Padding(
      padding: const EdgeInsets.all(32),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Text("When was ${ob.childName} born?", style: Theme.of(context).textTheme.headlineMedium),
          const SizedBox(height: 32),
          BirthDatePicker(
            initialYear: ob.birthYear,
            initialMonth: ob.birthMonth,
            onChanged: (year, month) => context.read<OnboardingProvider>().setBirthDate(year, month),
          ),
          const SizedBox(height: 24),
          AgeGroupPreview(birthYear: ob.birthYear, birthMonth: ob.birthMonth),
          const Spacer(),
          FilledButton(
            onPressed: () => context.read<OnboardingProvider>().nextStep(),
            child: const Text('Continue'),
          ),
        ],
      ),
    );
  }
}

class _LanguageStep extends StatelessWidget {
  const _LanguageStep({super.key});

  @override
  Widget build(BuildContext context) {
    final ob = context.watch<OnboardingProvider>();
    return Padding(
      padding: const EdgeInsets.all(32),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Text('Choose content language', style: Theme.of(context).textTheme.headlineMedium),
          const SizedBox(height: 32),
          for (final (code, label) in [('fa', 'فارسی'), ('en', 'English')])
            Padding(
              padding: const EdgeInsets.only(bottom: 12),
              child: OutlinedButton(
                style: OutlinedButton.styleFrom(
                  side: BorderSide(
                    width: 2,
                    color: ob.language == code
                        ? Theme.of(context).colorScheme.primary
                        : Theme.of(context).colorScheme.outline,
                  ),
                ),
                onPressed: () => context.read<OnboardingProvider>().setLanguage(code),
                child: Text(label, style: const TextStyle(fontSize: 18)),
              ),
            ),
          const Spacer(),
          if (ob.error != null)
            Text(ob.error!, style: TextStyle(color: Theme.of(context).colorScheme.error)),
          FilledButton(
            onPressed: ob.isLoading ? null : () => _submit(context),
            child: ob.isLoading
                ? const CircularProgressIndicator()
                : const Text('Get started'),
          ),
        ],
      ),
    );
  }

  Future<void> _submit(BuildContext context) async {
    final child = await context.read<OnboardingProvider>().submit();
    if (child != null && context.mounted) {
      context.read<AuthProvider>().setChild(child);
    }
  }
}
