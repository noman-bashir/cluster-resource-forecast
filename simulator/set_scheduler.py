import random
import apache_beam as beam


def _ScheduleByMachineID(row):
    row["simulated_machine"] = str(row["sample"]["info"]["machine_id"])
    return row


def _ScheduleByVMID(row):
    row["simulated_machine"] = row["sample"]["info"]["unique_id"]
    return row


def _ScheduleAtRandom(row, num_machines):
    row["simulated_machine"] = random.randint(0, num_machines)
    return row


def SetScheduler(data, configs):
    scheduler = configs.scheduler.WhichOneof("scheduler")

    if scheduler == "by_machine_id":
        scheduled_samples = data | "Scheduling by Machine ID" >> beam.Map(
            _ScheduleByMachineID
        )

    if scheduler == "by_vm_unique_id":
        scheduled_samples = data | "Scheduling by VM ID" >> beam.Map(_ScheduleByVMID)

    if scheduler == "at_random":
        if configs.scheduler.at_random.seed != None:
            random.seed(configs.scheduler.at_random.seed)
        scheduled_samples = data | "Scheduling at Random" >> beam.Map(
            _ScheduleAtRandom, configs.scheduler.at_random.num_machines,
        )

    return data
