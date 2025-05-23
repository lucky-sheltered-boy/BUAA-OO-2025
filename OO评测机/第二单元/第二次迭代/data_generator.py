import random
import sys
import math
from typing import List, Tuple, Set, Dict, Optional

# --- Constants Strictly Based on HW6 Specification & New Rules ---
ALL_FLOORS = ['B4', 'B3', 'B2', 'B1', 'F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7']
SCHE_TARGET_FLOORS = ['B2', 'B1', 'F1', 'F2', 'F3', 'F4', 'F5'] # Also used for UPDATE target floor
ELEVATOR_IDS = list(range(1, 7))

MIN_TIME = 1 # Start time slightly adjusted based on example
MAX_TIME = 50.0

# Constraints from User Request:
MAX_TOTAL_SCHE_COMMANDS = 20
MIN_PASSENGER_REQUESTS = 1
MAX_PASSENGER_REQUESTS = 100
PASSENGER_ID_RANGE = (1, 1000)
MAX_PASSENGER_PRIORITY = 100
MIN_SCHE_INTERVAL_PER_ELEVATOR = 8.0 # seconds. Also applies between SCHE and UPDATE
# --- New Constraints ---
MAX_SCHE_PER_ELEVATOR = 1 # Each elevator can receive at most one SCHE command
MAX_UPDATE_COMMANDS = 3 # Maximum number of UPDATE commands allowed (as each uses 2 unique elevators)

# --- Configuration for Burst Generation ---
MIN_BURSTS = 2
MAX_BURST_DIVISOR = 4 # Higher divisor means potentially fewer bursts for the same N

# --- Timestamp Generation Functions ---

