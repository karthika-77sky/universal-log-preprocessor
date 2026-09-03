from drain3 import TemplateMiner

template_miner = TemplateMiner()

logs = [
    "Connection from 192.168.1.10 failed",
    "Connection from 192.168.1.25 failed",
    "Connection from 10.0.0.5 failed",
    "User alice logged in from 192.168.1.10",
    "User bob logged in from 192.168.1.25",
    "User charlie logged in from 10.0.0.5"
]

for log in logs:
    result = template_miner.add_log_message(log)

    cluster = template_miner.drain.id_to_cluster[result["cluster_id"]]

    print("\nRAW:", log)
    print("TEMPLATE:", cluster.get_template())
    print("PARAMETERS:", result.get("parameter_list"))