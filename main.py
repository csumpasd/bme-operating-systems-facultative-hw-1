import copy

rr_time_slice = 2


class Task:
    def __init__(self, name, priority, start, length):
        self.name = name
        self.priority = priority
        self.start = start
        self.length = length
        self.wait_time = 0
        self.run_time = 0


# read in everything
tasks = []
while True:
    try:
        data = input().split(",")
        task = Task(data[0], int(data[1]), int(data[2]), int(data[3]))
        tasks.append(task)

    except EOFError:
        break
    except IndexError:
        break

# sort them by name beforehand so ones that would go into the same spot in the queue are already in the right order
original = copy.copy(tasks)
original.sort(key=lambda x: x.start)
tasks.sort(key=lambda x: x.name)


time = 0
rr_ready = []
srtf_ready = []
current = None
result = ""


def insert_rr(task_rr):
    rr_ready.append(task_rr)


def round_robin():
    global rr_ready
    global srtf_ready
    global current
    global result

    if current is None:
        current = rr_ready.pop(0)
        result += current.name

    elif current.priority == 0:
        insert_srtf(current)
        current = rr_ready.pop(0)
        result += current.name

    # tick waiting times of all others
    for waiting in rr_ready:
        waiting.wait_time += 1
    for waiting in srtf_ready:
        waiting.wait_time += 1

    # tick current as well
    current.run_time += 1  # run task for 1 frame (to keep track of the time left from the slice)
    current.length -= 1  # and actually subtract 1 from remaining

    if current.run_time % rr_time_slice == 0 and current.length != 0 and not len(rr_ready) == 0:
        insert_rr(current)
        current = None

    elif current.length == 0:
        current = None


def insert_srtf(task_srtf):

    if len(srtf_ready) != 0:
        found = False
        for compared in srtf_ready:
            if task_srtf.length < compared.length:  # only less because this way the name ordering remains intact
                srtf_ready.insert(srtf_ready.index(compared), task_srtf)
                found = True
                break
        if not found:
            srtf_ready.append(task_srtf)
    else:
        srtf_ready.append(task_srtf)


def shortest_remaining_time_first():
    global rr_ready
    global srtf_ready
    global current
    global result

    if current is None:
        current = srtf_ready.pop(0)
        result += current.name

    else:
        i = 0
        while len(srtf_ready) > 0 and i < len(srtf_ready):
            if srtf_ready[i].start == time-1 and srtf_ready[i].length < current.length:
                insert_srtf(current)
                current = srtf_ready[i]
                srtf_ready.remove(current)
                result += current.name
            else:
                i += 1

    for waiting in rr_ready:
        waiting.wait_time += 1
    for waiting in srtf_ready:
        waiting.wait_time += 1

    current.run_time += 1
    current.length -= 1

    if current.length == 0:
        current = None


while len(tasks) > 0 or len(rr_ready) > 0 or len(srtf_ready) > 0 or current is not None:

    if len(rr_ready) > 0 or (current is not None and current.priority == 1):
        round_robin()
    elif len(srtf_ready) > 0 or (current is not None and current.priority == 0):
        shortest_remaining_time_first()

    # add all tasks that are ready to run in the current tick to the queues of each scheduler
    i = 0
    while len(tasks) > 0 and i < len(tasks):
        if tasks[i].start == time:
            if tasks[i].priority == 1:
                insert_rr(tasks[i])
                tasks.remove(tasks[i])
            elif tasks[i].priority == 0:
                insert_srtf(tasks[i])
                tasks.remove(tasks[i])
        else:
            i += 1

    time += 1


waiting_times = ""
for task in original:
    waiting_times += task.name + ":" + str(task.wait_time)
    if original.index(task) != len(original)-1:
        waiting_times += ","

print(result)
print(waiting_times)

