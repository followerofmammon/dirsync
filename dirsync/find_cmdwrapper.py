import subprocess


def find_files(rootpath, max_depth=None, file_extentions=None):
    command = _get_base_command(rootpath)
    if max_depth is not None:
        command.extend(["-maxdepth", str(max_depth)])
    if file_extentions is not None:
        command.append("-regex")
        addition = ".*." + "\|.*.".join(file_extentions)
        command.append(addition)
    command += ["-type", "f"]
    return _get_command_output(command)


def find_dirs(rootpath, max_depth):
    command = _get_base_command(rootpath)
    if max_depth is not None:
        command.extend(["-maxdepth", str(max_depth)])
    command += ["-type", "d"]
    return _get_command_output(command)


def _get_base_command(rootpath):
    return ["find", rootpath]

def _get_command_output(command):
    print ' '.join(command)
    output = subprocess.check_output(command)
    return output.splitlines()
