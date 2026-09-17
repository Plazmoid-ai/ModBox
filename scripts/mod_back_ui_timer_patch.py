from pathlib import Path


def edit(path, transform):
    p = Path(path)
    s = p.read_text(encoding='utf-8')
    out = transform(s)
    if out != s:
        p.write_text(out, encoding='utf-8')


def patch_main_activity(s):
    old_helper = '''private object ModBoxBackUiTimer {
    private val handler = android.os.Handler(android.os.Looper.getMainLooper())
    private var pending: Runnable? = null

    fun schedule(activity: android.app.Activity, delayMs: Long) {
        cancel()
        val task = Runnable { activity.finishAndRemoveTask() }
        pending = task
        handler.postDelayed(task, delayMs.coerceAtLeast(1000L))
    }

    fun cancel() {
        pending?.let(handler::removeCallbacks)
        pending = null
    }
}
'''
    new_helper = '''private object ModBoxBackUiTimer {
    private const val REQUEST_CODE = 240924
    private val handler = android.os.Handler(android.os.Looper.getMainLooper())
    private var pending: Runnable? = null

    private fun pendingIntent(context: android.content.Context): android.app.PendingIntent {
        val intent = android.content.Intent(context, ModBoxBackUiTimerReceiver::class.java)
        return android.app.PendingIntent.getBroadcast(
            context,
            REQUEST_CODE,
            intent,
            android.app.PendingIntent.FLAG_UPDATE_CURRENT or android.app.PendingIntent.FLAG_IMMUTABLE,
        )
    }

    fun schedule(activity: android.app.Activity, delayMs: Long) {
        cancel(activity)
        val delay = delayMs.coerceAtLeast(1000L)

        // Handler is the fast path while the process stays alive.
        // AlarmManager is the durable fallback: Android may suspend or kill
        // the Flutter process while the task is backgrounded.
        val task = Runnable {
            cancel(activity)
            activity.finishAndRemoveTask()
        }
        pending = task
        handler.postDelayed(task, delay)

        val alarmManager = activity.getSystemService(android.content.Context.ALARM_SERVICE)
            as android.app.AlarmManager
        alarmManager.setAndAllowWhileIdle(
            android.app.AlarmManager.ELAPSED_REALTIME_WAKEUP,
            android.os.SystemClock.elapsedRealtime() + delay,
            pendingIntent(activity),
        )
    }

    fun cancel(context: android.content.Context) {
        pending?.let(handler::removeCallbacks)
        pending = null
        val alarmManager = context.getSystemService(android.content.Context.ALARM_SERVICE)
            as android.app.AlarmManager
        alarmManager.cancel(pendingIntent(context))
    }
}

/** AlarmManager fallback for the Back-UI timer. */
class ModBoxBackUiTimerReceiver : android.content.BroadcastReceiver() {
    override fun onReceive(context: android.content.Context, intent: android.content.Intent?) {
        val activityManager = context.getSystemService(android.content.Context.ACTIVITY_SERVICE)
            as android.app.ActivityManager
        activityManager.appTasks.forEach { task ->
            runCatching { task.finishAndRemoveTask() }
        }
    }
}
'''

    if old_helper in s:
        s = s.replace(old_helper, new_helper, 1)
    elif 'private object ModBoxBackUiTimer' not in s:
        marker = 'class MainActivity'
        if marker not in s:
            raise SystemExit('MainActivity class insertion point not found')
        s = s.replace(marker, new_helper + '\n' + marker, 1)
    elif 'ModBoxBackUiTimerReceiver' not in s:
        raise SystemExit('Existing Back timer helper has an unexpected format; refusing unsafe rewrite')

    # The public cancel() API now requires a Context. Do this after helper
    # insertion so the helper's own calls (cancel(activity)) are untouched.
    s = s.replace('ModBoxBackUiTimer.cancel()\n', 'ModBoxBackUiTimer.cancel(this)\n')
    return s


