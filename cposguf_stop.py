from cposguf_run import sql_connection
import pprint

con, cur = sql_connection()

cur.execute("SELECT comp_id, cpu_type, active_lattice, active_p FROM computers")
computers = {}
for i, computer in enumerate(cur.fetchall()):
    if computer[2] is not None and computer[3] is not None:
        computers[i] = computer

print("Active computers:")
pprint.pprint(computers)

output = input("Select # computer to stop (type 'all' to stop all): ")


def stop_comp(cur, comp_id):
    cur.execute(
        "UPDATE computers SET active_lattice = NULL, active_p = NULL WHERE comp_id = '{}'".format(
            comp_id
        )
    )
    print(comp_id, "will stop after the current iteration.")


if output == "all":
    for computer in computers.values():
        stop_comp(cur, computer[0])
elif int(output) in computers:
    stop_comp(cur, computers[int(output)][0])
else:
    print("Not a valid computer")

cur.close()
con.close()
