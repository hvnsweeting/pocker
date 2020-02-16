import glob
import gzip
import itertools
import json
import os
import random
import shutil
import subprocess
import tarfile
import uuid


BTRFS_PATH = "/var/bocker"


def check(directory):
    output = subprocess.check_output(
        ["btrfs", "subvolume", "list", BTRFS_PATH]
    ).decode("utf-8")
    # ID 257 gen 7 top level 5 path PATHNAME
    for line in output.splitlines():
        if line.split()[-1] == directory:
            return True
    return False


def init(directory):
    """
    Create an image from a directory
    """
    uuid = f"img_{random.randrange(42002, 42254)}"

    if os.path.isdir(directory):
        # [[ "$(bocker_check "$uuid")" == 0 ]] && bocker_run "$@"
        fullpath = os.path.join(BTRFS_PATH, uuid)
        subprocess.call(["btrfs", "subvolume", "create", fullpath])

        # cannot use shutil.copytree as it requires dst dir must not exist
        # TODO pythonize
        subprocess.call(
            ["cp", "-rf", "--reflink=auto"]
            + glob.glob(f"{directory}/*")
            + [fullpath]
        )
        print(f"Created: {uuid}")
    else:
        print(f"No directory named {directory} exists")

    return uuid


def images():
    print("IMAGE_ID\t\tSOURCE")
    for imgpath in glob.glob(f"{BTRFS_PATH}/img_*"):
        img = os.path.basename(imgpath)
        with open(os.path.join(imgpath, "img.source")) as f:
            nametag = f.read().strip()
        print(f"{img}\t\t{nametag}")


def pull(name="alpine", tag="latest"):
    """
    Download from docker hub
    Extract layers
    Delete unused files
    Create new btrfs subvolume
    """
    # TODO us tempfile.mkdtemp to replace uuid
    tmp_uuid = str(uuid.uuid4())
    path = os.path.join("/tmp", tmp_uuid)
    os.makedirs(path)

    subprocess.call(["download-frozen-image-v2", path, f"{name}:{tag}"])

    os.remove(os.path.join(path, "repositories"))

    manifest = os.path.join(path, "manifest.json")

    with open(manifest) as f:
        content = json.load(f)

    # extract all layers, in order

    for tar in itertools.chain(*[i["Layers"] for i in content]):
        tarpath = os.path.join(path, tar)
        print(f"Extracting {tarpath}")
        with gzip.GzipFile(tarpath) as gz:
            t = tarfile.TarFile(fileobj=gz)
            t.extractall(path)
        os.remove(tarpath)
        print(f"Removed {tarpath}")

    # delete config files
    for config in [i["Config"] for i in content]:
        print(config)
        os.remove(os.path.join(path, config))

    with open(os.path.join(path, "img.source"), "w") as f:
        f.write(f"{name}:{tag}\n")

    print(os.listdir(path))

    img_id = init(path)

    shutil.rmtree(path)
    return img_id


def run(image_id, command):
    img_exists = check(image_id)
    if not img_exists:
        exit(f"No image named {image_id} exists")

    container_uuid = f"ps_{random.randrange(42002, 42254)}"
    print(f"Container: {container_uuid}")
    container_exists = check(container_uuid)
    if container_exists:
        exit("UUID conflict, please retry")

    # cmd, mac

    subprocess.call(
        [
            "ip",
            "link",
            "add",
            "dev",
            f"veth0_{container_uuid}",
            "type",
            "veth",
            "peer",
            "name",
            f"veth1_{container_uuid}",
        ]
    )
    subprocess.call(
        ["ip", "link", "set", "dev", f"veth0_{container_uuid}", "up"]
    )
    subprocess.call(
        ["ip", "link", "set", f"veth0_{container_uuid}", "master", "bridge0"]
    )

    subprocess.call(["ip", "netns", "add", f"netns_{container_uuid}"])

    subprocess.call(
        [
            "ip",
            "link",
            "set",
            f"veth1_{container_uuid}",
            "netns",
            f"netns_{container_uuid}",
        ]
    )

    namespace = f"netns_{container_uuid}"
    subprocess.call(
        [
            "ip",
            "netns",
            "exec",
            namespace,
            "ip",
            "link",
            "set",
            "dev",
            "lo",
            "up",
        ]
    )
    mac = "02:42:ac:11:00:" + container_uuid[-2:]
    print(mac)

    ip = int(container_uuid[-3:])
    subprocess.call(
        [
            "ip",
            "netns",
            "exec",
            namespace,
            "ip",
            "link",
            "set",
            "dev",
            f"veth1_{container_uuid}",
            "address",
            mac,
        ]
    )
    subprocess.call(
        [
            "ip",
            "netns",
            "exec",
            namespace,
            "ip",
            "addr",
            "add",
            f"10.0.0.{ip}/24",
            "dev",
            f"veth1_{container_uuid}",
        ]
    )
    subprocess.call(
        [
            "ip",
            "netns",
            "exec",
            namespace,
            "ip",
            "link",
            "set",
            f"veth1_{container_uuid}",
            "up",
        ]
    )
    subprocess.call(
        [
            "ip",
            "netns",
            "exec",
            namespace,
            "ip",
            "route",
            "add",
            "default",
            "via",
            "10.0.0.1",
        ]
    )

    ###
    container_path = os.path.join(BTRFS_PATH, container_uuid)
    subprocess.call(
        [
            "btrfs",
            "subvolume",
            "snapshot",
            os.path.join(BTRFS_PATH, image_id),
            container_path,
        ]
    )

    with open(os.path.join(container_path, "etc/resolv.conf"), "w") as f:
        f.write("nameserver 208.67.222.222\n")
    with open(os.path.join(container_path, f"{container_uuid}.cmd"), "w") as f:
        f.write(command)

    #### cgcreate cgexec
    subprocess.call(
        ["cgcreate", "-g", f"cpu,cpuacct,memory:/{container_uuid}"]
    )
    subprocess.call(["cgset", "-r", "cpu.shares=512", container_uuid])
    subprocess.call(
        ["cgset", "-r", "memory.limit_in_bytes=512000000", container_uuid]
    )

    subprocess.call(
        [
            "cgexec",
            "-g",
            f"cpu,cpuacct,memory:{container_uuid}",
            "ip",
            "netns",
            "exec",
            namespace,
            "unshare",
            "--mount-proc",
            "-fmuip",
            "chroot",
            container_path,
            "/bin/sh",
            "-c",
            "mkdir -p /proc && /bin/mount -t proc proc /proc && free -m && cat /etc/passwd && ps xau && df -h && mount && cat /etc/os-release",
        ]
    )
    # TODO seem free -m says memory limit not work
    subprocess.call(["ip", "link", "del", "dev", f"veth0_{container_uuid}"])
    subprocess.call(["ip", "netns", "del", namespace])


def main():
    # TODO parse args
    images()
    img_id = pull()
    run(img_id, "TODO")


if __name__ == "__main__":
    main()
