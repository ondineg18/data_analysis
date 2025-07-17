import json
from datetime import datetime
from collections import defaultdict, Counter

# path to your JSONL file
jsonl_path = "678e6eb7170e3a5da7c4ab91.jsonl"

# Aggregate across all records
all_times_by_condition = defaultdict(list)
all_change_counts_by_condition = defaultdict(Counter)

with open(jsonl_path, "r", encoding="utf-8") as f:
    for line_num, line in enumerate(f, 1):
        line = line.strip()
        if not line:
            continue

        # Parse JSON object
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            print(f"Skipping invalid JSON on line {line_num}")
            continue

        user_answer = record.get("user_answer", {})

        times_by_condition = defaultdict(list)
        change_counts_by_condition = defaultdict(Counter)

        for key in user_answer:
            if "first_choice" in key:
                # E.g. key = "7first_choiceC3"
                qnum_part, cond_part = key.split("first_choice")
                question_num = qnum_part
                condition = cond_part

                first_key = f"{question_num}first_choice{condition}"
                second_key = f"{question_num}second_choice{condition}"
                third_key = f"{question_num}third_choice{condition}"

                try:
                    # Get timestamps
                    first_time_str = user_answer[first_key][0]
                    third_time_str = user_answer[third_key][0]
                    first_time = datetime.fromisoformat(first_time_str)
                    third_time = datetime.fromisoformat(third_time_str)
                    time_spent = (third_time - first_time).total_seconds()

                    times_by_condition[condition].append(time_spent)
                    all_times_by_condition[condition].append(time_spent)

                    # Get choices
                    first_choice = user_answer[first_key][1]
                    second_choice = user_answer[second_key][1]
                    third_choice = user_answer[third_key][1]

                    # Analyze changes
                    changes = 0
                    if first_choice != second_choice:
                        changes += 1
                    if second_choice != third_choice:
                        changes += 1

                    if changes == 0:
                        change_type = "no_change"
                    elif changes == 1:
                        change_type = "one_change"
                    else:
                        change_type = "two_changes"

                    change_counts_by_condition[condition][change_type] += 1
                    all_change_counts_by_condition[condition][change_type] += 1

                except (KeyError, ValueError, IndexError):
                    continue

        # Optional: print record summary
        print(f"--- Record {line_num} ---")
        for cond, times in times_by_condition.items():
            avg_time = sum(times) / len(times) if times else 0
            change_counts = change_counts_by_condition[cond]
            print(f"  Condition {cond}: {len(times)} questions, avg time {avg_time:.2f}s")
            print(f"    Changes summary: {dict(change_counts)}")

print("\n=== Overall summary across JSONL file ===")
for cond, times in all_times_by_condition.items():
    avg_time = sum(times) / len(times) if times else 0
    change_counts = all_change_counts_by_condition[cond]
    total_questions = sum(change_counts.values())
    print(f"\nCondition {cond}:")
    print(f"  Total questions: {total_questions}")
    print(f"  Average time spent: {avg_time:.2f} seconds")
    for change_type, count in change_counts.items():
        percentage = (count / total_questions) * 100 if total_questions else 0
        print(f"    {change_type}: {count} times ({percentage:.1f}%)")