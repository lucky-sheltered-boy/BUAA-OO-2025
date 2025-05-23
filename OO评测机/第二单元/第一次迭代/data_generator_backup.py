import random
import sys
from typing import List, Dict


def generate_passenger_requests(n: int) -> List[str]:
    """生成电梯乘客请求数据

    Args:
        n: 要生成的请求数量(1-60)

    Returns:
        生成的请求字符串列表
    """
    # 参数校验
    if not 1 <= n <= 60:
        raise ValueError("请求数量必须在1-60之间")

    # 可用楼层
    floors = ['B4', 'B3', 'B2', 'B1', 'F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7']
    # 可用电梯ID - 只使用1、2号电梯
    elevator_ids = [1, 2]
    # 已使用的乘客ID，确保不重复
    used_ids = set()
    # 记录每个电梯的请求计数
    elevator_counts: Dict[int, int] = {eid: 0 for eid in elevator_ids}

    requests = []
    # 第一组输入时间：50%几率48s，50%几率49s
    first_group_time = 48.0 if random.random() < 0.5 else 49.0
    # 时间范围：从first_group_time到50.0秒
    min_time = first_group_time
    max_time = 50.0
    # 平均分配时间间隔
    time_increment = (max_time - min_time) / max(1, n-1)

    for i in range(n):
        # 计算当前时间
        current_time = min_time + i * time_increment
        current_time = round(current_time, 1)

        # 生成唯一乘客ID
        passenger_id = random.randint(1, 999)
        while passenger_id in used_ids:
            passenger_id = random.randint(1, 999)
        used_ids.add(passenger_id)
        passenger_id_str = f"{passenger_id:d}"

        # 生成优先级(1-100)，使用beta分布来产生合理的方差
        priority = int(random.betavariate(2, 5) * 100) + 1
        priority = max(1, min(priority, 100))  # 确保在1-100范围内

        # 生成起点和终点，确保不同
        from_floor, to_floor = random.sample(floors, 2)

        # 生成指定的电梯ID，确保不超过30条/电梯
        available_elevators = [eid for eid in elevator_ids if elevator_counts[eid] < 30]
        if not available_elevators:
            raise RuntimeError("无法分配电梯，所有电梯都已达到30条请求上限")
        elevator_id = random.choice(available_elevators)
        elevator_counts[elevator_id] += 1

        # 构建请求字符串
        request = f"[{current_time}]{passenger_id_str}-PRI-{priority}-FROM-{from_floor}-TO-{to_floor}-BY-{elevator_id}"
        requests.append(request)

    return requests


def main():
    if len(sys.argv) != 2:
        print("使用方法: python data_generator.py <请求数量(1-60)>")
        return

    try:
        n = int(sys.argv[1])
        if not 1 <= n <= 60:
            raise ValueError
    except ValueError:
        print("请输入一个1-60之间的正整数作为请求数量")
        return

    try:
        requests = generate_passenger_requests(n)
        # 输出所有请求，并在最后添加一个换行
        print('\n'.join(requests) + '\n', end='')
    except Exception as e:
        print(f"生成数据时出错: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()