import subprocess
import json
import sys
import os
from datetime import datetime
#####################################################################
#renombrar segun corresponda la ubiccacion del az.cmd o si corre el azure shell cli dejarlo en "az"
AZ_PATH = r"C:\Program Files (x86)\Microsoft SDKs\Azure\CLI2\wbin\az.cmd"

# Archivos de log
TXT_LOG = "session_log.txt"
JSON_LOG = "session_log.json"

# Si no existe el JSON, creamos lista vacía
if not os.path.exists(JSON_LOG):
    with open(JSON_LOG, "w") as jf:
        json.dump([], jf, indent=4)

def log_action(subscription, rg, action, output_text, output_json):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # Log TXT
    with open(TXT_LOG, "a", encoding="utf-8") as tf:
        tf.write(f"\n{'='*50}\n[{timestamp}]\n")
        tf.write(f"Suscripción: {subscription}\nResource Group: {rg}\nAcción: {action}\n")
        tf.write("-"*50 + "\n")
        tf.write(output_text + "\n")
    # Log JSON
    with open(JSON_LOG, "r+", encoding="utf-8") as jf:
        data = json.load(jf)
        data.append({
            "timestamp": timestamp,
            "subscription": subscription,
            "resource_group": rg,
            "action": action,
            "output": output_json
        })
        jf.seek(0)
        json.dump(data, jf, indent=4)

def run_az_command(cmd_list, capture_json=True):
    print(f"\n🔹 Ejecutando: {' '.join(cmd_list)}")
    result = subprocess.run(cmd_list, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"❌ Error ejecutando: {' '.join(cmd_list)}")
        print(result.stderr)
        sys.exit(1)

    output = result.stdout.strip()

    if capture_json:
        if output.startswith("{") or output.startswith("["):
            return json.loads(output), output
        else:
            print("❌ El resultado no es JSON válido.")
            sys.exit(1)
    else:
        return output

def choose_option(items, title, enable_filter=False):
    filtered_items = items
    while True:
        print(f"\n📋 {title}\n")
        for idx, item in enumerate(filtered_items, start=1):
            print(f"[{idx}] {item}")
        if enable_filter:
            print("[F] Filtrar por texto")
        print("[0] Volver")
        print("[Q] Salir")

        choice = input("\nSelecciona una opción: ").strip()

        if choice.lower() == "q":
            print("👋 Saliendo...")
            sys.exit(0)
        if choice == "0":
            return None
        if enable_filter and choice.lower() == "f":
            text = input("🔍 Escribe texto a buscar: ").strip().lower()
            filtered_items = [i for i in items if text in i.lower()]
            if not filtered_items:
                print("❌ No se encontraron coincidencias, mostrando todo.")
                filtered_items = items
            continue
        if choice.isdigit():
            num = int(choice)
            if 1 <= num <= len(filtered_items):
                selected_item = filtered_items[num - 1]
                real_index = items.index(selected_item)
                return real_index
        print("❌ Opción inválida, intenta nuevamente.")

def main():
    print("✅ Iniciando sesión en Azure...\n")
    subprocess.run([AZ_PATH, "login"])

    while True:
        subs, _ = run_az_command([AZ_PATH, "account", "list", "--output", "json"])
        subs_display = [f"{s['name']} (ID: {s['id']})" for s in subs]
        idx = choose_option(subs_display, "Suscripciones disponibles")
        if idx is None:
            continue
        sub_id = subs[idx]["id"]
        sub_name = subs[idx]["name"]

        print(f"\n✅ Cambiando a la suscripción '{sub_name}'...\n")
        subprocess.run([AZ_PATH, "account", "set", "--subscription", sub_id])

        while True:
            rgs, _ = run_az_command([AZ_PATH, "group", "list", "--output", "json"])
            if not rgs:
                print("❌ No se encontraron Resource Groups.")
                break
            rgs_display = [rg["name"] for rg in rgs]
            idx_rg = choose_option(rgs_display, "Resource Groups disponibles", enable_filter=True)
            if idx_rg is None:
                break
            rg_name = rgs[idx_rg]["name"]

            while True:
                print(f"\n❓ ¿Qué quieres hacer con el Resource Group '{rg_name}'?\n")
                actions = [
                    "Listar Clusters AKS",
                    "Ver TODOS los recursos",
                    "Ver Máquinas Virtuales",
                    "Ver Storage Accounts",
                    "Ver App Services",
                    "Ver IPs Públicas",
                    "Ver SQL Databases",
                    "Ver Redis Caches",
                    "Ver CosmosDB Accounts"
                ]
                for idx_act, act in enumerate(actions, start=1):
                    print(f"[{idx_act}] {act}")
                print("[0] Volver")
                print("[Q] Salir")

                action_choice = input("\nSelecciona una opción: ").strip()
                if action_choice.lower() == "q":
                    print("👋 Saliendo...")
                    sys.exit(0)
                if action_choice == "0":
                    break

                if not action_choice.isdigit() or not (1 <= int(action_choice) <= len(actions)):
                    print("❌ Opción inválida, intenta nuevamente.")
                    continue

                action_idx = int(action_choice) -1
                action_name = actions[action_idx]

                cmd_map = {
                    0: [AZ_PATH, "aks", "list", "--resource-group", rg_name, "--output", "json"],
                    1: [AZ_PATH, "resource", "list", "--resource-group", rg_name, "--output", "json"],
                    2: [AZ_PATH, "vm", "list", "--resource-group", rg_name, "--output", "json"],
                    3: [AZ_PATH, "storage", "account", "list", "--resource-group", rg_name, "--output", "json"],
                    4: [AZ_PATH, "webapp", "list", "--resource-group", rg_name, "--output", "json"],
                    5: [AZ_PATH, "network", "public-ip", "list", "--resource-group", rg_name, "--output", "json"],
                    6: [AZ_PATH, "sql", "server", "list", "--resource-group", rg_name, "--output", "json"],
                    7: [AZ_PATH, "redis", "list", "--resource-group", rg_name, "--output", "json"],
                    8: [AZ_PATH, "cosmosdb", "list", "--resource-group", rg_name, "--output", "json"]
                }

                cmd = cmd_map[action_idx]
                json_data, raw_output = run_az_command(cmd)
                if isinstance(json_data, list) and len(json_data) == 0:
                    print("⚠️ No se encontraron recursos.")
                    continue

                print("\n✅ Resultado:\n")
                subprocess.run(cmd[:-1] + ["table"])

                # Log de esta acción
                log_action(sub_name, rg_name, action_name, raw_output, json_data)

                # Si fue AKS, preguntar si quiere conectarse
                if action_idx == 0:
                    aks_names = [aks["name"] for aks in json_data]
                    if not aks_names:
                        print("⚠️ No hay Clusters AKS.")
                        continue
                    aks_idx = choose_option(aks_names, "Clusters AKS disponibles")
                    if aks_idx is None:
                        continue
                    aks_name = aks_names[aks_idx]
                    confirm = input(f"\n¿Deseas conectarte a '{aks_name}' y abrir un shell kubectl? (s/n): ").strip().lower()
                    if confirm == "s":
                        subprocess.run([
                            AZ_PATH, "aks", "get-credentials",
                            "--resource-group", rg_name,
                            "--name", aks_name,
                            "--overwrite-existing",
                            "--admin"
                        ])
                        subprocess.run(["kubelogin", "convert-kubeconfig", "-l", "msi"])
                        print("\n💻 Ingresando shell interactivo (escribe 'exit' para salir)...\n")
                        subprocess.run(["cmd"])

if __name__ == "__main__":
    main()
