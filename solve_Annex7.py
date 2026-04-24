import csv
import math
import os
import sys
from collections import defaultdict

# File paths
BASE = 'Annex7-20260415/'
SOLAR = BASE + 'solar.csv'
BUILDINGS = BASE + 'buildings.csv'
BATTERY = BASE + 'battery.csv'
GRID = BASE + 'grid.csv'

# Policy
PENALTY_LIMIT = 30

# Read solar
solar = [0] * 97
with open(SOLAR, encoding='utf-8') as f:
    next(f)
    for line in f:
        idx, val = line.strip().split(',')
        solar[int(idx)] = float(val)

# Read grid
grid_limit = [0] * 97
co2_factor = [0] * 97
with open(GRID, encoding='utf-8') as f:
    next(f)
    for line in f:
        idx, lim, co2 = line.strip().split(',')
        grid_limit[int(idx)] = float(lim)
        co2_factor[int(idx)] = float(co2)

# Read battery
if not os.path.exists(BATTERY):
    print(f"Xato: {BATTERY} topilmadi!")
    sys.exit(1)

with open(BATTERY, encoding='utf-8') as f:
    reader = csv.DictReader(f)
    try:
        row = next(reader)
        cap = float(row['capacity'])
        max_ch = float(row['max_charge'])
        max_dch = float(row['max_discharge'])
        init_ch = float(row['initial_charge'])
        min_safe = float(row['min_safe_level'])
    except StopIteration:
        print("Xato: Battery fayli bo'sh!")
        sys.exit(1)
    except KeyError as e:
        print(f"Xato: Battery faylida ustun topilmadi: {e}")
        sys.exit(1)

# Read buildings
# For each interval, collect all loads
interval_loads = defaultdict(list)
with open(BUILDINGS, encoding='utf-8') as f:
    next(f)
    for line in f:
        b_id, b_type, interval, base, flex, priority = line.strip().split(',')
        interval = int(interval)
        interval_loads[interval].append({
            'id': b_id,
            'type': b_type,
            'base': float(base),
            'flex': float(flex),
            'priority': int(priority)
        })

stable_count = 0
battery = init_ch
for t in range(1, 97):
    # 1. Calculate total mandatory and flexible loads
    base_total = 0
    flex_LC = []  # (priority, flex_load) for L and C
    flex_MD = 0   # sum for M and D (must be fully served)
    for b in interval_loads[t]:
        base_total += b['base']
        if b['type'] in ('L', 'C'):
            if b['flex'] > 0:
                flex_LC.append((b['priority'], b['flex']))
        elif b['type'] in ('M', 'D'):
            flex_MD += b['flex']
    flex_LC.sort()  # increasing priority
    flex_total = sum(f for _, f in flex_LC) + flex_MD
    total_load = base_total + flex_total
    # 2. Use solar first
    solar_used = min(solar[t], total_load)
    remaining = total_load - solar_used
    # 3. Use battery next
    battery_used = min(remaining, max_dch, battery - min_safe if battery > min_safe else 0)
    battery_used = max(battery_used, 0)
    remaining -= battery_used
    # 4. Use grid next
    grid_used = min(remaining, grid_limit[t])
    remaining -= grid_used
    # 5. If still insufficient, curtail flexible load (L, C only, by increasing priority)
    flex_shed = 0
    if remaining > 0 and flex_LC:
        for i, (prio, flex) in enumerate(flex_LC):
            shed = min(remaining, flex)
            flex_LC[i] = (prio, flex - shed)
            flex_shed += shed
            remaining -= shed
            if remaining <= 0:
                break
    # 6. If still insufficient, check if mandatory load is unmet
    if remaining > 0:
        # Not stable
        # Update battery (charge if excess solar)
        excess_solar = solar[t] - solar_used
        battery_charge = min(excess_solar, max_ch, cap - battery)
        battery += battery_charge
        battery = min(battery, cap)
        continue
    # 7. Update battery (charge if excess solar)
    excess_solar = solar[t] - solar_used
    battery_charge = min(excess_solar, max_ch, cap - battery)
    battery += battery_charge
    battery -= battery_used
    battery = min(battery, cap)
    # 8. Check battery safe level
    if battery < min_safe:
        continue
    # 9. Penalty if grid_used > 80% grid_limit
    penalty = 0
    if grid_used > 0.8 * grid_limit[t]:
        penalty = math.ceil((grid_used * co2_factor[t]) / 3)
    if penalty > PENALTY_LIMIT:
        continue
    # 10. If all conditions met, interval is stable
    stable_count += 1
print(stable_count)
