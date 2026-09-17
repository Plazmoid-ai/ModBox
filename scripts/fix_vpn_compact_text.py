from pathlib import Path
p = Path('app/lib/screens/settings_screen.dart')
s = p.read_text(encoding='utf-8')
old = 'Put unreachable WireGuard tunnels to sleep after they sit idle, freeing memory and saving battery. They wake instantly on use.'
new = 'Put unreachable WireGuard tunnels to sleep after they sit idle, freeing memory and saving battery. They wake instantly on use. Only affects tunnels not on the active route.'
if old not in s:
    raise SystemExit('target text not found')
p.write_text(s.replace(old, new, 1), encoding='utf-8')
