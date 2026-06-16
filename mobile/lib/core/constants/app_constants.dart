/// App-wide constants.
class AppConstants {
  AppConstants._();

  static const String appName = 'BabyMotion';
  static const int splashDurationMs = 2000;

  static const List<String> supportedLanguages = ['fa', 'en'];
  static const String defaultLanguage = 'fa';

  static const List<String> ageGroups = ['12_18m', '18_30m', '30_42m', '42_60m'];

  /// Days before next age group at which we show the transition hint (FR-A13).
  static const int upcomingTransitionDays = 30;
}
