import random
import sys
from typing import List


def generate_passenger_requests(n: int) -> List[str]:
    """生成电梯乘客请求数据

    Args:
        n: 要生成的请求数量

    Returns:
        生成的请求字符串列表
    """
    # 可用楼层
    floors = ['B4', 'B3', 'B2', 'B1', 'F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7']
    # 可用电梯ID
    elevator_ids = [1, 2, 3, 4, 5, 6]
    # 已使用的乘客ID，确保不重复
    used_ids = set()

    requests = []
    current_time = 0.0

    for i in range(n):
        # 如果是最后一条请求，确保时间不超过50秒
        if i == n - 1 and current_time >= 50:
            break

        # 80%概率使用短间隔(0.0-0.2秒)，20%概率使用长间隔(1.0-3.0秒)
        if random.random() < 0.8:
            time_increment = random.uniform(0.0, 0.2)
        else:
            time_increment = random.uniform(1.0, 3.0)

        # 确保加上时间增量后不超过50秒
        if current_time + time_increment > 50:
            time_increment = max(0.1, 50 - current_time)  # 至少0.1秒间隔

        current_time = round(current_time + time_increment, 1)

        # 生成唯一乘客ID
        passenger_id = random.randint(1, 999)
        while passenger_id in used_ids:
            passenger_id = random.randint(1, 999)
        used_ids.add(passenger_id)
        passenger_id_str = f"{passenger_id:d}"

        # 生成优先级(1-100)，使用beta分布来产生合理的方差
        # alpha=2, beta=5 会产生右偏分布，多数在1-50之间，少数高优先级
        priority = int(random.betavariate(2, 5) * 100) + 1
        priority = max(1, min(priority, 100))  # 确保在1-100范围内

        # 生成起点和终点，确保不同
        from_floor, to_floor = random.sample(floors, 2)

        # 生成指定的电梯ID
        elevator_id = random.choice(elevator_ids)

        # 构建请求字符串
        request = f"[{current_time}]{passenger_id_str}-PRI-{priority}-FROM-{from_floor}-TO-{to_floor}-BY-{elevator_id}"
        requests.append(request)

    return requests


def main():
    if len(sys.argv) != 2:
        print("使用方法: python data_generator.py <请求数量>")
        return

    try:
        n = int(sys.argv[1])
        if n <= 0:
            raise ValueError
    except ValueError:
        print("请输入一个正整数作为请求数量")
        return

    requests = generate_passenger_requests(n)

    # 输出所有请求，并在最后添加一个换行
    print('\n'.join(requests) + '\n', end='')


if __name__ == "__main__":
    main()