def patch_manifest(s):
    if '.ModBoxBackUiTimerReceiver' in s:
        return s
    marker = '''        <receiver
            android:name=".vpn.VpnWatchdogReceiver"
            android:exported="false" />
'''
    if marker not in s:
        raise SystemExit('Manifest VpnWatchdogReceiver insertion point not found')
    receiver = '''        <!-- ModBox Back UI timer: AlarmManager fallback for background/process
             suspension. The receiver finishes this app's task directly. -->
        <receiver
            android:name=".ModBoxBackUiTimerReceiver"
            android:exported="false" />

'''
    return s.replace(marker, receiver + marker, 1)


def patch_general(s):
    if "import 'package:flutter/services.dart';" not in s:
        marker = "import 'package:flutter/material.dart';\n"
        if marker not in s:
            raise SystemExit('Flutter material import not found in general_tab.dart')
        s = s.replace(marker, marker + "import 'package:flutter/services.dart';\n", 1)
    return s


def patch_home(s):
    prefs_marker = "  static const _keepUiOnBackPrefsKey = 'keep_ui_on_back';\n"
    if '_backUiTimerPrefsKey' not in s:
        if prefs_marker not in s:
            raise SystemExit('HomeScreen Back preference marker not found')
        s = s.replace(
            prefs_marker,
            prefs_marker + "  static const _backUiTimerPrefsKey = 'keep_ui_on_back_close_after_minutes';\n",
            1,
        )

    if 'Future<void> _cancelBackUiCloseTimer() async' not in s:
        marker = '''  Future<void> _handleSystemBack() async {
'''
        if marker not in s:
            raise SystemExit('HomeScreen Back handler not found')
        helpers = '''  Future<void> _cancelBackUiCloseTimer() async {
    try {
      await const MethodChannel('com.leadaxe.lxbox/utils')
          .invokeMethod<void>('cancelBackUiClose');
    } catch (_) {}
  }

  Future<void> _scheduleBackUiCloseTimer() async {
    final prefs = await SharedPreferences.getInstance();
    final minutes = prefs.getInt(_backUiTimerPrefsKey) ?? 0;
    if (minutes <= 0) return;
    final delayMs = minutes * 60 * 1000;
    try {
      await const MethodChannel('com.leadaxe.lxbox/utils').invokeMethod<void>(
        'scheduleBackUiClose',
        {'delayMs': delayMs},
      );
    } catch (_) {}
  }

'''
        s = s.replace(marker, helpers + marker, 1)

        old = '''      try {
        await const MethodChannel('com.leadaxe.lxbox/utils')
            .invokeMethod<bool>('moveTaskToBack');
      } on PlatformException {
'''
        new = '''      try {
        await _scheduleBackUiCloseTimer();
        await const MethodChannel('com.leadaxe.lxbox/utils')
            .invokeMethod<bool>('moveTaskToBack');
      } on PlatformException {
'''
        if old not in s:
            raise SystemExit('HomeScreen moveTaskToBack block not found')
        s = s.replace(old, new, 1)

    lifecycle_marker = '''  @override
  void didChangeAppLifecycleState(AppLifecycleState state) {
    _lifecycle = state;
'''
    if 'unawaited(_cancelBackUiCloseTimer());' not in s:
        if lifecycle_marker not in s:
            raise SystemExit('HomeScreen lifecycle handler not found')
        s = s.replace(
            lifecycle_marker,
            lifecycle_marker + '    if (state == AppLifecycleState.resumed) {\n      unawaited(_cancelBackUiCloseTimer());\n    }\n',
            1,
        )
    return s


edit('app/android/app/src/main/kotlin/com/leadaxe/lxbox/MainActivity.kt', patch_main_activity)
edit('app/android/app/src/main/AndroidManifest.xml', patch_manifest)
edit('app/lib/screens/app_settings_screen/widgets/general_tab.dart', patch_general)
edit('app/lib/screens/home_screen.dart', patch_home)
