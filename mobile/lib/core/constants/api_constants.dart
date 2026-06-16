/// API base URL and endpoint paths.
class ApiConstants {
  ApiConstants._();

  static const String baseUrl = 'https://api.babymotion.app/api/v1';

  // Auth
  static const String googleAuth = '/auth/google';
  static const String refreshToken = '/auth/refresh';
  static const String logout = '/auth/logout';

  // User
  static const String me = '/me';
  static String children() => '/children';
  static String child(String id) => '/children/$id';
  static String acknowledgeAgeGroup(String id) => '/children/$id/acknowledge-age-group';

  // Content
  static const String categories = '/categories';
  static const String stories = '/stories';
  static String story(String id) => '/stories/$id';
  static String startStory(String id) => '/stories/$id/start';

  // Sessions
  static String completeSession(String id) => '/sessions/$id/complete';
  static String abandonSession(String id) => '/sessions/$id/abandon';

  // i18n
  static String i18n(String language) => '/i18n/$language';
}