def generate_bursty_timestamps(n_commands: int) -> List[float]:
    """Generates timestamps clustered into distinct 'bursts'."""
    if n_commands == 0:
        return []
    if n_commands == 1:
        return [round(random.uniform(MIN_TIME, MAX_TIME), 1)]

    max_bursts = max(MIN_BURSTS + 1, n_commands // MAX_BURST_DIVISOR)
    max_bursts = min(max_bursts, n_commands) # Cannot have more bursts than commands
    num_bursts = random.randint(MIN_BURSTS, max_bursts)

    burst_times_set: Set[float] = set()
    attempts = 0
    max_attempts = num_bursts * 5
    while len(burst_times_set) < num_bursts and attempts < max_attempts:
        t = round(random.uniform(MIN_TIME, MAX_TIME), 1)
        # Ensure minimum separation between burst centers? Not strictly necessary.
        burst_times_set.add(t)
        attempts += 1

    # Fallback if no burst times generated (highly unlikely)
    if not burst_times_set:
         burst_times_set.add(round(random.uniform(MIN_TIME, MAX_TIME), 1))

    final_burst_times = sorted(list(burst_times_set))

    assigned_timestamps = []
    for _ in range(n_commands):
        # Assign each command to a random burst center time
        assigned_timestamps.append(random.choice(final_burst_times))

    assigned_timestamps.sort() # Crucial for processing order
    return assigned_timestamps

# --- Helper Function for Time Constraints ---

def check_time_interval(current_time: float, sche_times: List[Tuple[float, int]], update_times: List[float], interval: float) -> bool:
    """
    Checks if current_time is at least 'interval' away from all SCHE and UPDATE times.
    Args:
        current_time: The timestamp being checked.
        sche_times: List of (timestamp, elevator_id) for generated SCHE commands.
        update_times: List of timestamps for generated UPDATE commands.
        interval: The minimum required time separation (e.g., MIN_SCHE_INTERVAL_PER_ELEVATOR).
    Returns:
        True if the interval constraint is met, False otherwise.
    """
    for sche_ts, _ in sche_times:
        if abs(current_time - sche_ts) < interval:
            return False
    for update_ts in update_times:
        if abs(current_time - update_ts) < interval:
            return False
    return True

# --- Main Request Generation Logic ---

def generate_requests(n_passengers: int, n_total_sche: int, n_update: int) -> List[str]:
    """
    Generates elevator input data including PRI, SCHE, and UPDATE commands.
    Strictly follows BUAA OO HW6 specs + new rules.

    Args:
        n_passengers: Number of passenger requests (1-100).
        n_total_sche: Total number of SCHE commands attempted (0-20).
        n_update: Total number of UPDATE commands attempted (0-3).

    Returns:
        List of command strings sorted by timestamp.
    """
    # --- Input Validation ---
    if not (MIN_PASSENGER_REQUESTS <= n_passengers <= MAX_PASSENGER_REQUESTS):
        raise ValueError(f"乘客请求数量 ({n_passengers}) 必须在 {MIN_PASSENGER_REQUESTS}-{MAX_PASSENGER_REQUESTS} 之间")
    if not (0 <= n_total_sche <= MAX_TOTAL_SCHE_COMMANDS):
        raise ValueError(f"SCHE 请求总数 ({n_total_sche}) 必须在 0-{MAX_TOTAL_SCHE_COMMANDS} 之间")
    if not (0 <= n_update <= MAX_UPDATE_COMMANDS):
        raise ValueError(f"UPDATE 请求总数 ({n_update}) 必须在 0-{MAX_UPDATE_COMMANDS} 之间")

    # Clamp SCHE based on elevator availability and 1-per-elevator rule
    max_possible_sche = len(ELEVATOR_IDS) * MAX_SCHE_PER_ELEVATOR
    n_total_sche = min(n_total_sche, max_possible_sche)
    if n_total_sche < int(sys.argv[2]): # Check original requested value
         print(f"Warning: Requested {sys.argv[2]} SCHE commands, but reducing to {n_total_sche} due to 1-SCHE-per-elevator limit.", file=sys.stderr)

    # Calculate total commands
    n_total_commands = n_passengers + n_total_sche + n_update
    if n_total_commands == 0:
        return []

    # --- State Variables ---
    used_passenger_ids: Set[int] = set()
    last_sche_time_per_elevator: Dict[int, float] = {eid: -float('inf') for eid in ELEVATOR_IDS}
    sche_received_elevators: Set[int] = set() # Elevators that got a SCHE
    update_involved_elevators: Set[int] = set() # Elevators involved in an UPDATE

    generated_commands: List[Tuple[float, str]] = []
    # Store details of successfully generated special commands for constraint checking
    generated_sche_details: List[Tuple[float, int]] = [] # (timestamp, elevator_id)
    generated_update_timestamps: List[float] = []

    # --- 1. Choose Timestamp Distribution and Generate Timestamps ---
    # For simplicity, using bursty distribution for all commands together.
    # Could potentially use different distributions for different command types if needed.
    print("DEBUG: Using Bursty timestamp distribution.", file=sys.stderr)
    timestamps = generate_bursty_timestamps(n_total_commands)

    # --- 2. Pre-assign Command Type Placeholders ---
    # Determine how many of each special type we will *attempt* to place
    # Ensure we don't request more special commands than total slots available
    num_sche_to_attempt = min(n_total_sche, n_total_commands)
    remaining_slots_after_sche = n_total_commands - num_sche_to_attempt
    num_update_to_attempt = min(n_update, MAX_UPDATE_COMMANDS, remaining_slots_after_sche)
    # Ensure we don't try to generate more UPDATEs than possible (max 3)
    num_update_to_attempt = min(num_update_to_attempt, len(ELEVATOR_IDS) // 2)


    num_pri_placeholders = n_total_commands - num_sche_to_attempt - num_update_to_attempt

    print(f"DEBUG: Planning placeholders: PRI={num_pri_placeholders}, SCHE={num_sche_to_attempt}, UPDATE={num_update_to_attempt}", file=sys.stderr)

    # Create the list of placeholder types
    command_placeholders = ['PRI'] * num_pri_placeholders + \
                           ['SCHE_CANDIDATE'] * num_sche_to_attempt + \
                           ['UPDATE_CANDIDATE'] * num_update_to_attempt

    # Shuffle the placeholders to mix command types randomly across timestamps
    random.shuffle(command_placeholders)

    # --- 3. Generate Commands Iteratively (in sorted time order) ---
    sche_generated_count = 0
    update_generated_count = 0
    passengers_generated_count = 0

    for i in range(n_total_commands):
        current_time_precise = timestamps[i]
        current_time_output = current_time_precise # Keep precision for checks

        placeholder_type = command_placeholders[i]
        request_str: Optional[str] = None
        generate_as_pri = False # Flag to fallback to PRI generation

        # --- Attempt to generate SCHE if designated ---
        if placeholder_type == 'SCHE_CANDIDATE' and sche_generated_count < n_total_sche:
            sche_success = False
            # Find an elevator not used in SCHE or UPDATE yet
            available_for_sche = [
                eid for eid in ELEVATOR_IDS
                if eid not in sche_received_elevators and eid not in update_involved_elevators
            ]
            random.shuffle(available_for_sche)

            for target_elevator_id in available_for_sche:
                # Check interval against its own last SCHE time
                time_ok_self = current_time_precise >= last_sche_time_per_elevator[target_elevator_id] + MIN_SCHE_INTERVAL_PER_ELEVATOR
                # Check interval against ALL existing UPDATE commands
                time_ok_update = check_time_interval(current_time_precise, [], generated_update_timestamps, MIN_SCHE_INTERVAL_PER_ELEVATOR)

                if time_ok_self and time_ok_update:
                    speed = 0.5 # Fixed speed for SCHE as per spec? Assume 0.5
                    target_floor = random.choice(SCHE_TARGET_FLOORS)
                    request_str = f"[{current_time_output:.1f}]SCHE-{target_elevator_id}-{speed:.1f}-{target_floor}"

                    # Update state
                    last_sche_time_per_elevator[target_elevator_id] = current_time_precise
                    sche_received_elevators.add(target_elevator_id)
                    generated_sche_details.append((current_time_precise, target_elevator_id))
                    sche_generated_count += 1
                    sche_success = True
                    break # Successfully generated SCHE

            if not sche_success:
                # Fallback if no suitable elevator/time found for SCHE
                generate_as_pri = True

        # --- Attempt to generate UPDATE if designated ---
        elif placeholder_type == 'UPDATE_CANDIDATE' and update_generated_count < n_update:
            update_success = False
            # Find two distinct elevators *not* involved in any UPDATE yet
            available_for_update = [
                eid for eid in ELEVATOR_IDS if eid not in update_involved_elevators
            ]

            if len(available_for_update) >= 2:
                possible_pairs = list(itertools.combinations(available_for_update, 2))
                random.shuffle(possible_pairs)

                for e1, e2 in possible_pairs:
                    # Check time interval against ALL existing SCHE commands
                    time_ok_sche = check_time_interval(current_time_precise, generated_sche_details, [], MIN_SCHE_INTERVAL_PER_ELEVATOR)

                    if time_ok_sche:
                        target_floor = random.choice(SCHE_TARGET_FLOORS)
                        # Randomize order? Doesn't matter functionally.
                        request_str = f"[{current_time_output:.1f}]UPDATE-{e1}-{e2}-{target_floor}"

                        # Update state
                        update_involved_elevators.add(e1)
                        update_involved_elevators.add(e2)
                        generated_update_timestamps.append(current_time_precise)
                        update_generated_count += 1
                        update_success = True
                        break # Successfully generated UPDATE

            if not update_success:
                 # Fallback if couldn't find pair or time conflict for UPDATE
                generate_as_pri = True

        # --- Generate PRI if designated or as fallback ---
        else: # Placeholder was 'PRI' or a fallback occurred
             generate_as_pri = True


        if generate_as_pri:
             # Generate unique passenger ID
            passenger_id = random.randint(PASSENGER_ID_RANGE[0], PASSENGER_ID_RANGE[1])
            id_attempts = 0
            max_id_attempts = (PASSENGER_ID_RANGE[1] - PASSENGER_ID_RANGE[0] + 1)
            while passenger_id in used_passenger_ids and id_attempts < max_id_attempts:
                passenger_id = random.randint(PASSENGER_ID_RANGE[0], PASSENGER_ID_RANGE[1])
                id_attempts += 1
            if id_attempts >= max_id_attempts and passenger_id in used_passenger_ids:
                 print(f"Warning: Could not find unique passenger ID after {max_id_attempts} attempts. Re-using IDs possible.", file=sys.stderr)
                 # Still generate the request, maybe with a reused ID
                 # Or could assign a special negative ID? Sticking to spec for now.

            used_passenger_ids.add(passenger_id)
            passenger_id_str = f"{passenger_id:d}"
            priority = random.randint(1, MAX_PASSENGER_PRIORITY)
            from_floor, to_floor = random.sample(ALL_FLOORS, 2)
            request_str = f"[{current_time_output:.1f}]{passenger_id_str}-PRI-{priority}-FROM-{from_floor}-TO-{to_floor}"
            passengers_generated_count += 1


        # --- Store the generated command ---
        if request_str is not None:
            generated_commands.append((current_time_precise, request_str))
        else:
             # This case should ideally not happen with the fallback logic
             print(f"Warning: No command generated for slot {i} at time {current_time_output:.1f} (Placeholder: {placeholder_type})", file=sys.stderr)


    # --- Final Processing ---
    # Commands were generated based on pre-sorted timestamps. Re-sort for safety.
    generated_commands.sort(key=lambda x: x[0])
    final_requests = [cmd[1] for cmd in generated_commands]

    # --- Final Validation/Debug Output ---
    actual_sche_count = sum(1 for req in final_requests if req.split(']')[1].startswith('SCHE'))
    actual_update_count = sum(1 for req in final_requests if req.split(']')[1].startswith('UPDATE'))
    actual_pri_count = len(final_requests) - actual_sche_count - actual_update_count

    print(f"DEBUG: Generated {actual_pri_count} PRI requests.", file=sys.stderr)
    print(f"DEBUG: Generated {actual_sche_count} SCHE requests (Attempted placeholders: {num_sche_to_attempt}).", file=sys.stderr)
    print(f"DEBUG: Generated {actual_update_count} UPDATE requests (Attempted placeholders: {num_update_to_attempt}).", file=sys.stderr)

    # Check counts against expectations
    expected_total = n_passengers + n_total_sche + n_update # Based on initial args adjusted for limits
    # Note: actual PRI might be higher if fallbacks happened.
    # The total number of generated commands should match the length of the timestamp list.
    if len(final_requests) != n_total_commands:
       print(f"Error/Warning: Expected total {n_total_commands} command slots, generated {len(final_requests)} final commands.", file=sys.stderr)
    if actual_sche_count > max_possible_sche:
         print(f"Error: Generated {actual_sche_count} SCHE, exceeding maximum possible of {max_possible_sche}.", file=sys.stderr)
    if actual_update_count > MAX_UPDATE_COMMANDS:
         print(f"Error: Generated {actual_update_count} UPDATE, exceeding maximum possible of {MAX_UPDATE_COMMANDS}.", file=sys.stderr)

    # Final constraint check (optional but good for debugging)
    all_sche = [(float(r.split(']')[0][1:]), int(r.split('-')[1])) for r in final_requests if r.split(']')[1].startswith('SCHE')]
    all_update = [float(r.split(']')[0][1:]) for r in final_requests if r.split(']')[1].startswith('UPDATE')]
    for t_upd in all_update:
        for t_sch, _ in all_sche:
            if abs(t_upd - t_sch) < MIN_SCHE_INTERVAL_PER_ELEVATOR:
                 print(f"Error: Constraint Violation! UPDATE at {t_upd:.1f} is too close to SCHE at {t_sch:.1f}", file=sys.stderr)

    for eid in ELEVATOR_IDS:
         eid_sche_times = sorted([t for t, elevator_id in all_sche if elevator_id == eid])
         for k in range(len(eid_sche_times) - 1):
              if eid_sche_times[k+1] - eid_sche_times[k] < MIN_SCHE_INTERVAL_PER_ELEVATOR:
                  print(f"Error: Constraint Violation! SCHE commands for elevator {eid} at {eid_sche_times[k]:.1f} and {eid_sche_times[k+1]:.1f} are too close.", file=sys.stderr)


    return final_requests


# --- Need itertools for combinations in UPDATE ---
import itertools

def main():
    if len(sys.argv) != 4:
        print(f"使用方法: python {sys.argv[0]} <乘客请求数(1-100)> <SCHE请求总数(0-20)> <UPDATE请求总数(0-3)>")
        sys.exit(1)

    try:
        n_pass_str = sys.argv[1]
        n_sche_str = sys.argv[2]
        n_update_str = sys.argv[3]
        if not n_pass_str.isdigit(): raise ValueError("乘客请求数必须是一个非负整数")
        if not n_sche_str.isdigit(): raise ValueError("SCHE请求总数必须是一个非负整数")
        if not n_update_str.isdigit(): raise ValueError("UPDATE请求总数必须是一个非负整数")

        n_passengers = int(n_pass_str)
        n_total_sche = int(n_sche_str)
        n_update = int(n_update_str)

        # Validate against the specific constraints
        if not (MIN_PASSENGER_REQUESTS <= n_passengers <= MAX_PASSENGER_REQUESTS):
             raise ValueError(f"乘客请求数量 ({n_passengers}) 必须在 {MIN_PASSENGER_REQUESTS}-{MAX_PASSENGER_REQUESTS} 之间")
        if not (0 <= n_total_sche <= MAX_TOTAL_SCHE_COMMANDS):
            raise ValueError(f"SCHE 请求总数 ({n_total_sche}) 必须在 0-{MAX_TOTAL_SCHE_COMMANDS} 之间")
        if not (0 <= n_update <= MAX_UPDATE_COMMANDS):
             raise ValueError(f"UPDATE 请求总数 ({n_update}) 必须在 0-{MAX_UPDATE_COMMANDS} 之间")

        # Check if total commands > 0 (implicit unless all args are 0, but PRI min is 1)
        if n_passengers < MIN_PASSENGER_REQUESTS and n_total_sche == 0 and n_update == 0:
             raise ValueError("总指令数不能为0 (乘客请求数至少为1)")


    except ValueError as e:
        print(f"输入错误: {e}", file=sys.stderr)
        print(f"请提供乘客请求数 ({MIN_PASSENGER_REQUESTS}-{MAX_PASSENGER_REQUESTS}), SCHE请求总数 (0-{MAX_TOTAL_SCHE_COMMANDS}), UPDATE请求总数 (0-{MAX_UPDATE_COMMANDS})")
        sys.exit(1)

    try:
        # Optional Seeding
        # seed_val = n_passengers * 10000 + n_total_sche * 100 + n_update + random.randint(0, 1000)
        # random.seed(seed_val)
        # print(f"DEBUG: Using seed: {seed_val}", file=sys.stderr)

        requests = generate_requests(n_passengers, n_total_sche, n_update)
        sys.stdout.write('\n'.join(requests) + '\n')

    except ValueError as e: # Catch validation errors from generate_requests
        print(f"!!! 数据生成配置错误: {str(e)}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"!!! 生成数据时发生严重错误: {str(e)}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()